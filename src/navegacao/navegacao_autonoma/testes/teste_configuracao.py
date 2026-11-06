"""Contratos de configuração; não comprovam navegação nem segurança física."""
from pathlib import Path
import os
import signal
import subprocess
import time
import xml.etree.ElementTree as ET

import pytest
import yaml

PACOTE = Path(__file__).resolve().parents[1]
CONFIGURACAO = PACOTE / 'configuracao'


def parametros(nome):
    arquivo = CONFIGURACAO / 'nav2.yaml'
    assert arquivo.is_file(), 'Falta a configuração Nav2 real'
    no = yaml.safe_load(arquivo.read_text(encoding='utf-8'))[nome]
    return no.get('ros__parameters', no)


def teste_controlador_diferencial_respeita_limites_virtuais():
    p = parametros('controller_server')
    assert p['use_sim_time'] is True
    assert p['enable_stamped_cmd_vel'] is True
    assert p['controller_frequency'] == 10.0
    assert p['odom_topic'] == '/odom'
    assert p['controller_plugins'] == ['FollowPath']
    assert all(0 <= p[k] <= 0.001 for k in (
        'min_x_velocity_threshold', 'min_y_velocity_threshold',
        'min_theta_velocity_threshold'))
    d = p['FollowPath']
    assert d['plugin'] == 'nav2_regulated_pure_pursuit_controller::RegulatedPurePursuitController'
    assert d['desired_linear_vel']==0.16
    assert d['use_collision_detection'] is True
    assert d['use_rotate_to_heading'] is True and d['allow_reversing'] is False
    assert 0<d['lookahead_dist']<.5 and 0<d['min_approach_linear_velocity']<.16
    assert d['max_angular_accel']==1.2
    assert d['rotate_to_heading_angular_vel']==.5
    assert d['use_regulated_linear_velocity_scaling'] is True
    assert d['use_cost_regulated_linear_velocity_scaling'] is True
    assert d['inflation_cost_scaling_factor']==3.0
    assert d['transform_tolerance']==.2
    assert p['goal_checker_plugins'] == ['goal_checker']
    assert p['goal_checker'] == {
        'plugin': 'nav2_controller::SimpleGoalChecker',
        'xy_goal_tolerance': 0.10, 'yaw_goal_tolerance': 0.15, 'stateful': True}
    assert p['progress_checker_plugins'] == ['progress_checker']
    assert p['progress_checker'] == {
        'plugin': 'nav2_controller::SimpleProgressChecker',
        'required_movement_radius': 0.05, 'movement_time_allowance': 20.0}


@pytest.mark.parametrize('nome,frame,camadas', [
    ('global_costmap', 'map', ['static_layer', 'obstacle_layer', 'inflation_layer']),
    ('local_costmap', 'odom', ['obstacle_layer', 'inflation_layer']),
])
def teste_costmaps_usam_raio_conservador_e_scan(nome, frame, camadas):
    p = parametros(nome)[nome]['ros__parameters']
    assert p['use_sim_time'] is True
    assert p['global_frame'] == frame
    assert p['robot_base_frame'] == 'base_footprint'
    assert p['robot_radius'] == 0.18 and p['footprint_padding'] == 0.0
    assert 'footprint' not in p
    assert p['resolution'] == 0.05
    assert p['track_unknown_space'] is True
    assert p['transform_tolerance'] == 0.2
    assert p['initial_transform_timeout'] == 0.3
    assert p['rolling_window'] is (nome == 'local_costmap')
    assert p['plugins'] == camadas
    assert p['inflation_layer']['plugin'] == 'nav2_costmap_2d::InflationLayer'
    assert p['inflation_layer']['inflation_radius'] == 0.35
    assert p['inflation_layer']['cost_scaling_factor'] > 0
    o = p['obstacle_layer']
    assert o['plugin'] == 'nav2_costmap_2d::ObstacleLayer'
    assert o['observation_sources'] == 'laser'
    s = o['laser']
    assert s['topic'] == '/scan' and s['sensor_frame'] == 'laser_simulado'
    assert s['data_type'] == 'LaserScan'
    assert s['clearing'] is s['marking'] is s['inf_is_valid'] is True
    assert s['expected_update_rate'] == 0.5
    assert s['observation_persistence'] == 0.0
    assert s['obstacle_max_range'] == 8.0
    assert s['raytrace_max_range'] == 10.0
    assert 0 <= s['raytrace_min_range'] <= s['obstacle_min_range']
    if nome == 'global_costmap':
        assert p['static_layer']['plugin'] == 'nav2_costmap_2d::StaticLayer'
        assert p['static_layer']['map_topic'] == '/map'
        assert p['static_layer']['map_subscribe_transient_local'] is True
        assert p['static_layer']['subscribe_to_updates'] is True
    else:
        assert p['width'] == p['height'] == 4
        assert type(p['width']) is type(p['height']) is int


