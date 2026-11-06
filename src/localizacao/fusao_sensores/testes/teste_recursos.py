from pathlib import Path
import xml.etree.ElementTree as ET

def teste_manifesto_e_recursos():
    pasta = Path(__file__).resolve().parents[1]
    assert ET.parse(pasta/'package.xml').getroot().findtext('name') == pasta.name
    assert (pasta/'recursos'/pasta.name).is_file()
