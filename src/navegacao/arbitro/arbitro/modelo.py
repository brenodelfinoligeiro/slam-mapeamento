"""Seleção exclusiva, expiração ROS/monotônica e épocas de comando."""
import math

class Arbitro:
    def __init__(self,prazo=.3,tolerancia_futuro=.05):
        if (type(prazo) not in (int,float) or not math.isfinite(prazo) or prazo<=0 or
            type(tolerancia_futuro) not in (int,float) or not math.isfinite(tolerancia_futuro) or tolerancia_futuro<0):
            raise ValueError('Prazo/tolerância inválidos')
        self.prazo=prazo;self.tolerancia_futuro=tolerancia_futuro
        self.modo='manual';self.comando=None;self.barreira=None
        self.motivo='inicializacao';self.geracao=0
        self.recebido=None;self.ultimo_carimbo=None
        self.ultimo_ros=None;self.ultimo_parede=None
    def invalidar(self,motivo):
        self.comando=None;self.recebido=None;self.motivo=motivo
    def _relogios(self,ros,parede):
        if not all(math.isfinite(t) and t>=0 for t in (ros,parede)):
            self.modo='parado';self.invalidar('relogio_invalido');return False
        retrocesso=((self.ultimo_ros is not None and ros<self.ultimo_ros-1e-9) or
                    (self.ultimo_parede is not None and parede<self.ultimo_parede))
        self.ultimo_ros=ros;self.ultimo_parede=parede
        if retrocesso:
            self.modo='parado';self.invalidar('retrocesso_relogio');self.ultimo_carimbo=None
            self.barreira=ros+self.tolerancia_futuro;self.geracao+=1;return False
        return ros>0
    def selecionar(self,modo,agora_ros,agora_parede):
        if modo not in ('manual','autonomo'):raise ValueError('Modo inválido')
        if not self._relogios(agora_ros,agora_parede):return False
        self.modo=modo;self.invalidar('selecao_explicita')
        self.barreira=agora_ros+self.tolerancia_futuro
        self.ultimo_carimbo=None;self.geracao+=1;return True
    def parar(self,agora_ros,agora_parede):
        self._relogios(agora_ros,agora_parede)
        self.modo='parado';self.invalidar('parada_solicitada')
        self.barreira=agora_ros+self.tolerancia_futuro;self.geracao+=1
    def rejeitar(self,origem):
        if origem==self.modo:self.invalidar('entrada_invalida')
    def receber(self,origem,linear,angular,instante,agora_ros,agora_parede):
        if self.modo not in ('manual','autonomo') or origem!=self.modo:return False
        if not self._relogios(agora_ros,agora_parede):self.invalidar('relogio_nao_iniciado');return False
        if not all(math.isfinite(v) for v in (linear,angular,instante)) or instante<=0:
            self.invalidar('entrada_invalida');return False
        if self.barreira is not None and instante<=self.barreira:return False
        entrada=(linear,angular,instante)
        if self.ultimo_carimbo is not None and instante<=self.ultimo_carimbo:
            if entrada==self.comando and self._valido(agora_ros,agora_parede):return True
            self.invalidar('replay_ou_conflito');return False
        if agora_ros-instante>self.prazo or instante-agora_ros>self.tolerancia_futuro:
            self.invalidar('carimbo_fora_do_prazo');return False
        self.comando=entrada;self.recebido=agora_parede;self.ultimo_carimbo=instante
        self.motivo='comando_admitido';return True
    def _valido(self,agora_ros,agora_parede):
        return (self.comando is not None and self.recebido is not None and
            -self.tolerancia_futuro<=agora_ros-self.comando[2]<=self.prazo and
            0<=agora_parede-self.recebido<=self.prazo)
    def saida(self,agora_ros,agora_parede):
        if not self._relogios(agora_ros,agora_parede):return (0.,0.,agora_ros if math.isfinite(agora_ros) and agora_ros>=0 else 0.)
        if self.comando is not None and not self._valido(agora_ros,agora_parede):self.invalidar('comando_expirado')
        return self.comando or (0.,0.,agora_ros)
