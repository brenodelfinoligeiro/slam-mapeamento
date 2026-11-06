import ast
import configparser
from pathlib import Path
import runpy
from types import SimpleNamespace
import xml.etree.ElementTree as ElementTree

import pytest


RAIZ = Path(__file__).resolve().parents[1]


def teste_mensagem_preserva_aquisicao_e_campos_laserscan():
    from lidar_simulado.aquisicao import preencher_mensagem_scan
    from lidar_simulado.varredura import GeradorVarredura, ParametrosLidar
    from lidar_simulado.mundo import Mundo
    parametros = ParametrosLidar(numero_raios=4, ruido_desvio=0.)
    dados = GeradorVarredura(Mundo((-1, -1, 1, 1), ()), parametros).varrer((0, 0, 0), (0, 0, 0))
    mensagem = SimpleNamespace(header=SimpleNamespace())
    aquisicao = SimpleNamespace(sec=12, nanosec=340_000_000)
    preencher_mensagem_scan(mensagem, aquisicao, dados, parametros)
    assert mensagem.header.stamp is aquisicao
    assert mensagem.header.frame_id == 'laser_simulado'
    assert mensagem.angle_min == dados.angulo_minimo
    assert mensagem.angle_max == dados.angulo_maximo
    assert mensagem.angle_increment == dados.angulo_incremento
    assert mensagem.time_increment == 0.
    assert mensagem.scan_time == .1
    assert mensagem.range_min == .05
    assert mensagem.range_max == 10.
    assert len(mensagem.ranges) == 4
    assert mensagem.intensities == []


def teste_empacotamento_ament_instala_cenario_e_executavel(monkeypatch):
    import setuptools
    capturado = {}
    monkeypatch.setattr(setuptools, 'setup', lambda **valores: capturado.update(valores))
    monkeypatch.chdir(RAIZ)
    runpy.run_path(str(RAIZ / 'setup.py'), run_name='__main__')
    assert capturado['name'] == 'lidar_simulado'
    assert 'lidar_simulado' in capturado['packages']
    assert capturado['entry_points']['console_scripts'] == ['simular_lidar = lidar_simulado.no_lidar:main']
    arquivos = dict(capturado['data_files'])
    assert arquivos['share/ament_index/resource_index/packages'] == ['recursos/lidar_simulado']
    assert arquivos['share/lidar_simulado/configuracao'] == ['configuracao/mundo.yaml']
    assert (RAIZ / 'recursos' / 'lidar_simulado').is_file()
    manifesto = ElementTree.parse(RAIZ / 'package.xml').getroot()
    assert manifesto.findtext('name') == 'lidar_simulado'
    assert manifesto.findtext('export/build_type') == 'ament_python'
    assert manifesto.find('maintainer').attrib['email'] == 'a_definir@example.com'
    assert manifesto.findtext('maintainer') == 'lamggm'
    assert manifesto.findtext('license') == 'A definir'
    dependencias = {elemento.text for elemento in manifesto.findall('exec_depend')}
    assert {'rclpy', 'nav_msgs', 'sensor_msgs', 'tf2_ros', 'tf2_msgs', 'rcl_interfaces',
            'ament_index_python', 'python3-yaml'} <= dependencias
    configuracao = configparser.ConfigParser()
    configuracao.read(RAIZ / 'setup.cfg')
    assert configuracao['tool:pytest']['python_files'] == 'teste_*.py'
    assert configuracao['tool:pytest']['python_functions'] == 'teste_*'


def teste_no_so_publica_scan_e_consulta_tf_estatica_sem_bloqueio():
    codigo = (RAIZ / 'lidar_simulado' / 'no_lidar.py').read_text()
    arvore = ast.parse(codigo)
    chamadas = [no for no in ast.walk(arvore) if isinstance(no, ast.Call)]
    publicacoes = [no for no in chamadas if isinstance(no.func, ast.Attribute) and no.func.attr == 'create_publisher']
    assert len(publicacoes) == 1
    assert publicacoes[0].args[1].value == '/scan'
    assinaturas = [no for no in chamadas if isinstance(no.func, ast.Attribute) and no.func.attr == 'create_subscription']
    assert {no.args[1].value for no in assinaturas} == {'/tf_static', '/simulacao/referencia'}
    assert not any(isinstance(no.func, ast.Attribute) and no.func.attr in {'create_timer', 'now', 'set_transform'} for no in chamadas)
    consultas = [no for no in chamadas if isinstance(no.func, ast.Attribute) and no.func.attr == 'lookup_transform']
    assert len(consultas) == 1
    assert not consultas[0].keywords
    assert isinstance(consultas[0].args[2], ast.Call)
    assert consultas[0].args[2].func.id == 'Time'
    assert not consultas[0].args[2].args
    assert 'set_transform_static' in codigo
    assert 'qos_profile_sensor_data' in codigo
    assert 'qos_profile_clock' not in codigo
    assert not any(isinstance(no.func, ast.Name) and no.func.id == 'TransformListener' for no in chamadas)


def teste_importacao_real_ros_quando_disponivel():
    pytest.importorskip('rclpy', reason='ROS ausente: testes geométricos não validam ROS/DDS')
    from lidar_simulado.no_lidar import NoLidarSimulado
    assert callable(NoLidarSimulado)
