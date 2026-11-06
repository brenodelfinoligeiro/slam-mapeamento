import pytest
pytest.importorskip('rclpy')
from lidar_simulado import no_lidar as m

def teste_sinal_somente_marca_saida_do_loop(monkeypatch):
 import signal
 handlers={};chamadas=[]
 def registrar(numero,handler):
  antigo=handlers.get(numero,signal.SIG_DFL);handlers[numero]=handler;return antigo
 monkeypatch.setattr(signal,'signal',registrar)
 monkeypatch.setattr(m.rclpy,'ok',lambda:True)
 def spin(no,timeout_sec):
  chamadas.append(timeout_sec);handlers[signal.SIGINT](signal.SIGINT,None)
 monkeypatch.setattr(m.rclpy,'spin_once',spin)
 m.girar(object())
 assert chamadas==[.1] and handlers[signal.SIGINT]==signal.SIG_DFL

def teste_main_nao_invalida_contexto_durante_tf(monkeypatch):
 from rclpy.signals import SignalHandlerOptions
 opcoes={}
 class No:
  def destroy_node(self):pass
 monkeypatch.setattr(m,'NoLidarSimulado',No)
 monkeypatch.setattr(m.rclpy,'init',lambda **kw:opcoes.update(kw))
 monkeypatch.setattr(m.rclpy,'ok',lambda:False)
 monkeypatch.setattr(m,'girar',lambda _:None,raising=False)
 monkeypatch.setattr(m.rclpy,'spin',lambda _:None)
 m.main();assert opcoes['signal_handler_options']==SignalHandlerOptions.NO
