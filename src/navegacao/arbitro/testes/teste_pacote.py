from pathlib import Path
import xml.etree.ElementTree as ET

P=Path(__file__).resolve().parents[1]

def teste_manifesto_e_instalacao():
    raiz=ET.parse(P/'package.xml').getroot()
    assert raiz.findtext('name')=='arbitro'
    assert {'geometry_msgs','std_srvs','std_msgs','rclpy'}<={x.text for x in raiz.findall('exec_depend')}
    assert (P/'recursos/arbitro').is_file()
    assert 'arbitrar = arbitro.no:main' in (P/'setup.py').read_text()

def teste_composicao_preserva_simulacao_original_e_remapeia_teleop():
    texto=(P/'inicializacao/simulacao_arbitrada.launch.py').read_text()
    assert 'simulacao.launch.py' in texto and 'GroupAction' in texto
    assert '/cmd_vel_manual' in texto and '/cmd_vel_autonomo' in (P/'arbitro/no.py').read_text()
