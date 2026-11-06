"""Dublês apenas na fronteira DDS; ROS real sem serviços é ensaiado à parte."""
import importlib
from types import SimpleNamespace
import pytest


def modulo():
    return importlib.import_module('mapeamento_slam.salvar_mapa')


class Futuro:
    def __init__(self, concluido=True, erro=None):
        self.concluido = concluido
        self.erro = erro
        self.cancelado = False
    def done(self):
        return self.concluido
    def result(self):
        if self.erro:
            raise self.erro
        return 'resposta recebida'
    def cancel(self):
        self.cancelado = True


class No:
    def __init__(self, disponivel=True, futuro=None):
        self.disponivel = disponivel
        self.futuro = futuro or Futuro()
        self.destruidos = []
        self.requisicao = None
    def create_client(self, tipo, nome):
        self.nome = nome
        return self
    def wait_for_service(self, timeout_sec):
        assert 0 < timeout_sec <= 0.2
        return self.disponivel
    def call_async(self, requisicao):
        self.requisicao = requisicao
        return self.futuro
    def destroy_client(self, cliente):
        self.destruidos.append(cliente)


def spin(*args, **kwargs):
    assert 0 < kwargs['timeout_sec'] <= 0.2


def teste_transporte_recebe_resposta_e_destroi_cliente():
    no = No()
    requisicao = object()
    resposta = modulo().chamar_servico(no, SimpleNamespace(spin_until_future_complete=spin),
                                     object, '/slam_toolbox/save_map', requisicao, 0.2)
    assert resposta == 'resposta recebida'
    assert no.requisicao is requisicao
    assert no.destruidos == [no]


@pytest.mark.parametrize('caso', ['ausente', 'timeout', 'excecao'])
def teste_transporte_falha_com_prazo_e_limpa_cliente(caso):
    futuro = Futuro(concluido=caso != 'timeout', erro=RuntimeError('DDS') if caso == 'excecao' else None)
    no = No(disponivel=caso != 'ausente', futuro=futuro)
    with pytest.raises((RuntimeError, TimeoutError)):
        modulo().chamar_servico(no, SimpleNamespace(spin_until_future_complete=spin),
                               object, '/slam_toolbox/save_map', object(), 0.2)
    assert no.destruidos == [no]
    if caso == 'timeout':
        assert futuro.cancelado


def teste_requisicoes_usam_campos_oficiais_sem_copiar_srv():
    class Serializar:
        class Request:
            pass
    class Salvar:
        class Request:
            def __init__(self):
                self.name = SimpleNamespace(data='')
    tipos = {'serialize_map': Serializar, 'save_map': Salvar}
    assert modulo().criar_requisicao(tipos['serialize_map'], 'serialize_map', '/work/sala').filename == '/work/sala'
    requisicao = modulo().criar_requisicao(tipos['save_map'], 'save_map', '/work/sala')
    assert requisicao.map_url == '/work/sala'
    assert requisicao.map_topic == '/map'
    assert requisicao.image_format == 'pgm' and requisicao.map_mode == 'trinary'
    assert requisicao.free_thresh < requisicao.occupied_thresh


@pytest.mark.parametrize('tempo', ['0', '-1', 'nan', 'inf'])
def teste_cli_rejeita_timeout_invalido_sem_ros(tempo):
    with pytest.raises(SystemExit) as erro:
        modulo().main(['--arquivo', '/work/sala', '--timeout', tempo])
    assert erro.value.code == 2


def teste_cli_rejeita_prefixo_shell_sem_ros(capsys):
    assert modulo().main(['--arquivo', '/mapas/sala;comando']) == 1
    assert 'shell' in capsys.readouterr().err


def teste_cli_ajuda_explicita_mapeamento_e_recarga(capsys):
    with pytest.raises(SystemExit) as erro:
        modulo().main(['--help'])
    assert erro.value.code == 0
    texto = capsys.readouterr().out
    assert 'arquivo_grafo' in texto and 'localizacao' in texto
