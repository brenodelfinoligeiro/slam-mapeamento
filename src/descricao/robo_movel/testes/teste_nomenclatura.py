"""Impede retorno de nome afetivo à identidade do software ROS."""
from pathlib import Path
import json
import xml.etree.ElementTree as ET

PACOTE = Path(__file__).resolve().parents[1]
TRABALHO = next(p for p in Path(__file__).resolve().parents if (p / 'docs').is_dir() and (p / 'src').is_dir())
POLITICA = json.loads((TRABALHO / 'docs/nomenclatura-ros.json').read_text())


def teste_identidade_ros_generica():
    assert PACOTE.name == POLITICA['pacote_principal']
    assert ET.parse(PACOTE / 'package.xml').getroot().findtext('name') == 'robo_movel'
    assert (PACOTE / 'robo_movel/__init__.py').is_file()
    assert (PACOTE / 'recursos/robo_movel').is_file()
    assert (PACOTE / 'descricao/robo_movel.urdf').is_file()
    assert ET.parse(PACOTE / 'descricao/robo_movel.urdf').getroot().attrib['name'] == 'robo_movel'


def teste_fontes_ros_sem_nome_afetivo():
    erros = []
    for arquivo in PACOTE.rglob('*'):
        if not arquivo.is_file() or '__pycache__' in arquivo.parts or arquivo.suffix in {'.pyc', '.stl'}:
            continue
        for termo in POLITICA['termos_proibidos']:
            if termo.casefold() in arquivo.relative_to(PACOTE).as_posix().casefold() or termo.casefold() in arquivo.read_text().casefold():
                erros.append(str(arquivo.relative_to(PACOTE)))
    assert not erros, erros