def teste_servidores_minimos_e_interfaces_jazzy():
    planejador = parametros('planner_server')
    assert planejador['use_sim_time'] is True
    assert planejador['expected_planner_frequency'] == 1.0
    assert planejador['planner_plugins'] == ['GridBased']
    assert planejador['GridBased'] == {
        'plugin': 'nav2_navfn_planner::NavfnPlanner', 'tolerance': 0.10,
        'use_astar': False, 'allow_unknown': False}
    comportamento = parametros('behavior_server')
    assert comportamento['use_sim_time'] is True
    assert comportamento['enable_stamped_cmd_vel'] is True
    assert comportamento['behavior_plugins'] == ['spin', 'wait']
    assert comportamento['spin']['plugin'] == 'nav2_behaviors::Spin'
    assert comportamento['wait']['plugin'] == 'nav2_behaviors::Wait'
    assert comportamento['local_frame'] == 'odom'
    assert comportamento['global_frame'] == 'map'
    assert comportamento['robot_base_frame'] == 'base_footprint'
    assert comportamento['transform_tolerance'] == 0.2
    assert 0 < comportamento['min_rotational_vel'] < comportamento['max_rotational_vel'] <= 0.8
    assert 0 < comportamento['rotational_acc_lim'] <= 1.2
    for chave, valor in {
        'local_costmap_topic': 'local_costmap/costmap_raw',
        'global_costmap_topic': 'global_costmap/costmap_raw',
        'local_footprint_topic': 'local_costmap/published_footprint',
        'global_footprint_topic': 'global_costmap/published_footprint',
    }.items():
        assert comportamento[chave] == valor
    bt = parametros('bt_navigator')
    assert bt['use_sim_time'] is True
    assert bt['global_frame'] == 'map' and bt['robot_base_frame'] == 'base_footprint'
    assert bt['odom_topic'] == '/odom' and bt['transform_tolerance'] == 0.2
    assert bt['navigators'] == ['navigate_to_pose']
    assert bt['navigate_to_pose']['plugin'] == 'nav2_bt_navigator::NavigateToPoseNavigator'
    assert 'plugin_lib_names' not in bt  # As bibliotecas nativas são incluídas pelo Jazzy.
    assert 'default_nav_to_pose_bt_xml' not in bt  # Caminho absoluto vem do launch.
    dados = yaml.safe_load((CONFIGURACAO / 'nav2.yaml').read_text())
    assert set(dados) == {'planner_server', 'controller_server', 'behavior_server',
                          'bt_navigator', 'global_costmap', 'local_costmap'}


def elemento(raiz, caminho):
    no = raiz.find(caminho)
    assert no is not None, f'Elemento BT ausente: {caminho}'
    return no


