"""Núcleo cinemático virtual, independente de ROS e de hardware."""

from dataclasses import dataclass
import math
import random
import secrets


@dataclass(frozen=True)
class ParametrosSimulacao:
    # Referência CAD confirmada pelo projeto; não é calibração física.
    raio_roda: float = 0.03446139931678772
    distancia_rodas: float = 0.13238015174865722
    frequencia: float = 50.0
    pulsos_por_volta: int = 720  # Resolução VIRTUAL, não medida no encoder real.
    prazo_comando: float = 0.4
    tolerancia_futuro: float = 0.05  # s; absorve ordenação de entrega DDS de /clock.
    escala_encoder_esquerda: float = 1.02
    escala_encoder_direita: float = 0.98
    ruido_giroscopio: float = 0.004
    bias_giroscopio: float = 0.01
    semente: int = 7
    publicar_clock: bool = True
    limite_velocidade_roda: float = 20.0  # rad/s, limite VIRTUAL.
    limite_aceleracao_roda: float = 500.0  # rad/s², rampa discreta VIRTUAL.

    def __post_init__(self):
        for nome in (
            'raio_roda', 'distancia_rodas', 'frequencia', 'prazo_comando',
            'tolerancia_futuro',
            'escala_encoder_esquerda', 'escala_encoder_direita',
            'limite_velocidade_roda', 'limite_aceleracao_roda',
        ):
            valor = getattr(self, nome)
            if not _finito(valor) or valor <= 0.0:
                raise ValueError(f'{nome} deve ser positivo e finito')
        if self.frequencia > 1e9:
            raise ValueError('frequencia excede a resolução temporal de 1 ns')
        if type(self.pulsos_por_volta) is not int or not 0 < self.pulsos_por_volta < 2**32:
            raise ValueError('pulsos_por_volta deve caber em uint32 não nulo')
        if not _finito(self.ruido_giroscopio) or self.ruido_giroscopio < 0.0:
            raise ValueError('ruido_giroscopio deve ser não negativo e finito')
        if not _finito(self.bias_giroscopio):
            raise ValueError('bias_giroscopio deve ser finito')
        if type(self.semente) is not int:
            raise ValueError('semente deve ser inteira')
        if type(self.publicar_clock) is not bool:
            raise ValueError('publicar_clock deve ser booleano')


def _finito(valor):
    return type(valor) in (int, float) and math.isfinite(valor)


@dataclass(frozen=True)
class EstadoSimulado:
    x: float
    y: float
    angulo: float
    velocidade_linear: float
    velocidade_angular: float
    sessao: int
    contagem_esquerda: int
    contagem_direita: int
    giroscopio_z: float
    aceleracao_x: float
    aceleracao_y: float
    aceleracao_z: float


class ReferenciaRodas:
    """Valida JointState e limita a validade por dois relógios independentes."""

    NOMES = ('left_wheel_joint', 'right_wheel_joint')

    def __init__(self, parametros: ParametrosSimulacao):
        self.parametros = parametros
        self.ativa = False
        self._comando = (0.0, 0.0)
        self._instante = 0.0
        self._recepcao = 0.0
        self._ultimo_instante = 0.0

    def invalidar(self):
        self.ativa = False
        self._comando = (0.0, 0.0)

    def receber(self, nomes, velocidades, instante, agora_ros, agora_monotonico) -> bool:
        self.invalidar()  # Toda entrada inválida revoga o comando anterior.
        if (
            len(nomes) != 2 or len(set(nomes)) != 2
            or set(nomes) != set(self.NOMES) or len(velocidades) != 2
            or not all(_finito(v) for v in (
                *velocidades, instante, agora_ros, agora_monotonico
            ))
        ):
            return False
        if (
            instante <= 0.0 or instante <= self._ultimo_instante
            or instante + self.parametros.prazo_comando <= agora_ros
            or instante > agora_ros + self.parametros.tolerancia_futuro
            or agora_monotonico < 0.0
        ):
            return False
        por_nome = dict(zip(nomes, velocidades))
        limite = self.parametros.limite_velocidade_roda
        esquerda, direita = (max(-limite, min(limite, por_nome[n])) for n in self.NOMES)
        self._comando = (esquerda, direita)
        self._instante = self._ultimo_instante = instante
        self._recepcao = agora_monotonico
        self.ativa = True
        return True

    def obter(self, agora_ros, agora_monotonico) -> tuple[float, float]:
        if not self.ativa:
            return (0.0, 0.0)
        if (
            not _finito(agora_ros) or not _finito(agora_monotonico)
            or agora_ros >= self._instante + self.parametros.prazo_comando
            or agora_monotonico >= self._recepcao + self.parametros.prazo_comando
            or agora_ros + self.parametros.tolerancia_futuro < self._instante
            or agora_monotonico < self._recepcao
        ):
            self.invalidar()
        return self._comando


