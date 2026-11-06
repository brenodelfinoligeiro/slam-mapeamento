"""Valida identidade da descrição e nomes dos recursos próprios."""
from pathlib import Path
import xml.etree.ElementTree as ET
RAIZ=Path(__file__).resolve().parents[1]

def teste_localizacao_academica_em_portugues():
    manifesto=ET.parse(RAIZ/'package.xml').getroot()
    assert manifesto.findtext('name')=='robo_movel'
    assert manifesto.findtext('export/build_type')=='ament_python'
    assert (RAIZ/'recursos/robo_movel').is_file()
    assert (RAIZ/'robo_movel/__init__.py').is_file()
    for recurso in ('inicializacao','configuracao','descricao','visualizacao'):
        assert (RAIZ/recurso).is_dir()