def teste_arvore_replaneja_e_recupera_sem_recuo_cego():
    arquivo = CONFIGURACAO / 'ir_para.xml'
    assert arquivo.is_file(), 'Falta a árvore BT de navegação'
    raiz = ET.parse(arquivo).getroot()
    assert raiz.attrib == {'BTCPP_format': '4', 'main_tree_to_execute': 'IrPara'}
    arvore = elemento(raiz, "BehaviorTree[@ID='IrPara']")
    recuperacao = elemento(arvore, 'RecoveryNode')
    assert 1 <= int(recuperacao.attrib['number_of_retries']) <= 3
    assert len(recuperacao) == 2
    pipeline = elemento(recuperacao, 'PipelineSequence')
    taxa = elemento(pipeline, 'RateController')
    assert float(taxa.attrib['hz']) == 1.0
    plano = elemento(taxa, './/ComputePathToPose')
    assert plano.attrib == {'goal': '{goal}', 'path': '{path}',
                            'planner_id': 'GridBased',
                            'error_code_id': '{compute_path_error_code}'}
    seguir = elemento(pipeline, './/FollowPath')
    assert seguir.attrib == {'path': '{path}', 'controller_id': 'FollowPath',
                             'goal_checker_id': 'goal_checker',
                             'progress_checker_id': 'progress_checker',
                             'error_code_id': '{follow_path_error_code}'}
    for no in arvore.iter('RecoveryNode'):
        assert len(no) == 2
    servicos = {no.attrib['service_name'] for no in arvore.iter('ClearEntireCostmap')}
    assert servicos == {'local_costmap/clear_entirely_local_costmap',
                        'global_costmap/clear_entirely_global_costmap'}
    assert recuperacao.find('.//GoalUpdated') is not None
    spin = elemento(arvore, './/Spin')
    assert 0 < float(spin.attrib['spin_dist']) <= 0.8
    assert spin.attrib['error_code_id'] == '{spin_error_code}'
    assert float(spin.attrib['time_allowance']) >= 10.0
    espera = elemento(arvore, './/Wait')
    assert 0 < float(espera.attrib['wait_duration']) <= 3.0
    # Wait Jazzy não oferece error_code_id; o action server faz halt/cancel nativo.
    assert 'error_code_id' not in espera.attrib
    # Todas as saídas de erro são propagadas ao resultado NavigateToPose.
    codigos = {no.attrib['error_code_id'].strip('{}') for no in arvore.iter()
               if 'error_code_id' in no.attrib}
    assert set(parametros('bt_navigator')['error_code_names']) == codigos
    assert {no.tag for no in arvore.iter()} <= {
        'BehaviorTree', 'RecoveryNode', 'PipelineSequence', 'RateController',
        'ComputePathToPose', 'FollowPath', 'ClearEntireCostmap', 'Sequence',
        'ReactiveFallback', 'GoalUpdated', 'RoundRobin', 'Spin', 'Wait'}


@pytest.mark.skipif(not Path('/opt/ros/jazzy/share/nav2_controller').is_dir(),
                    reason='Exige a instalação real ROS 2 Jazzy/Nav2')
