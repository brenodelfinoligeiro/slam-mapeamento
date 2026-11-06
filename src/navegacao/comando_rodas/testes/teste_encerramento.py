"""Não ocultar falhas reais ao tratar a corrida de shutdown do SDK Jazzy."""
import pytest
pytest.importorskip('rclpy')
from comando_rodas import no

@pytest.mark.parametrize('ativo,texto,rejeitar',[
 (False,"Unable to convert call argument '0' to Python object",False),
 (True,"Unable to convert call argument '0' to Python object",True),
 (False,'falha real de controle',True),
])
def teste_sdk_so_e_ignorado_apos_contexto_encerrado(monkeypatch,ativo,texto,rejeitar):
 eventos=[]
 class Modelo:
  def invalidar(self):eventos.append('invalidado')
 class No:
  modelo=Modelo()
  def publicar(self):eventos.append('zero')
  def destroy_node(self):eventos.append('destruido')
 monkeypatch.setattr(no,'ComandoRodas',No)
 monkeypatch.setattr(no.rclpy,'init',lambda **_:None)
 monkeypatch.setattr(no.rclpy,'ok',lambda:ativo)
 monkeypatch.setattr(no.rclpy,'shutdown',lambda:eventos.append('shutdown'))
 def girar(_):raise RuntimeError(texto)
 monkeypatch.setattr(no,'girar',girar)
 if rejeitar:
  with pytest.raises(RuntimeError,match=texto):no.main()
 else:no.main()
 assert eventos.count('destruido')==1 and eventos.count('invalidado')==1


def teste_sigint_nao_invalida_contexto_em_thread_interna(monkeypatch):
 from rclpy.signals import SignalHandlerOptions
 from comando_rodas import no as m
 opcoes={}
 class Modelo:
  def invalidar(self):pass
 class No:
  modelo=Modelo()
  def publicar(self):pass
  def destroy_node(self):pass
 monkeypatch.setattr(m,'ComandoRodas',No)
 monkeypatch.setattr(m.rclpy,'init',lambda **kwargs:opcoes.update(kwargs))
 monkeypatch.setattr(m.rclpy,'ok',lambda:False)
 def girar(_):raise KeyboardInterrupt
 monkeypatch.setattr(m,'girar',girar)
 m.main()
 assert opcoes.get('signal_handler_options')==SignalHandlerOptions.NO
