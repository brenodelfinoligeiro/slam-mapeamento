"""Gate puro de autonomia; tempos ROS inteiros em nanossegundos."""

import math


SEGUNDO = 1_000_000_000


class ProtecaoAutonomia:
    """Máquina determinística; não depende de rclpy nem executa serviços.

    Cada método de entrada recebe ROS em ns e monotônico em segundos.
    O adaptador encaminha somente ``True`` de receber_comando, nunca a partir
    do timer. As intenções de serviço são confirmadas por número de sequência.
    """

    def __init__(self, prazo_sensores=.5, prazo_tf=.5, prazo_comando=.3,
                 tolerancia_futuro=.05, tolerancia_tf_futuro=.25):
        valores = (prazo_sensores, prazo_tf, prazo_comando,
                   tolerancia_futuro, tolerancia_tf_futuro)
        if any(type(v) not in (int, float) or not math.isfinite(v) or v < 0
               for v in valores) or any(v <= 0 for v in valores[:3]):
            raise ValueError('Prazos e tolerâncias devem ser finitos e válidos')
        self.prazo_sensores = prazo_sensores
        self.prazo_tf = prazo_tf
        self.prazo_comando = prazo_comando
        self.futuro_ns = round(tolerancia_futuro * SEGUNDO)
        self.futuro_tf_ns = round(tolerancia_tf_futuro * SEGUNDO)
        self.parar_pendente = False
        self.cancelar_pendente = False
        self.sequencia_cancelamento = 0
        self.sequencia_parada = 0
        self.modo = 'desconhecido'
        self.geracao = None
        self.armado = False
        self.epoca = None
        self.objetivo = None
        self.retirados = set()
        self.comando = None
        self.mapa_valido = False
        self.sensores = {}
        self.motivo = 'inicializacao'
        self.ultima_falha = None
        self.ultimo_ros = None
        self.ultima_parede = None
        self.ultimo_comando = None
        self.ultima_entrada = None

    def receber_mapa(self, valido):
        """Mapa válido fica retido, sem exigir atualizações de mapa estático."""
        self.mapa_valido = bool(valido)
        if not valido and self.objetivo is not None:
            self._falhar('mapa_indisponivel')

    def receber_sensor(self, nome, carimbo, valido, agora_ros, agora_parede):
        """Registra scan/odom/tf; apenas carimbo estritamente novo renova lease."""
        falha_clock = self._observar_relogios(agora_ros, agora_parede)
        if falha_clock is not None and self.armado:
            self._falhar(falha_clock)
        anterior = self.sensores.get(nome)
        valido = bool(valido and type(carimbo) is int and carimbo > 0)
        if anterior is not None and carimbo < anterior[0]:
            valido = False
        if valido and anterior is not None and carimbo == anterior[0]:
            return
        self.sensores[nome] = (carimbo, agora_parede, bool(valido))
        if not valido and self.objetivo is not None:
            self._falhar(nome + '_indisponivel')

    def receber_estado(self, estado, agora_ros, agora_parede):
        """Consome o JSON do árbitro; modo/geração repetidos não rearmam."""
        relogio_valido = self.avaliar(agora_ros, agora_parede)['prerequisitos']['relogio']
        if (not isinstance(estado, dict) or
                estado.get('modo') not in ('manual', 'autonomo', 'parado') or
                type(estado.get('geracao')) is not int or estado['geracao'] < 0 or
                type(estado.get('ativo')) is not bool or
                not isinstance(estado.get('motivo'), str)):
            self._falhar('estado_arbitro_invalido')
            return
        if (estado['modo'], estado['geracao']) != (self.modo, self.geracao):
            if self.geracao is not None and estado['geracao'] <= self.geracao:
                self._falhar('geracao_invalida')
                return
            self.modo, self.geracao = estado['modo'], estado['geracao']
            self.armado = self.modo == 'autonomo' and not self.parar_pendente and relogio_valido
            self.epoca = agora_ros
            self._retirar_objetivo()
            self.ultimo_comando = None
            self.ultima_entrada = None
            self._cancelar()
            self.motivo = 'nova_epoca'

    def confirmar_cancelamento(self, sequencia, agora_ros, agora_parede):
        """Confirma RPC correspondente e cerca objetivos aceitos antes do ACK."""
        self.avaliar(agora_ros, agora_parede)
        if sequencia == self.sequencia_cancelamento:
            self.cancelar_pendente = False
            self.epoca = agora_ros

    def receber_objetivos(self, objetivos, agora_ros, agora_parede):
        """Lista completa de (UUID, aceitação_ns, GoalStatus), não um delta.

        ACCEPTED/EXECUTING são ativos; CANCELING e terminais neutralizam.
        Não impõe prazo artificial à execução/planejamento de uma ação: o
        protocolo de status não garante heartbeat periódico. Associação de
        comando a objetivo é temporal; TwistStamped não contém UUID de ação.
        """
        self.avaliar(agora_ros, agora_parede)
        ativos = [(i, c) for i, c, s in objetivos if s in (1, 2)]
        if (len(ativos) > 1 or any(s not in range(7) for _, _, s in objetivos) or
                any(type(c) is not int or c <= 0 or c > agora_ros + self.futuro_ns
                    for _, c in ativos)):
            self._falhar('status_objetivo_invalido')
            self.retirados.update(i for i, _ in ativos)
            return
        if self.objetivo is not None and self.objetivo not in ativos:
            self._retirar_objetivo()
            self._cancelar()
            self.motivo = 'objetivo_encerrado'
        candidatos = []
        for identidade, carimbo in ativos:
            if (not self.armado or self.cancelar_pendente or
                    identidade in self.retirados or carimbo <= self.epoca):
                self.retirados.add(identidade)
                self._cancelar()
            else:
                candidatos.append((identidade, carimbo))
        if candidatos:
            novo = max(candidatos, key=lambda item: item[1])
            if novo != self.objetivo:
                self._retirar_objetivo()
                self.objetivo = novo
                self.motivo = 'objetivo_ativo'
        self.avaliar(agora_ros, agora_parede)

    def _retirar_objetivo(self):
        if self.objetivo is not None:
            self.retirados.add(self.objetivo[0])
        self.objetivo = None
        self.comando = None

    def receber_comando(self, linear, angular, carimbo, agora_ros, agora_parede):
        """True autoriza encaminhar esta entrada uma vez; nunca renova replay."""
        if (not self.avaliar(agora_ros, agora_parede)['autorizado'] or
                self.objetivo is None or self.epoca is None):
            return False
        if (type(carimbo) is not int or carimbo <= 0 or
                not all(math.isfinite(v) for v in (linear, angular))):
            self.rejeitar_comando()
            return False
        if carimbo <= max(self.objetivo[1], self.epoca + self.futuro_ns):
            return False
        if self.ultimo_comando is not None and carimbo <= self.ultimo_comando:
            if (linear, angular, carimbo) != self.ultima_entrada:
                self._falhar('replay_ou_conflito')
            return False
        if (agora_ros - carimbo > round(self.prazo_comando * SEGUNDO) or
                carimbo - agora_ros > self.futuro_ns):
            self.rejeitar_comando()
            return False
        self.comando = (linear, angular, carimbo, agora_parede)
        self.ultimo_comando = carimbo
        self.ultima_entrada = (linear, angular, carimbo)
        return True

    def rejeitar_comando(self):
        if self.objetivo is not None and self.armado:
            self._falhar('comando_invalido')

    def rejeitar_objetivos(self):
        self._falhar('status_objetivo_invalido')

    def confirmar_parada(self, sequencia):
        if sequencia == self.sequencia_parada:
            self.parar_pendente = False

    def _cancelar(self):
        self.sequencia_cancelamento += 1
        self.cancelar_pendente = True

    def _falhar(self, motivo):
        self.armado = False
        self._retirar_objetivo()
        self.motivo = motivo
        self.ultima_falha = motivo
        self.sequencia_parada += 1
        self.parar_pendente = True
        self._cancelar()

    def _observar_relogios(self, agora_ros, agora_parede):
        falta = None
        if (type(agora_ros) is not int or agora_ros <= 0 or
                not math.isfinite(agora_parede) or agora_parede < 0):
            falta = 'relogio_invalido'
        elif ((self.ultimo_ros is not None and agora_ros < self.ultimo_ros) or
              (self.ultima_parede is not None and agora_parede < self.ultima_parede)):
            falta = 'retrocesso_relogio'
        if type(agora_ros) is int and agora_ros > 0 and math.isfinite(agora_parede):
            self.ultimo_ros = agora_ros
            self.ultima_parede = agora_parede
        return falta

    def avaliar(self, agora_ros, agora_parede):
        """Atualiza watchdog e retorna diagnóstico; jamais gera velocidade positiva.

        pronto mede pré-requisitos, aceita_objetivo inclui armamento e ACKs,
        autorizado inclui objetivo ativo, comando_valido inclui sua lease.
        ultima_falha preserva a causa mesmo após o estado parado do árbitro.
        """
        falta = self._observar_relogios(agora_ros, agora_parede)
        requisitos = {'mapa': self.mapa_valido, 'scan': False, 'odom': False,
                      'tf': False, 'relogio': False}
        requisitos['relogio'] = falta is None
        if falta is None:
            for nome in ('scan', 'odom', 'tf'):
                registro = self.sensores.get(nome)
                futuro = self.futuro_tf_ns if nome == 'tf' else self.futuro_ns
                prazo = self.prazo_tf if nome == 'tf' else self.prazo_sensores
                requisitos[nome] = bool(registro is not None and registro[2] and
                    -futuro <= agora_ros - registro[0] <= round(prazo * SEGUNDO) and
                    0 <= agora_parede - registro[1] <= prazo)
            falta = next((nome + '_indisponivel' for nome in ('mapa', 'scan', 'odom', 'tf')
                          if not requisitos[nome]), None)
        pronto = falta is None
        if not pronto and (self.objetivo is not None or
                           (self.armado and not requisitos['relogio'])):
            self._falhar(falta)
        if self.comando is not None and (
                agora_ros - self.comando[2] > round(self.prazo_comando * SEGUNDO) or
                agora_parede - self.comando[3] > self.prazo_comando):
            self.comando = None
            self.motivo = 'comando_expirado'
        autorizado = (pronto and self.armado and self.objetivo is not None and
                      not self.cancelar_pendente and not self.parar_pendente)
        return {'pronto': pronto, 'autorizado': autorizado,
                'armado': self.armado, 'ultima_falha': self.ultima_falha,
                'aceita_objetivo': pronto and self.armado and not self.cancelar_pendente and
                                   not self.parar_pendente,
                'bloqueado': not autorizado, 'requer_nova_selecao': not self.armado,
                'cancelamento_pendente': self.cancelar_pendente,
                'parada_pendente': self.parar_pendente, 'prerequisitos': requisitos,
                'motivo_prontidao': falta or 'pronto', 'epoca_ns': self.epoca,
                'objetivo': self.objetivo[0] if self.objetivo else None,
                'comando_valido': autorizado and self.comando is not None,
                'modo': self.modo, 'geracao': self.geracao, 'motivo': self.motivo}
