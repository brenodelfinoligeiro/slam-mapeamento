"""Cinemática inversa e validade temporal, sem dependência ROS."""
import math

class Conversor:
    def __init__(self, raio=.05, distancia=.2, maximo_linear=.3, maximo_angular=1.5,
                 prazo=.4, limite_roda=20., tolerancia_futuro=.05):
        for valor in (raio, distancia, maximo_linear, maximo_angular, prazo, limite_roda):
            if not math.isfinite(valor) or valor <= 0: raise ValueError('Parâmetro deve ser positivo e finito')
        if not math.isfinite(tolerancia_futuro) or tolerancia_futuro < 0: raise ValueError('Tolerância inválida')
        self.raio=raio; self.distancia=distancia; self.maximo_linear=maximo_linear
        self.maximo_angular=maximo_angular; self.prazo=prazo; self.limite_roda=limite_roda
        self.tolerancia_futuro=tolerancia_futuro
        self._versao=0; self._versao_emitida=0; self._ultima_saida=(0.,0.)
        self._ultima_entrada=None; self._ultimo_relogio=None
        self.invalidar()

    def invalidar(self):
        self.referencia=(0.,0.); self.instante_origem=None; self.recebido_parede=None

    def rejeitar(self):
        self._versao+=1
        self.invalidar()

    def _registrar_relogio(self, agora_ros):
        if self._ultimo_relogio is not None and agora_ros < self._ultimo_relogio-self.tolerancia_futuro:
            self._ultima_entrada=None; self.rejeitar(); self._ultimo_relogio=agora_ros
            return False
        self._ultimo_relogio=max(agora_ros,self._ultimo_relogio or agora_ros)
        return True

    def nova_referencia(self, agora_ros, agora_parede):
        velocidades=self.rodas(agora_ros,agora_parede)
        if self._versao==self._versao_emitida and velocidades==self._ultima_saida:return None
        self._versao_emitida=self._versao; self._ultima_saida=velocidades
        return velocidades

    def receber(self, linear, angular, instante, agora_ros, agora_parede):
        valores=(linear,angular,instante,agora_ros,agora_parede)
        if not all(math.isfinite(v) for v in valores) or instante <= 0:
            self.rejeitar(); return False
        if not self._registrar_relogio(agora_ros):return False
        idade=agora_ros-instante
        if idade > self.prazo or idade < -self.tolerancia_futuro:
            self.rejeitar(); return False
        entrada=(linear,angular,instante)
        if self._ultima_entrada is not None and instante<=self._ultima_entrada[2]:
            # Timer e evento de tecla podem cair no mesmo tick de /clock.
            # Duplicata idêntica é idempotente, não é nova liveness/validade.
            if (entrada==self._ultima_entrada and self.instante_origem==instante and
                self.recebido_parede is not None and 0<=agora_parede-self.recebido_parede<=self.prazo):
                return True
            self.rejeitar();return False
        self._versao+=1
        escala=max(1.,abs(linear)/self.maximo_linear,abs(angular)/self.maximo_angular)
        linear/=escala; angular/=escala
        esquerda=(linear-angular*self.distancia/2)/self.raio
        direita=(linear+angular*self.distancia/2)/self.raio
        escala_rodas=max(1.,abs(esquerda)/self.limite_roda,abs(direita)/self.limite_roda)
        self.referencia=(esquerda/escala_rodas,direita/escala_rodas)
        self.instante_origem=instante; self.recebido_parede=agora_parede; self._ultima_entrada=entrada
        return True

    def rodas(self, agora_ros, agora_parede):
        if not all(math.isfinite(v) for v in (agora_ros,agora_parede)):
            self.invalidar();return self.referencia
        if not self._registrar_relogio(agora_ros):return self.referencia
        if self.instante_origem is None:return (0.,0.)
        if (agora_ros-self.instante_origem > self.prazo or
            agora_ros-self.instante_origem < -self.tolerancia_futuro or
            agora_parede-self.recebido_parede > self.prazo or agora_parede < self.recebido_parede):
            self.invalidar()
        return self.referencia