def teste_plugins_e_portas_exportados_pelo_jazzy_instalado():
    prefixo = Path('/opt/ros/jazzy')
    pacotes = ('nav2_controller', 'nav2_navfn_planner', 'nav2_regulated_pure_pursuit_controller', 'nav2_behaviors', 'nav2_bt_navigator', 'nav2_costmap_2d')
    classes = set()
    for pacote in pacotes:
        for arquivo in (prefixo / 'share' / pacote).glob('*.xml'):
            raiz = ET.parse(arquivo).getroot()
            bibliotecas = [raiz] if raiz.tag == 'library' else raiz.findall('library')
            for biblioteca in bibliotecas:
                assert (prefixo / 'lib' / f"lib{biblioteca.attrib['path']}.so").is_file()
                for classe in biblioteca.findall('class'):
                    classes.add(classe.attrib.get('name', classe.attrib['type']))
    dados = yaml.safe_load((CONFIGURACAO / 'nav2.yaml').read_text())

    def validar(valor):
        if isinstance(valor, dict):
            for chave, item in valor.items():
                if chave in ('plugin', 'trajectory_generator_name'):
                    assert item in classes, f'Classe não exportada: {item}'
                validar(item)
        elif isinstance(valor, list):
            for item in valor:
                validar(item)

    validar(dados)
    for critico in parametros('controller_server')['FollowPath'].get('critics', []):
        assert f'dwb_critics::{critico}Critic' in classes
    modelos = ET.parse(prefixo / 'share/nav2_behavior_tree/nav2_tree_nodes.xml').getroot()
    modelos = {no.attrib['ID']: no for no in modelos.iter() if 'ID' in no.attrib}
    for no in ET.parse(CONFIGURACAO / 'ir_para.xml').getroot().iter():
        if no.tag in ('root', 'BehaviorTree', 'Sequence', 'ReactiveFallback'):
            continue  # Estruturas nativas BT.CPP; instanciadas no teste de runtime.
        assert no.tag in modelos, f'Nó BT não instalado: {no.tag}'
        portas = {p.attrib['name'] for p in modelos[no.tag]}
        assert set(no.attrib) - {'name'} <= portas
    lista = (prefixo / 'include/nav2_behavior_tree/plugins_list.hpp').read_text()
    bibliotecas = lista.split('BT_BUILTIN_PLUGINS = "', 1)[1].split('"', 1)[0].split(';')
    assert bibliotecas
    assert all((prefixo / 'lib' / f'lib{nome}.so').is_file() for nome in bibliotecas)
    twist = (prefixo / 'include/nav2_util/nav2_util/twist_publisher.hpp').read_text()
    assert 'enable_stamped_cmd_vel' in twist and 'geometry_msgs::msg::TwistStamped' in twist


@pytest.mark.skipif(os.environ.get('NAV2_TESTAR_RUNTIME') != '1',
                    reason='Opt-in em contêiner isolado; não executar junto ao robô')
