"""Adaptador exercitado com rclpy e mensagens Jazzy reais, sem robô/Nav2."""
import importlib
import json
from pathlib import Path

import pytest

rclpy = pytest.importorskip('rclpy')
from rclpy.clock import ClockType
from rclpy.qos import ReliabilityPolicy, DurabilityPolicy
from geometry_msgs.msg import TwistStamped, TransformStamped
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry, OccupancyGrid
from std_msgs.msg import String
from action_msgs.msg import GoalStatus, GoalStatusArray
from action_msgs.srv import CancelGoal
from std_srvs.srv import Trigger
from rclpy.task import Future
from rclpy.executors import SingleThreadedExecutor
import signal
import subprocess
import sys
import time
import select


def teste_main_modulo_executa_e_encerra_por_sigint():
    # Sinalizar durante imports/construção exercita objetos incompletos do tf2,
    # não o shutdown do nó. O invólucro só anuncia que o construtor terminou.
    codigo = (
        'import navegacao_autonoma.no_protecao as modulo\n'
        'original = modulo.NoProtecao\n'
        'def criar():\n'
        '    no = original()\n'
        '    print("NO_PRONTO", flush=True)\n'
        '    return no\n'
        'modulo.NoProtecao = criar\n'
        'modulo.main(["--ros-args", "-p", "use_sim_time:=true"])\n'
    )
    processo = subprocess.Popen([sys.executable, '-u', '-c', codigo],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        assert select.select([processo.stdout], [], [], 5.)[0], 'main não inicializou no prazo'
        assert processo.stdout.readline().strip() == 'NO_PRONTO'
        assert processo.poll() is None, 'main deve manter executor ativo'
        processo.send_signal(signal.SIGINT)
        saida, erros = processo.communicate(timeout=5)
        assert processo.returncode == 0, saida + erros
        assert 'Traceback' not in erros
    finally:
        if processo.poll() is None:
            processo.kill()
            processo.communicate()


def teste_servicos_e_estado_retido_no_dds_real_isolado(no):
    servidor = rclpy.create_node('servicos_gate_ensaio')
    executor = SingleThreadedExecutor()
    executor.add_node(no)
    executor.add_node(servidor)
    recebidos, estados = [], []

    def cancelar(requisicao, resposta):
        recebidos.append(('cancelar', requisicao))
        resposta.return_code = CancelGoal.Response.ERROR_NONE
        return resposta

    def parar(requisicao, resposta):
        recebidos.append(('parar', requisicao))
        resposta.success = True
        return resposta

    servicos = [servidor.create_service(CancelGoal, '/navigate_to_pose/_action/cancel_goal', cancelar),
                servidor.create_service(Trigger, '/arbitro/parar', parar)]
    assinatura = servidor.create_subscription(String, '/navegacao/estado',
                                              lambda m: estados.append(json.loads(m.data)),
                                              no.estado.qos_profile)
    try:
        no.receber_estado(String(data='inválido'))
        limite = time.monotonic() + 5.
        while time.monotonic() < limite:
            executor.spin_once(timeout_sec=.02)
            if (not no.modelo.cancelar_pendente and not no.modelo.parar_pendente and
                    any(not e['parada_pendente'] and e['motivo'] == 'estado_arbitro_invalido'
                        for e in estados)):
                break
        assert not no.modelo.cancelar_pendente and not no.modelo.parar_pendente
        assert {'parar', 'cancelar'} == {nome for nome, _ in recebidos}
        pedido = next(p for nome, p in recebidos if nome == 'cancelar')
        assert bytes(pedido.goal_info.goal_id.uuid) == bytes(16)
        assert pedido.goal_info.stamp.sec == 0 and pedido.goal_info.stamp.nanosec == 0
        assert estados and not estados[-1]['autorizado']
        assert not estados[-1]['parada_pendente']
    finally:
        executor.remove_node(no)
        executor.remove_node(servidor)
        executor.shutdown()
        servidor.destroy_node()


def teste_action_stamp_invalido_nao_derruba_callback_e_para(no):
    agora, *_ = dados_prontos(no)
    status = autorizar(no, agora)
    status.goal_info.stamp.sec = -1
    no.receber_objetivos(GoalStatusArray(status_list=[status]))
    assert no.modelo.parar_pendente and no.modelo.objetivo is None


class ClienteAdiado:
    """Somente o transporte é dublado; future e mensagens são os reais."""
    def __init__(self, disponivel=True):
        self.disponivel = disponivel
        self.requisicoes = []
        self.futuros = []

    def service_is_ready(self):
        return self.disponivel

    def call_async(self, requisicao):
        self.requisicoes.append(requisicao)
        futuro = Future()
        self.futuros.append(futuro)
        return futuro


def teste_cancelamento_async_repeticao_servico_indisponivel_e_confirmacao(no):
    agora = [BASE, 1.]
    no.tempos = lambda: tuple(agora)
    cliente = ClienteAdiado(False)
    no.cliente_cancelar = cliente
    no.receber_estado(String(data=json.dumps({'modo': 'manual', 'geracao': 0,
                                            'ativo': False, 'motivo': 'inicializacao'})))
    assert not cliente.requisicoes
    assert no.modelo.cancelar_pendente
    cliente.disponivel = True
    agora[1] = 1.3
    no.atualizar()
    assert len(cliente.requisicoes) == 1
    pedido = cliente.requisicoes[0]
    assert bytes(pedido.goal_info.goal_id.uuid) == bytes(16)
    assert pedido.goal_info.stamp.sec == 0 and pedido.goal_info.stamp.nanosec == 0
    # Não bloqueia nem lança outro pedido enquanto o primeiro não respondeu.
    agora[1] = 500.
    for _ in range(4):
        no.atualizar()
    assert len(cliente.requisicoes) == 1 and no.modelo.cancelar_pendente
    cliente.futuros[0].set_result(CancelGoal.Response(return_code=0))
    no.atualizar()
    assert not no.modelo.cancelar_pendente


def teste_falha_rpc_e_resposta_negativa_mantem_intencao_para_retry(no):
    agora = [BASE, 1.]
    no.tempos = lambda: tuple(agora)
    cliente = ClienteAdiado()
    no.cliente_cancelar = cliente
    no.receber_estado(String(data=json.dumps({'modo': 'manual', 'geracao': 0,
                                            'ativo': False, 'motivo': 'inicializacao'})))
    cliente.futuros[0].set_exception(RuntimeError('falha sintética de transporte'))
    no.atualizar()
    assert no.modelo.cancelar_pendente
    agora[1] = 1.3
    no.atualizar()
    assert len(cliente.futuros) == 2
    cliente.futuros[1].set_result(CancelGoal.Response(return_code=1))
    no.atualizar()
    assert no.modelo.cancelar_pendente
    agora[1] = 1.6
    no.atualizar()
    cliente.futuros[2].set_result(CancelGoal.Response(return_code=0))
    no.atualizar()
    assert not no.modelo.cancelar_pendente


def teste_parada_async_resposta_antiga_nao_rearma_ou_confirma_falha_nova(no):
    agora, *_ = dados_prontos(no)
    autorizar(no, agora)
    cliente = ClienteAdiado()
    no.cliente_parar = cliente
    no.modelo.rejeitar_comando()
    no.atualizar()
    assert len(cliente.requisicoes) == 1
    assert isinstance(cliente.requisicoes[0], Trigger.Request)
    no.receber_estado(String(data='JSON inválido'))
    cliente.futuros[0].set_result(Trigger.Response(success=True))
    no.atualizar()
    assert no.modelo.parar_pendente
    assert not no.modelo.armado
    agora[1] = 1.5
    no.atualizar()
    assert len(cliente.requisicoes) == 2
    cliente.futuros[1].set_result(Trigger.Response(success=True))
    no.atualizar()
    assert not no.modelo.parar_pendente
    assert not no.modelo.armado


class Coletor:
    def __init__(self):
        self.mensagens = []

    def publish(self, mensagem):
        self.mensagens.append(mensagem)


BASE = 1_800_000_000_000_000_000


def dados_prontos(no):
    agora = [BASE, 1.]
    no.tempos = lambda: tuple(agora)
    no.publicador = Coletor()
    scan = LaserScan()
    scan.header.frame_id = 'laser_simulado'
    scan.header.stamp.sec = BASE // 1_000_000_000
    scan.angle_min, scan.angle_max, scan.angle_increment = -1., 1., 1.
    scan.range_min, scan.range_max = .1, 10.
    scan.ranges = [1., float('inf'), 2.]
    odom = Odometry()
    odom.header.frame_id = 'odom'
    odom.child_frame_id = 'base_footprint'
    odom.header.stamp = scan.header.stamp
    odom.pose.pose.orientation.w = 1.
    mapa = OccupancyGrid()
    mapa.header.frame_id = 'map'
    mapa.info.width, mapa.info.height, mapa.info.resolution = 1, 1, .1
    mapa.info.origin.orientation.w = 1.
    mapa.data = [0]
    tf = TransformStamped()
    tf.header.frame_id, tf.child_frame_id = 'map', 'base_footprint'
    tf.header.stamp = scan.header.stamp
    tf.transform.rotation.w = 1.
    no.buffer_tf.set_transform(tf, 'ensaio_isolado')
    no.receber_scan(scan)
    no.receber_odom(odom)
    no.receber_mapa(mapa)
    no.tick()
    return agora, scan, odom, mapa


def autorizar(no, agora):
    no.receber_estado(String(data=json.dumps({'modo': 'autonomo', 'geracao': 1,
                                            'ativo': False, 'motivo': 'selecao_explicita'})))
    no.modelo.confirmar_cancelamento(no.modelo.sequencia_cancelamento, *agora)
    agora[:] = [BASE + 100_000_000, 1.1]
    status = GoalStatus()
    status.goal_info.goal_id.uuid = [1] * 16
    status.goal_info.stamp.sec = BASE // 1_000_000_000
    status.goal_info.stamp.nanosec = 100_000_000
    status.status = 2
    no.receber_objetivos(GoalStatusArray(status_list=[status]))
    return status


def teste_callbacks_reais_prontidao_e_comando_preservam_time_sem_replay_por_timer(no):
    agora, *_ = dados_prontos(no)
    assert json.loads(no.ultimo_estado)['pronto']
    autorizar(no, agora)
    agora[:] = [BASE + 123_456_789, 1.123]
    mensagem = TwistStamped()
    mensagem.header.frame_id = 'base_footprint'
    mensagem.header.stamp.sec = BASE // 1_000_000_000
    mensagem.header.stamp.nanosec = 123_456_789
    mensagem.twist.linear.x = .2
    no.receber_comando(mensagem)
    positivos = [m for m in no.publicador.mensagens if m.twist.linear.x != 0.]
    assert len(positivos) == 1
    assert positivos[0].header.stamp == mensagem.header.stamp
    assert positivos[0].header.stamp.nanosec == 123_456_789
    for _ in range(4):
        no.tick()
    no.receber_comando(mensagem)
    assert len([m for m in no.publicador.mensagens if m.twist.linear.x != 0.]) == 1


@pytest.mark.parametrize('campo', ['frame', 'nao_planar', 'nan'])
def teste_adaptador_reutiliza_contrato_e_para_entrada_ativa_invalida(no, campo):
    agora, *_ = dados_prontos(no)
    autorizar(no, agora)
    agora[:] = [BASE + 200_000_000, 1.2]
    m = TwistStamped()
    m.header.stamp.sec, m.header.stamp.nanosec = BASE // 1_000_000_000, 200_000_000
    m.twist.linear.x = .2
    if campo == 'frame':
        m.header.frame_id = 'map'
    elif campo == 'nao_planar':
        m.twist.linear.y = .1
    else:
        m.twist.angular.z = float('nan')
    no.receber_comando(m)
    assert no.modelo.parar_pendente
    assert no.publicador.mensagens[-1].twist.linear.x == 0.
    assert not any(m.twist.linear.x != 0. for m in no.publicador.mensagens)


@pytest.mark.parametrize('sensor', ['scan', 'odom', 'mapa'])
def teste_conteudo_de_sensor_invalido_trava_imediatamente(no, sensor):
    agora, scan, odom, mapa = dados_prontos(no)
    autorizar(no, agora)
    agora[:] = [BASE + 200_000_000, 1.2]
    if sensor == 'scan':
        scan.ranges = [float('nan')] * 3
        no.receber_scan(scan)
    elif sensor == 'odom':
        odom.pose.pose.position.x = float('inf')
        no.receber_odom(odom)
    else:
        mapa.data = []
        no.receber_mapa(mapa)
    assert no.modelo.parar_pendente
    assert no.modelo.objetivo is None


@pytest.fixture
def no():
    caminho = Path(__file__).parents[1] / 'navegacao_autonoma' / 'no_protecao.py'
    assert caminho.is_file(), 'Adaptador ROS ainda não implementado'
    rclpy.init(args=['--ros-args', '-p', 'use_sim_time:=true'])
    instancia = importlib.import_module('navegacao_autonoma.no_protecao').NoProtecao()
    try:
        yield instancia
    finally:
        instancia.destroy_node()
        rclpy.shutdown()


def teste_no_real_tem_contrato_qos_watchdog_steady_parametros_somente_leitura(no):
    assert no.get_name() == 'protecao_autonomia'
    topicos = {s.topic_name for s in no.subscriptions}
    assert {'/cmd_vel_nav2', '/arbitro/estado', '/scan', '/odom', '/map',
            '/navigate_to_pose/_action/status'} <= topicos
    assert no.publicador.topic_name == '/cmd_vel_autonomo'
    assert no.estado.topic_name == '/navegacao/estado'
    assert no.timer.clock.clock_type == ClockType.STEADY_TIME
    for assinatura in no.subscriptions:
        if assinatura.topic_name in ('/arbitro/estado', '/navigate_to_pose/_action/status', '/map'):
            assert assinatura.qos_profile.reliability == ReliabilityPolicy.RELIABLE
            assert assinatura.qos_profile.durability == DurabilityPolicy.TRANSIENT_LOCAL
    for nome in ('prazo_sensores', 'prazo_tf', 'prazo_comando',
                 'tolerancia_futuro', 'tolerancia_tf_futuro', 'intervalo_retentativa'):
        assert no.describe_parameter(nome).read_only
    assert json.loads(no.ultimo_estado)['pronto'] is False
    assert not no.modelo.parar_pendente
