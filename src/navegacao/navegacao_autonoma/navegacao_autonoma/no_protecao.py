"""Adaptador rclpy do gate Nav2, com watchdog independente de /clock."""
import json
import math
import signal
import time

import rclpy
from rclpy.clock import Clock, ClockType
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from rclpy.signals import SignalHandlerOptions
from rclpy.time import Time
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy, qos_profile_sensor_data
from rcl_interfaces.msg import ParameterDescriptor
from geometry_msgs.msg import TwistStamped
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry, OccupancyGrid
from std_msgs.msg import String
from action_msgs.msg import GoalStatusArray
from action_msgs.srv import CancelGoal
from std_srvs.srv import Trigger
from tf2_ros import Buffer, TransformListener, TransformException
from arbitro.contrato import extrair_comando

from .protecao import ProtecaoAutonomia


def carimbo_ns(marca):
    if marca.sec < 0 or not 0 <= marca.nanosec < 1_000_000_000:
        raise ValueError('Carimbo ROS inválido')
    return marca.sec * 1_000_000_000 + marca.nanosec


def vetor_finito(vetor):
    return all(math.isfinite(v) for v in (vetor.x, vetor.y, vetor.z))


def quaternion_valido(q):
    valores = (q.x, q.y, q.z, q.w)
    return all(math.isfinite(v) for v in valores) and abs(sum(v * v for v in valores) - 1.) < .01


def pose_valida(pose):
    return vetor_finito(pose.position) and quaternion_valido(pose.orientation)


