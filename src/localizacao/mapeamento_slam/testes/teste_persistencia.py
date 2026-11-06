"""Persistência não pode confundir resposta recebida com arquivo salvo."""
import importlib
from pathlib import Path
from types import SimpleNamespace
import pytest


def modulo():
    return importlib.import_module('mapeamento_slam.persistencia')


def escrever_artefatos(prefixo):
    Path(str(prefixo) + '.posegraph').write_bytes(b'grafo de teste, nao ROS')
    Path(str(prefixo) + '.data').write_bytes(b'dados de teste, nao ROS')
    Path(str(prefixo) + '.pgm').write_bytes(b'P5\n2 2\n255\n\x00\xfe\xcd\xfe')
    Path(str(prefixo) + '.yaml').write_text(
        f'image: {prefixo.name}.pgm\nresolution: 0.05\norigin: [0.0, 0.0, 0.0]\n')


def teste_salvar_verifica_respostas_e_quatro_arquivos(tmp_path):
    prefixo = tmp_path / 'mapas/sala'
    chamadas = []
    def chamar(servico, arquivo):
        chamadas.append((servico, arquivo))
        if servico == 'save_map':
            escrever_artefatos(Path(arquivo))
        return SimpleNamespace(result=True) if servico == 'save_map' else SimpleNamespace(result=0, RESULT_SUCCESS=0)
    arquivos = modulo().salvar(str(prefixo), chamar, raiz=tmp_path)
    assert chamadas == [('serialize_map', str(prefixo)), ('save_map', str(prefixo))]
    assert {p.suffix for p in arquivos} == {'.pgm', '.yaml', '.posegraph', '.data'}
    assert all(p.stat().st_size > 0 for p in arquivos)


@pytest.mark.parametrize('resposta', [None, SimpleNamespace(), SimpleNamespace(result=255, RESULT_SUCCESS=0),
                                     SimpleNamespace(result=1, RESULT_SUCCESS=0)])
def teste_resposta_de_falha_interrompe_sem_anunciar_sucesso(tmp_path, resposta):
    chamadas = []
    def chamar(servico, arquivo):
        chamadas.append(servico)
        return resposta
    with pytest.raises(RuntimeError, match='serialize_map'):
        modulo().salvar(str(tmp_path / 'sala'), chamar, raiz=tmp_path)
    assert chamadas == ['serialize_map']


def teste_future_concluido_sem_arquivos_nao_e_sucesso(tmp_path):
    with pytest.raises(RuntimeError, match='arquivo'):
        modulo().salvar(str(tmp_path / 'sala'),
                        lambda servico, _: SimpleNamespace(result=True) if servico == 'save_map' else SimpleNamespace(result=0, RESULT_SUCCESS=0), raiz=tmp_path)


@pytest.mark.parametrize('extensao', ['.pgm', '.yaml', '.posegraph', '.data'])
def teste_nao_aceita_arquivos_antigos_como_resultado(tmp_path, extensao):
    Path(str(tmp_path / 'sala') + extensao).write_bytes(b'antigo')
    with pytest.raises(ValueError, match='exist'):
        modulo().salvar(str(tmp_path / 'sala'), lambda *_: pytest.fail('não chamar serviço'), raiz=tmp_path)


@pytest.mark.parametrize('nome', ['../fora', 'sala.yaml', 'sala.posegraph', 'sala.txt', 'com espaco', 'sala;comando'])
def teste_prefixo_de_saida_invalido_nao_chama_ros(tmp_path, nome):
    with pytest.raises(ValueError):
        modulo().salvar(str(tmp_path / nome), lambda *_: pytest.fail('não chamar serviço'), raiz=tmp_path)


def teste_symlink_nao_permite_sair_de_work(tmp_path):
    dentro = tmp_path / 'work'
    dentro.mkdir()
    (dentro / 'atalho').symlink_to(tmp_path, target_is_directory=True)
    with pytest.raises(ValueError):
        modulo().salvar(str(dentro / 'atalho/sala'), lambda *_: pytest.fail('não chamar'), raiz=dentro)


@pytest.mark.parametrize('defeito', ['imagem_errada', 'pgm_truncado', 'yaml_invalido', 'resolucao_invalida'])
def teste_valida_conteudo_efetivo_do_mapa(tmp_path, defeito):
    prefixo = tmp_path / 'sala'
    def chamar(servico, arquivo):
        if servico == 'save_map':
            escrever_artefatos(prefixo)
            if defeito == 'imagem_errada':
                Path(str(prefixo) + '.yaml').write_text('image: outra.pgm\nresolution: 0.05\norigin: [0,0,0]\n')
            elif defeito == 'pgm_truncado':
                Path(str(prefixo) + '.pgm').write_bytes(b'P5\n2 2\n255\n\x00')
            elif defeito == 'yaml_invalido':
                Path(str(prefixo) + '.yaml').write_text('[')
            else:
                Path(str(prefixo) + '.yaml').write_text('image: sala.pgm\nresolution: .nan\norigin: [0,0,0]\n')
        return SimpleNamespace(result=True) if servico == 'save_map' else SimpleNamespace(result=0, RESULT_SUCCESS=0)
    with pytest.raises(RuntimeError, match='mapa'):
        modulo().salvar(str(prefixo), chamar, raiz=tmp_path)


def teste_prefixo_absoluto_explicito_funciona_fora_de_work(tmp_path):
    # O operador escolhe um destino, inclusive o bind persistente /mapas.
    prefixo=tmp_path/'mapas_duraveis'/'sala'
    encontrado,arquivos=modulo().preparar_saida(str(prefixo))
    assert encontrado==prefixo
    assert len(arquivos)==4


def teste_salvador_nativo_rejeita_false_sem_confundir_com_codigo_zero(tmp_path):
    def chamar(servico,arquivo):
        return SimpleNamespace(result=False) if servico=='save_map' else SimpleNamespace(result=0,RESULT_SUCCESS=0)
    with pytest.raises(RuntimeError,match='save_map'):
        modulo().salvar(str(tmp_path/'sala'),chamar,raiz=tmp_path)
