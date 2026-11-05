"""Verifica a localização em português da estrutura acadêmica do projeto."""
from importlib import import_module
from pathlib import Path
import xml.etree.ElementTree as ET

RAIZ = Path(__file__).resolve().parents[1]
DOMINIOS = ('navegacao', 'localizacao', 'dispositivos', 'percepcao', 'mapeamento', 'controle')
RECURSOS = ('inicializacao', 'configuracao', 'descricao', 'mapas', 'visualizacao')
NOMES_ANTERIORES = ('navigation', 'localization', 'devices', 'perception', 'slam', 'control')


def teste_localizacao_academica_em_portugues():
    for dominio in DOMINIOS:
        pasta = RAIZ / 'slamderson' / dominio
        assert (pasta / '__init__.py').is_file(), f'Módulo reservado ausente: {dominio}'

        assert import_module(f'slamderson.{dominio}').__name__ == f'slamderson.{dominio}'
    for nome in NOMES_ANTERIORES:
        assert not (RAIZ / 'slamderson' / nome).exists(), f'Nome anterior ainda presente: {nome}'
    for recurso in RECURSOS:
        assert (RAIZ / recurso / '.gitkeep').is_file(), f'Pasta de recursos ausente: {recurso}'
    manifesto = ET.parse(RAIZ / 'package.xml').getroot()
    assert manifesto.findtext('name') == 'slamderson'
    assert manifesto.findtext('export/build_type') == 'ament_python'
    assert 'Pacote ROS 2' in manifesto.findtext('description', '')
    assert (RAIZ / 'recursos' / 'slamderson').is_file()