class ModeloCinematico:
    def __init__(self, parametros: ParametrosSimulacao):
        self.parametros = parametros
        self.x = 0.0
        self.y = 0.0
        self.angulo = 0.0
        self.esquerda = 0.0
        self.direita = 0.0
        self._angulo_esquerda = 0.0
        self._angulo_direita = 0.0
        self._velocidade_anterior = 0.0
        self._aleatorio = random.Random(parametros.semente)
        # Identidade do processo, independente da semente de ruído.
        self.sessao = secrets.randbits(64) or 1

    def parar(self):
        """Parada virtual imediata de segurança, sem rampa de desaceleração."""
        self.esquerda = self.direita = 0.0

    def passo(self, esquerda: float, direita: float, dt: float) -> EstadoSimulado:
        if not all(_finito(v) for v in (esquerda, direita, dt)) or dt <= 0.0:
            raise ValueError('velocidades e dt devem ser finitos; dt deve ser positivo')
        limite = self.parametros.limite_velocidade_roda
        incremento = self.parametros.limite_aceleracao_roda * dt
        # Modelo virtual discreto: aplica a rampa na borda e mantém o twist
        # constante no intervalo. A integração SE(2) desse intervalo é exata.
        esquerda = self.esquerda + max(-incremento, min(
            incremento, max(-limite, min(limite, esquerda)) - self.esquerda
        ))
        direita = self.direita + max(-incremento, min(
            incremento, max(-limite, min(limite, direita)) - self.direita
        ))
        self.esquerda, self.direita = esquerda, direita
        velocidade = self.parametros.raio_roda * (esquerda + direita) / 2.0
        giro = self.parametros.raio_roda * (direita - esquerda) / self.parametros.distancia_rodas
        meio_giro = giro * dt / 2.0
        sinc = math.sin(meio_giro) / meio_giro if abs(meio_giro) > 1e-8 else (
            1.0 - meio_giro * meio_giro / 6.0
        )
        distancia = velocidade * dt * sinc
        self.x += distancia * math.cos(self.angulo + meio_giro)
        self.y += distancia * math.sin(self.angulo + meio_giro)
        self.angulo += giro * dt
        self._angulo_esquerda += esquerda * dt
        self._angulo_direita += direita * dt
        fator = self.parametros.pulsos_por_volta / math.tau
        # Contagens assinadas IDEALIZADAS: não certificam que o encoder real
        # de canal único detecte sentido. Quantização acumulada ao inteiro
        # mais próximo (empates pares), sem descartar subpulsos por amostra.
        contagem_esquerda = round(
            self._angulo_esquerda * fator * self.parametros.escala_encoder_esquerda
        )
        contagem_direita = round(
            self._angulo_direita * fator * self.parametros.escala_encoder_direita
        )
        giroscopio_z = giro + self.parametros.bias_giroscopio + self._aleatorio.gauss(
            0.0, self.parametros.ruido_giroscopio
        )
        # IMU VIRTUAL planar, nivelada, eixos alinhados ao corpo; sem braço
        # de alavanca, vibração, calibração de montagem ou orientação absoluta.
        aceleracao_x = (velocidade - self._velocidade_anterior) / dt
        self._velocidade_anterior = velocidade
        return EstadoSimulado(
            self.x, self.y, self.angulo, velocidade, giro, self.sessao,
            contagem_esquerda, contagem_direita, giroscopio_z,
            aceleracao_x, velocidade * giro, 9.80665,
        )
