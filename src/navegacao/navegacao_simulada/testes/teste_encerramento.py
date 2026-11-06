"""Falha SDK no take_message após SIGINT não pode esconder erro em execução."""
import pytest
pytest.importorskip('rclpy')
from navegacao_simulada import trajetorias

@pytest.mark.parametrize('ativo,mensagem,rejeitar',[
    (False,'Unable to convert call argument 0 to Python object',False),
    (False,"Unable to convert call argument '0' to Python object",False),
    (True,'Unable to convert call argument 0 to Python object',True),
    (False,'erro legitimo do programa',True),
])
def teste_runtime_error_so_e_encerramento_com_contexto_invalido(monkeypatch,ativo,mensagem,rejeitar):
    eventos=[]
    class No:
        def destroy_node(self):eventos.append('destruido')
    monkeypatch.setattr(trajetorias,'Trajetorias',No)
    monkeypatch.setattr(trajetorias.rclpy,'init',lambda **_:None)
    monkeypatch.setattr(trajetorias.rclpy,'ok',lambda:ativo)
    monkeypatch.setattr(trajetorias.rclpy,'shutdown',lambda:eventos.append('shutdown'))
    def girar(_):raise RuntimeError(mensagem)
    monkeypatch.setattr(trajetorias,'girar',girar,raising=False)
    if rejeitar:
        with pytest.raises(RuntimeError,match=mensagem):trajetorias.main()
    else:trajetorias.main()
    assert eventos.count('destruido')==1


def teste_sigint_nao_invalida_contexto_em_thread_interna(monkeypatch):
 from rclpy.signals import SignalHandlerOptions
 from navegacao_simulada import trajetorias as m
 opcoes={}
 class Modelo:
  def invalidar(self):pass
 class No:
  modelo=Modelo()
  def publicar(self):pass
  def destroy_node(self):pass
 monkeypatch.setattr(m,'Trajetorias',No)
 monkeypatch.setattr(m.rclpy,'init',lambda **kwargs:opcoes.update(kwargs))
 monkeypatch.setattr(m.rclpy,'ok',lambda:False)
 def girar(_):raise KeyboardInterrupt
 monkeypatch.setattr(m,'girar',girar,raising=False)
 m.main()
 assert opcoes.get('signal_handler_options')==SignalHandlerOptions.NO


def teste_sinal_nao_injeta_excecao_no_take_message(monkeypatch):
 import signal
 handlers={};chamadas=[]
 def registrar(numero,handler):
  antigo=handlers.get(numero,signal.SIG_DFL);handlers[numero]=handler;return antigo
 monkeypatch.setattr(signal,'signal',registrar)
 monkeypatch.setattr(trajetorias.rclpy,'ok',lambda:True)
 def spin_once(no,timeout_sec):
  chamadas.append(timeout_sec)
  handlers[signal.SIGINT](signal.SIGINT,None)
 monkeypatch.setattr(trajetorias.rclpy,'spin_once',spin_once)
 trajetorias.girar(object())
 assert chamadas==[.1]
 assert handlers[signal.SIGINT]==signal.SIG_DFL
