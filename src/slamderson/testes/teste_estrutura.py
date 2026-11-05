"""Verifica a organização inicial do pacote ROS 2 acadêmico."""
from importlib import import_module
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DOMINIOS = ('navegacao', 'localizacao', 'dispositivos', 'percepcao', 'mapeamento', 'controle')
RECURSOS = ('inicializacao', 'configuracao', 'descricao', 'mapas', 'visualizacao')


def teste_estrutura_solicitada():
    for dominio in DOMINIOS:
        caminho = RAIZ / 'slamderson' / dominio
        assert (caminho / '__init__.py').is_file(), f'Módulo reservado ausente: {dominio}'
        assert import_module(f'slamderson.{dominio}').__name__ == f'slamderson.{dominio}'
    for pasta in RECURSOS:
        assert (RAIZ / pasta / '.gitkeep').is_file(), f'Pasta de recursos ausente: {pasta}'
