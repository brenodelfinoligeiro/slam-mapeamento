"""Comandos de teclado com homem-morto por expiração de entrada."""
import math
class EstadoTeclado:
    def __init__(self, linear=.15, angular=.6, prazo=.4):
        if not all(math.isfinite(x) and x>0 for x in (linear,angular,prazo)):raise ValueError('Parâmetros inválidos')
        self.linear=linear;self.angular=angular;self.prazo=prazo;self.ultima_tecla=None
        self.comando=(0.,0.);self.sair=False
    def receber(self,tecla,agora):
        if not math.isfinite(agora):self.comando=(0.,0.);self.ultima_tecla=None;return
        self.ultima_tecla=agora
        self.comando={'w':(self.linear,0.),'s':(-self.linear,0.),'a':(0.,self.angular),'d':(0.,-self.angular),
                      'e':(self.linear,self.angular),'c':(self.linear,-self.angular)}.get(tecla,(0.,0.))
        if tecla in ('q','\x03'):self.sair=True;self.comando=(0.,0.)
    def velocidade(self,agora):
        if self.ultima_tecla is None or not math.isfinite(agora) or not 0<=agora-self.ultima_tecla<=self.prazo:
            self.comando=(0.,0.)
        return self.comando
