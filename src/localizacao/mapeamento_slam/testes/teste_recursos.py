"""Contratos verificáveis sem inferir qualidade de SLAM pela configuração."""
import ast
from pathlib import Path
import xml.etree.ElementTree as ET
import yaml

RAIZ = Path(__file__).resolve().parents[1]


def teste_configuracao_consume_scan_e_tf_estimado():
    parametros = yaml.safe_load((RAIZ / 'configuracao/slam.yaml').read_text())['slam_toolbox']['ros__parameters']
    assert {k: parametros[k] for k in ('map_frame', 'odom_frame', 'base_frame', 'scan_topic')} == {
        'map_frame': 'map', 'odom_frame': 'odom', 'base_frame': 'base_footprint', 'scan_topic': '/scan'}
    assert parametros['use_sim_time'] is True
    assert parametros['resolution'] == 0.05
    assert parametros['minimum_time_interval'] == 0.1
    assert parametros['minimum_travel_distance'] <= 0.1
    assert parametros['transform_publish_period'] > 0
    assert parametros['use_scan_matching'] is True
    assert parametros['use_map_saver'] is False
    assert 'map_file_name' not in parametros
    assert 'map_start_pose' not in parametros
    assert not any('referencia' in k or 'simulacao' in k for k in parametros)


def teste_composicao_simulada_nao_publica_transformacao_perfeita():
    texto = (RAIZ / 'inicializacao/slam_simulado.launch.py').read_text()
    arvore = ast.parse(texto)
    valores = [n.value for n in ast.walk(arvore) if isinstance(n, ast.Constant)]
    assert 'false' in valores and 'origem_virtual' in valores
    assert 'simular_lidar' in valores and 'arquivo_mundo' in valores
    assert 'configuracao/mundo.yaml' in valores
    assert 'lidar_mount_link' in valores and 'laser_simulado' in valores
    assert 'simulacao_mundo' in valores and 'map' in valores
    assert 'odom' not in valores and 'base_footprint' not in valores
    assert not any(v in valores for v in ('amcl', 'planner_server', 'controller_server', 'nav2_bringup'))
    funcao = next(n for n in arvore.body if isinstance(n, ast.FunctionDef) and n.name == 'compor')
    assert isinstance(funcao.body[0], ast.Expr)
    assert funcao.body[0].value.func.id == 'parametros_do_modo'


def teste_launch_tecnico_ativa_lifecycle_sem_dependencia_nav2():
    texto = (RAIZ / 'inicializacao/slam.launch.py').read_text()
    arvore = ast.parse(texto)
    nomes = {n.id for n in ast.walk(arvore) if isinstance(n, ast.Name)}
    assert {'LifecycleNode', 'OnStateTransition', 'ChangeState', 'RegisterEventHandler'} <= nomes
    assert 'TRANSITION_CONFIGURE' in texto and 'TRANSITION_ACTIVATE' in texto
    assert 'async_slam_toolbox_node' in texto and 'localization_slam_toolbox_node' in texto
    assert texto.index('parametros_do_modo(') < texto.index('LifecycleNode(')
    assert texto.index('RegisterEventHandler(') < texto.index('return [')
    assert 'nav2_lifecycle_manager' not in texto
    assert "DeclareLaunchArgument('modo', default_value='mapeamento')" in texto
    assert "DeclareLaunchArgument('arquivo_grafo', default_value='')" in texto


def teste_rviz_visualiza_mapa_sem_mapa_artificial():
    visual = yaml.safe_load((RAIZ / 'visualizacao/slam.rviz').read_text())['Visualization Manager']
    assert visual['Global Options']['Fixed Frame'] == 'map'
    exibicoes = {item['Class']: item for item in visual['Displays'] if item['Class'] != 'rviz_default_plugins/Path'}
    assert exibicoes['rviz_default_plugins/Map']['Topic']['Value'] == '/map'
    assert exibicoes['rviz_default_plugins/Map']['Topic']['Durability Policy'] == 'Transient Local'
    assert exibicoes['rviz_default_plugins/LaserScan']['Topic']['Value'] == '/scan'
    assert exibicoes['rviz_default_plugins/RobotModel']['Description Topic']['Durability Policy'] == 'Transient Local'
    assert 'CAD' not in str(visual)


def teste_manifesto_usa_interfaces_upstream_sem_rosidl():
    manifesto = ET.parse(RAIZ / 'package.xml').getroot()
    assert manifesto.findtext('name') == 'mapeamento_slam'
    assert manifesto.find('maintainer').text == 'lamggm'
    assert manifesto.find('maintainer').attrib['email'] == 'a_definir@example.com'
    assert manifesto.findtext('license') == 'A definir'
    dependencias = [elemento.text for elemento in manifesto.findall('exec_depend')]
    assert {'slam_toolbox', 'nav2_map_server', 'lidar_simulado', 'navegacao_simulada', 'rclpy'} <= set(dependencias)
    assert 'rosidl' not in (RAIZ / 'package.xml').read_text()
    assert not (RAIZ / 'srv').exists()


def teste_alcance_slam_nao_excede_lidar_virtual_configurado():
    parametros=yaml.safe_load((RAIZ/'configuracao/slam.yaml').read_text())['slam_toolbox']['ros__parameters']
    assert parametros['max_laser_range']<=10.0