class NoProtecao(Node):
    """Não substitui o árbitro, o watchdog físico nem autentica publicadores."""

    def __init__(self):
        super().__init__('protecao_autonomia')
        descritor = ParameterDescriptor(read_only=True)
        parametros = {nome: self.declare_parameter(nome, valor, descritor).value
                      for nome, valor in (
                          ('prazo_sensores', .5), ('prazo_tf', .5), ('prazo_comando', .3),
                          ('tolerancia_futuro', .05), ('tolerancia_tf_futuro', .25))}
        self.modelo = ProtecaoAutonomia(**parametros)
        self.intervalo_retentativa = self.declare_parameter(
            'intervalo_retentativa', .25, descritor).value
        if not math.isfinite(self.intervalo_retentativa) or self.intervalo_retentativa <= 0:
            raise ValueError('Intervalo de retentativa inválido')
        self.cliente_cancelar = self.create_client(CancelGoal, '/navigate_to_pose/_action/cancel_goal')
        self.cliente_parar = self.create_client(Trigger, '/arbitro/parar')
        self.pedidos = {nome: {'futuro': None, 'sequencia': None,
                               'proxima': 0., 'estado': 'ocioso'}
                        for nome in ('cancelar', 'parar')}
        self.publicador = self.create_publisher(TwistStamped, '/cmd_vel_autonomo', 10)
        retido = QoSProfile(depth=1, reliability=ReliabilityPolicy.RELIABLE,
                            durability=DurabilityPolicy.TRANSIENT_LOCAL)
        self.estado = self.create_publisher(String, '/navegacao/estado', retido)
        self.buffer_tf = Buffer(node=self)
        self.ouvinte_tf = TransformListener(self.buffer_tf, self, spin_thread=False)
        self.assinaturas = [self.create_subscription(tipo, topico, callback, qos)
                            for tipo, topico, callback, qos in (
                                (TwistStamped, '/cmd_vel_nav2', self.receber_comando, 10),
                                (String, '/arbitro/estado', self.receber_estado, retido),
                                (GoalStatusArray, '/navigate_to_pose/_action/status', self.receber_objetivos, retido),
                                (LaserScan, '/scan', self.receber_scan, qos_profile_sensor_data),
                                (Odometry, '/odom', self.receber_odom, qos_profile_sensor_data),
                                (OccupancyGrid, '/map', self.receber_mapa, retido))]
        self.ultimo_estado = None
        self.timer = self.create_timer(.02, self.tick,
                                       clock=Clock(clock_type=ClockType.STEADY_TIME))
        self.tick()

    def tempos(self):
        return self.get_clock().now().nanoseconds, time.monotonic()

    def tick(self):
        tempos = self.tempos()
        try:
            tf = self.buffer_tf.lookup_transform('map', 'base_footprint', Time())
            valido = vetor_finito(tf.transform.translation) and quaternion_valido(tf.transform.rotation)
            marca = carimbo_ns(tf.header.stamp)
        except (TransformException, ValueError):
            valido, marca = False, 0
        self.modelo.receber_sensor('tf', marca, valido, *tempos)
        self.atualizar()

    def receber_estado(self, mensagem):
        try:
            estado = json.loads(mensagem.data)
        except (ValueError, TypeError):
            estado = None
        self.modelo.receber_estado(estado, *self.tempos())
        self.atualizar()

    def receber_objetivos(self, mensagem):
        try:
            objetivos = [(bytes(s.goal_info.goal_id.uuid).hex(),
                          carimbo_ns(s.goal_info.stamp), s.status) for s in mensagem.status_list]
            if any(not any(s.goal_info.goal_id.uuid) for s in mensagem.status_list):
                raise ValueError('UUID do objetivo nulo')
            self.modelo.receber_objetivos(objetivos, *self.tempos())
        except ValueError:
            self.modelo.rejeitar_objetivos()
        self.atualizar()

    def receber_comando(self, mensagem):
        try:
            linear, angular, _ = extrair_comando(mensagem)
            aceito = self.modelo.receber_comando(linear, angular, carimbo_ns(mensagem.header.stamp),
                                                *self.tempos())
        except ValueError:
            self.modelo.rejeitar_comando()
            aceito = False
        if aceito:
            # Encaminha a mensagem original, incluindo Time inteiro, uma única vez.
            self.publicador.publish(mensagem)
        self.atualizar()

    def receber_scan(self, mensagem):
        m = mensagem
        valido = (bool(m.header.frame_id) and len(m.ranges) > 0 and
                  all(math.isfinite(v) for v in (m.angle_min, m.angle_max, m.angle_increment,
                                                 m.range_min, m.range_max, m.scan_time, m.time_increment)) and
                  m.angle_increment > 0 and m.angle_max >= m.angle_min and
                  0 <= m.range_min < m.range_max and m.scan_time >= 0 and m.time_increment >= 0 and
                  all(v == math.inf or (math.isfinite(v) and m.range_min <= v <= m.range_max)
                      for v in m.ranges))
        self.registrar_sensor('scan', m.header.stamp, valido)

    def receber_odom(self, mensagem):
        m = mensagem
        valido = (m.header.frame_id == 'odom' and m.child_frame_id == 'base_footprint' and
                  pose_valida(m.pose.pose) and vetor_finito(m.twist.twist.linear) and
                  vetor_finito(m.twist.twist.angular) and
                  all(math.isfinite(v) for v in (*m.pose.covariance, *m.twist.covariance)))
        self.registrar_sensor('odom', m.header.stamp, valido)

    def receber_mapa(self, mensagem):
        m = mensagem
        valido = (m.header.frame_id == 'map' and m.info.width > 0 and m.info.height > 0 and
                  math.isfinite(m.info.resolution) and m.info.resolution > 0 and
                  pose_valida(m.info.origin) and len(m.data) == m.info.width * m.info.height and
                  all(-1 <= v <= 100 for v in m.data))
        self.modelo.receber_mapa(valido)
        self.atualizar()

    def registrar_sensor(self, nome, carimbo, valido):
        try:
            marca = carimbo_ns(carimbo)
        except ValueError:
            marca, valido = 0, False
        self.modelo.receber_sensor(nome, marca, valido and marca > 0, *self.tempos())
        self.atualizar()

    def atualizar(self):
        tempos = self.tempos()
        self.modelo.avaliar(*tempos)
        self.processar_servicos(*tempos)
        estado = self.modelo.avaliar(*tempos)
        estado['servicos'] = {nome: pedido['estado'] for nome, pedido in self.pedidos.items()}
        if not estado['comando_valido']:
            zero = TwistStamped()
            zero.header.frame_id = 'base_footprint'
            zero.header.stamp = self.get_clock().now().to_msg()
            self.publicador.publish(zero)
        conteudo = json.dumps(estado, ensure_ascii=False, sort_keys=True)
        if conteudo != self.ultimo_estado:
            self.estado.publish(String(data=conteudo))
            self.ultimo_estado = conteudo

    def processar_servicos(self, agora_ros, agora_parede):
        """Uma requisição em voo por serviço; sem espera em callbacks.

        Um future sem resposta permanece pendente: descartá-lo por timeout
        permitiria que uma mutação remota tardia cancelasse um objetivo novo.
        Serviço ausente, erro ou recusa são retentados; sucesso só confirma a
        intenção cuja sequência foi realmente enviada.
        """
        for nome, tipo in (('cancelar', CancelGoal), ('parar', Trigger)):
            pedido = self.pedidos[nome]
            futuro = pedido['futuro']
            if futuro is not None:
                if not futuro.done():
                    continue
                try:
                    resposta = futuro.result()
                    sucesso = (resposta.return_code == CancelGoal.Response.ERROR_NONE
                               if nome == 'cancelar' else resposta.success is True)
                except Exception as erro:
                    # Fronteira do transporte assíncrono, não dos callbacks de dados.
                    self.get_logger().warning(f'Falha assíncrona ao {nome}: {type(erro).__name__}')
                    sucesso = False
                pedido['futuro'] = None
                pedido['proxima'] = agora_parede + self.intervalo_retentativa
                if sucesso:
                    if nome == 'cancelar':
                        self.modelo.confirmar_cancelamento(pedido['sequencia'], agora_ros, agora_parede)
                    else:
                        self.modelo.confirmar_parada(pedido['sequencia'])
                pedido['estado'] = 'confirmado' if sucesso else 'erro'
            pendente = (self.modelo.cancelar_pendente if nome == 'cancelar'
                        else self.modelo.parar_pendente)
            if not pendente:
                pedido['estado'] = 'ocioso'
                continue
            if agora_parede < pedido['proxima']:
                continue
            cliente = self.cliente_cancelar if nome == 'cancelar' else self.cliente_parar
            pedido['proxima'] = agora_parede + self.intervalo_retentativa
            if not cliente.service_is_ready():
                pedido['estado'] = 'indisponivel'
                continue
            try:
                pedido['sequencia'] = (self.modelo.sequencia_cancelamento if nome == 'cancelar'
                                       else self.modelo.sequencia_parada)
                pedido['futuro'] = cliente.call_async(tipo.Request())
                pedido['estado'] = 'aguardando'
            except Exception as erro:
                self.get_logger().warning(f'Falha ao solicitar {nome}: {type(erro).__name__}')
                pedido['estado'] = 'erro'


def main(args=None):
    # Não injetar KeyboardInterrupt em construtores/casts C++ do SDK.
    # Instalar antes do construtor cobre também a criação preguiçosa do executor.
    interrompido = False
    def solicitar(numero, quadro):
        nonlocal interrompido
        interrompido = True
    anteriores = {s: signal.signal(s, solicitar) for s in (signal.SIGINT, signal.SIGTERM)}
    no = None
    try:
        rclpy.init(args=args, signal_handler_options=SignalHandlerOptions.NO)
        no = NoProtecao()
        while rclpy.ok() and not interrompido:
            rclpy.spin_once(no, timeout_sec=.1)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        if no is not None:
            if rclpy.ok():
                no.modelo.rejeitar_comando()
                no.atualizar()
            no.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
        for s, handler in anteriores.items():
            signal.signal(s, handler)


if __name__ == '__main__':
    main()
