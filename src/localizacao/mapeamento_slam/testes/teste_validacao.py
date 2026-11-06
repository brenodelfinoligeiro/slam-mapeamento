"""Contrato dos modos: nunca localizar usando um grafo ausente."""
from pathlib import Path
import importlib
import pytest


def modulo():
    return importlib.import_module('mapeamento_slam.validacao')


def teste_mapeamento_novo_nao_recebe_grafo():
    assert modulo().parametros_do_modo('mapeamento', '') == {'mode': 'mapping'}


@pytest.mark.parametrize('modo', ['localization', '', 'amcl', 'MAPEAMENTO'])
def teste_rejeita_modo_desconhecido(modo):
    with pytest.raises(ValueError, match='modo'):
        modulo().parametros_do_modo(modo, '')


@pytest.mark.parametrize('arquivo', ['', '/nao/existe/grafo'])
def teste_localizacao_exige_par_de_arquivos(arquivo):
    with pytest.raises(ValueError, match='grafo'):
        modulo().parametros_do_modo('localizacao', arquivo)


def teste_localizacao_rejeita_grafo_incompleto_ou_vazio(tmp_path):
    prefixo = tmp_path / 'sala'
    Path(str(prefixo) + '.posegraph').write_bytes(b'grafo')
    with pytest.raises(ValueError, match='grafo'):
        modulo().parametros_do_modo('localizacao', str(prefixo))
    Path(str(prefixo) + '.data').touch()
    with pytest.raises(ValueError, match='grafo'):
        modulo().parametros_do_modo('localizacao', str(prefixo))


def teste_localizacao_fornece_grafo_e_estimativa_inicial_explicitamente(tmp_path):
    prefixo = tmp_path / 'sala'
    for extensao in ['.posegraph', '.data']:
        Path(str(prefixo) + extensao).write_bytes(b'conteudo de ensaio estrutural')
    parametros = modulo().parametros_do_modo('localizacao', str(prefixo))
    assert parametros == {'mode': 'localization', 'map_file_name': str(prefixo),
                          'map_start_pose': [0.0, 0.0, 0.0]}
    with pytest.raises(ValueError, match='extens'):
        modulo().parametros_do_modo('localizacao', str(prefixo) + '.posegraph')


def teste_grafo_nao_aceita_extensao_arbitraria(tmp_path):
    prefixo = tmp_path / 'sala.txt'
    for extensao in ('.posegraph', '.data'):
        Path(str(prefixo) + extensao).write_bytes(b'fixture estrutural')
    with pytest.raises(ValueError, match='extens'):
        modulo().parametros_do_modo('localizacao', str(prefixo))
