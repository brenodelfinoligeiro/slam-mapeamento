"""Contrato estático de empacotamento; não substitui execução ROS/DDS."""

import ast
from pathlib import Path
import xml.etree.ElementTree as ET


RAIZ = Path(__file__).resolve().parents[1]


def teste_manifesto_e_instalacao_ament_python():
    manifesto = ET.parse(RAIZ / "package.xml").getroot()
    assert manifesto.findtext("name") == "odometria_rodas"
    assert manifesto.findtext("export/build_type") == "ament_python"
    assert manifesto.findtext("maintainer") == "lamggm"
    assert manifesto.find("maintainer").attrib["email"] == "a_definir@example.com"
    assert manifesto.findtext("license") == "A definir"
    dependencias = {elemento.text for elemento in manifesto.findall("exec_depend")}
    assert set(['rclpy', 'rcl_interfaces', 'simulador_base', 'nav_msgs', 'sensor_msgs']) <= dependencias
    assert (RAIZ / "recursos/odometria_rodas").is_file()
    setup = (RAIZ / "setup.py").read_text()
    assert "share/ament_index/resource_index/packages" in setup
    assert "calcular_odometria = odometria_rodas.no:main" in setup
    assert "package.xml" in setup


def teste_contrato_estatico_do_no():
    fonte = (RAIZ / "odometria_rodas/no.py").read_text()
    arvore = ast.parse(fonte)
    nomes_importados = {apelido.name for elemento in ast.walk(arvore)
                        if isinstance(elemento, ast.ImportFrom) for apelido in elemento.names}
    assert "Node" in nomes_importados
    assert "qos_profile_sensor_data" in nomes_importados
    assert "ParameterDescriptor" in nomes_importados
    assert "use_sim_time" in fonte
    assert "Time" not in nomes_importados  # Não substituir aquisição por hora de publicação.
    assert "TransformBroadcaster" not in fonte
    assert "tf2_ros" not in fonte
    assert "header.stamp = mensagem.header.stamp" in fonte
    assert {"LeituraRodas", "Odometry", "JointState"} <= nomes_importados
    for identificador in ("/sensores/rodas", "/odometria/rodas", "/joint_states",
                          "left_wheel_joint", "right_wheel_joint", "odom", "base_footprint"):
        assert identificador in fonte