def teste_runtime_configura_plugins_instancia_bt_e_anuncia_tipo_correto(tmp_path):
    """Sem objetivos, mapas ou sensores artificiais: não é um ensaio E2E."""
    import rclpy
    from lifecycle_msgs.srv import ChangeState
    from rcl_interfaces.srv import GetParameters

    processos, arquivos = [], []
    rclpy.init()
    cliente = rclpy.create_node('sonda_configuracao_nav2')

    def chamar(tipo, nome, pedido):
        servico = cliente.create_client(tipo, nome)
        try:
            assert servico.wait_for_service(timeout_sec=12.0), nome
            futuro = servico.call_async(pedido)
            rclpy.spin_until_future_complete(cliente, futuro, timeout_sec=15.0)
            assert futuro.done(), f'Timeout: {nome}'
            resultado = futuro.result()
            assert resultado is not None, nome
            return resultado
        finally:
            cliente.destroy_client(servico)

    try:
        for pacote, executavel in (
            ('nav2_planner', 'planner_server'), ('nav2_controller', 'controller_server'),
            ('nav2_behaviors', 'behavior_server'), ('nav2_bt_navigator', 'bt_navigator'),
        ):
            log = (tmp_path / f'{executavel}.log').open('w')
            arquivos.append(log)
            comando = [f'/opt/ros/jazzy/lib/{pacote}/{executavel}', '--ros-args',
                       '--params-file', str(CONFIGURACAO / 'nav2.yaml'),
                       '-r', 'cmd_vel:=/cmd_vel_nav2']
            if executavel == 'bt_navigator':
                comando += ['-p', f'default_nav_to_pose_bt_xml:={CONFIGURACAO / "ir_para.xml"}']
            processos.append(subprocess.Popen(comando, stdout=log, stderr=subprocess.STDOUT))
        for nome in ('planner_server', 'controller_server', 'behavior_server', 'bt_navigator'):
            pedido = ChangeState.Request()
            pedido.transition.id = 1  # configure: carrega plugins reais, sem ativar movimento.
            assert chamar(ChangeState, f'/{nome}/change_state', pedido).success, nome
        pedido = ChangeState.Request()
        pedido.transition.id = 3  # Ativar só o navigator instancia a árvore e verifica portas.
        assert chamar(ChangeState, '/bt_navigator/change_state', pedido).success
        for nome in ('controller_server', 'behavior_server'):
            p = GetParameters.Request(names=['enable_stamped_cmd_vel', 'use_sim_time'])
            valores = chamar(GetParameters, f'/{nome}/get_parameters', p).values
            assert [v.bool_value for v in valores] == [True, True]
        for nome in ('local_costmap/local_costmap', 'global_costmap/global_costmap'):
            p = GetParameters.Request(names=['robot_radius', 'footprint_padding',
                                            'transform_tolerance', 'track_unknown_space'])
            valores = chamar(GetParameters, f'/{nome}/get_parameters', p).values
            assert [v.double_value for v in valores[:3]] == [0.18, 0.0, 0.2]
            assert valores[3].bool_value is True
        limite = time.monotonic() + 10.0
        publicadores = []
        while time.monotonic() < limite:
            publicadores = cliente.get_publishers_info_by_topic('/cmd_vel_nav2')
            if {p.node_name for p in publicadores} >= {'controller_server', 'behavior_server'}:
                break
            rclpy.spin_once(cliente, timeout_sec=0.1)
        assert {p.node_name for p in publicadores} == {'controller_server', 'behavior_server'}
        assert {p.topic_type for p in publicadores} == {'geometry_msgs/msg/TwistStamped'}
        # ObstacleLayer só assina /scan ao ativar: não ativamos os costmaps sem TF.
        for topico, tipo, nomes in (
            ('/map', 'nav_msgs/msg/OccupancyGrid', {'global_costmap'}),
            ('/odom', 'nav_msgs/msg/Odometry', {'controller_server', 'bt_navigator'}),
        ):
            limite = time.monotonic() + 5.0
            assinantes = []
            while time.monotonic() < limite:
                assinantes = cliente.get_subscriptions_info_by_topic(topico)
                if {s.node_name for s in assinantes} >= nomes:
                    break
                rclpy.spin_once(cliente, timeout_sec=0.1)
            assert {s.topic_type for s in assinantes} == {tipo}, topico
            assert {s.node_name for s in assinantes} >= nomes, topico
        from rclpy.qos import DurabilityPolicy
        mapa = cliente.get_subscriptions_info_by_topic('/map')
        assert all(s.qos_profile.durability == DurabilityPolicy.TRANSIENT_LOCAL for s in mapa)
        from rclpy.action import ActionClient
        from nav2_msgs.action import NavigateToPose
        acao = ActionClient(cliente, NavigateToPose, '/navigate_to_pose')
        try:
            assert acao.wait_for_server(timeout_sec=3.0)
        finally:
            acao.destroy()
        assert all(processo.poll() is None for processo in processos)
    finally:
        # Só encerra os subprocessos criados por esta sonda.
        for processo in processos:
            if processo.poll() is None:
                processo.send_signal(signal.SIGINT)
        for processo in processos:
            try:
                processo.wait(timeout=8.0)
            except subprocess.TimeoutExpired:
                processo.kill()
                processo.wait(timeout=3.0)
        cliente.destroy_node()
        rclpy.shutdown()
        for log in arquivos:
            log.close()
        for log in sorted(tmp_path.glob('*.log')):
            print(f'\n--- {log.name} ---\n{log.read_text()}')
    assert all(processo.returncode == 0 for processo in processos)
    for log in tmp_path.glob('*.log'):
        texto = log.read_text()
        assert '[ERROR]' not in texto and '[FATAL]' not in texto, texto
