"""Contrato estrutural offline; não substitui build ROS, DDS ou execução do nó."""

import ast
from pathlib import Path
import xml.etree.ElementTree as ET


PASTA = Path(__file__).resolve().parents[1]


def teste_interface_rosidl_exata_e_instalacao_sem_colisao():
    assert (PASTA / 'msg/LeituraRodas.msg').read_text() == (
        'std_msgs/Header header\nuint64 sessao\nint64 contagem_esquerda\n'
        'int64 contagem_direita\nuint32 pulsos_por_volta\n'
    )
    cmake = (PASTA / 'CMakeLists.txt').read_text()
    assert 'rosidl_generate_interfaces' in cmake
    assert 'ament_get_python_install_dir(PYTHON_INSTALL_DIR)' in cmake
    assert 'ament_python_install_package' not in cmake
    assert 'install(PROGRAMS programas/simular DESTINATION lib/${PROJECT_NAME})' in cmake
    assert 'DESTINATION ${PYTHON_INSTALL_DIR}' in cmake
    assert 'ament_add_pytest_test' in cmake
    raiz = ET.parse(PASTA / 'package.xml').getroot()
    assert raiz.findtext('name') == 'simulador_base'
    assert raiz.findtext('license') == 'A definir'
    mantenedor = raiz.find('maintainer')
    assert mantenedor.text == 'lamggm'
    assert mantenedor.attrib['email'] == 'a_definir@example.com'
    assert raiz.findtext('export/build_type') == 'ament_cmake'
    assert raiz.findtext('member_of_group') == 'rosidl_interface_packages'
    dependencias = {item.text for item in raiz if 'depend' in item.tag}
    assert {
        'rclpy', 'geometry_msgs', 'sensor_msgs', 'nav_msgs', 'rosgraph_msgs',
        'std_msgs', 'builtin_interfaces', 'rosidl_default_generators',
        'rosidl_default_runtime', 'ament_cmake_python', 'ament_cmake_pytest',
    } <= dependencias


def teste_no_usa_timer_steady_interfaces_e_nao_transmite_tf():
    fonte = (PASTA / 'simulador_base_nos/no_simulador.py').read_text()
    arvore = ast.parse(fonte)
    chamadas = [n for n in ast.walk(arvore) if isinstance(n, ast.Call)]
    timers = [n for n in chamadas if isinstance(n.func, ast.Attribute)
              and n.func.attr == 'create_timer']
    assert len(timers) == 1
    assert any(k.arg == 'clock' for k in timers[0].keywords)
    assert 'ClockType.STEADY_TIME' in fonte
    assert 'TransformBroadcaster' not in fonte and 'tf2_ros' not in fonte
    for topico in ('/clock', '/sensores/rodas', '/sensores/imu_bruta',
                   '/simulacao/referencia', '/rodas/referencia'):
        assert repr(topico) in fonte
    assert 'from simulador_base.msg import LeituraRodas' in fonte
    assert "'imu_mount_link'" in fonte
    assert 'orientation_covariance[0] = -1.0' in fonte
    assert "'simulacao_mundo'" in fonte
    assert (PASTA / 'programas/simular').stat().st_mode & 0o111
    assert 'simulador_base_nos.no_simulador' in (PASTA / 'programas/simular').read_text()
