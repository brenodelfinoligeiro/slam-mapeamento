"""Contrato inicial da descrição derivada do CAD; sem ROS/hardware no teste offline."""
from pathlib import Path
import json
import xml.etree.ElementTree as ET

RAIZ = Path(__file__).resolve().parents[1]


def teste_descricao_urdf_derivada_da_montagem_r05():
    arquivo = RAIZ / 'descricao/robo_movel.urdf'
    assert arquivo.is_file(), 'Descrição URDF da montagem R05 ainda não existe'
    robo = ET.parse(arquivo).getroot()
    assert robo.tag == 'robot' and robo.attrib['name'] == 'robo_movel'
    manifesto = json.loads((RAIZ / 'descricao/origem-cad.json').read_text())
    assert manifesto['revisao'] == 'R05'
    assert manifesto['pecas_impressas'] == 44
    assert manifesto['unidade'] == 'm'
    nomes = {link.attrib['name'] for link in robo.findall('link')}
    assert {'base_footprint', 'base_link', 'left_wheel_link', 'right_wheel_link',
            'lidar_mount_link', 'imu_mount_link'} <= nomes


def teste_launch_de_descricao_nao_inventa_joint_states():
    caminho = RAIZ / 'inicializacao/descricao.launch.py'
    assert caminho.is_file(), 'Launch de robot_state_publisher ainda não existe'
    texto = caminho.read_text()
    assert "package='robot_state_publisher'" in texto
    assert 'joint_state_publisher' not in texto
    assert 'cmd_vel' not in texto
    assert (RAIZ / 'inicializacao/visualizar.launch.py').is_file()
