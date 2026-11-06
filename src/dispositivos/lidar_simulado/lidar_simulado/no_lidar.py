"""Adaptador ROS: pose perfeita só gera raios; TF exclusivamente estática."""

from dataclasses import fields
import math
from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from nav_msgs.msg import Odometry
from rcl_interfaces.msg import ParameterDescriptor, SetParametersResult
import signal
import rclpy
from rclpy.signals import SignalHandlerOptions
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.parameter import Parameter
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy, qos_profile_sensor_data
from rclpy.time import Time
from sensor_msgs.msg import LaserScan
from tf2_msgs.msg import TFMessage
from tf2_ros import Buffer, TransformException

from .aquisicao import LimitadorAquisicao, extrair_pose_planar, preencher_mensagem_scan
from .geometria import vetor_finito
from .mundo import carregar_mundo
from .varredura import GeradorVarredura, ParametrosLidar


class NoLidarSimulado(Node):
    def __init__(self):
        super().__init__('lidar_simulado', parameter_overrides=[Parameter('use_sim_time', value=True)])
        if self.get_parameter('use_sim_time').value is not True:
            raise ValueError('lidar_simulado exige use_sim_time=True')
        self.add_on_set_parameters_callback(self._proteger_relogio)
        descritor = ParameterDescriptor(
            read_only=True, description='Parâmetro do LiDAR VIRTUAL; configurável na inicialização.'
        )
        padroes = ParametrosLidar()
        valores = {
            campo.name: self.declare_parameter(campo.name, getattr(padroes, campo.name), descritor).value
            for campo in fields(padroes)
        }
        self._parametros = ParametrosLidar(**valores)
        caminho_padrao = str(Path(get_package_share_directory('lidar_simulado')) / 'configuracao' / 'mundo.yaml')
        caminho = self.declare_parameter('arquivo_mundo', caminho_padrao, descritor).value
        if not isinstance(caminho, str) or not caminho.strip():
            raise ValueError('arquivo_mundo deve ser um caminho YAML não vazio')
        self._gerador = GeradorVarredura(carregar_mundo(caminho), self._parametros)
        self._limitador = LimitadorAquisicao(self._parametros.frequencia)
        # Sem TransformListener: /tf dinâmico, odometria e fusão nunca entram neste buffer.
        self._buffer_estatico = Buffer()
        self._assinatura_tf = self.create_subscription(
            TFMessage, '/tf_static', self._receber_tf_estatica,
            QoSProfile(depth=100, reliability=ReliabilityPolicy.RELIABLE,
                       durability=DurabilityPolicy.TRANSIENT_LOCAL),
        )
        self._publicador = self.create_publisher(LaserScan, '/scan', qos_profile_sensor_data)
        self._assinatura_referencia = self.create_subscription(
            Odometry, '/simulacao/referencia', self._receber_referencia, qos_profile_sensor_data,
        )
        self.get_logger().warning(
            'LiDAR GEOMÉTRICO VIRTUAL: alinhamento fixo do modelo, não calibração do C1; '
            'sem física de colisão, medição global de pose ou mapa perfeito publicado.'
        )

    @staticmethod
    def _proteger_relogio(parametros):
        for parametro in parametros:
            if parametro.name == 'use_sim_time' and parametro.value is not True:
                return SetParametersResult(successful=False, reason='LiDAR virtual exige use_sim_time=True')
        return SetParametersResult(successful=True)

    def _receber_tf_estatica(self, mensagem):
        globais = {'map', 'odom', 'simulacao_mundo'}
        for transformacao in mensagem.transforms:
            pai, filho = transformacao.header.frame_id, transformacao.child_frame_id
            if not pai or not filho or pai in globais or filho in globais:
                continue
            translacao = transformacao.transform.translation
            rotacao = transformacao.transform.rotation
            try:
                vetor_finito((translacao.x, translacao.y, translacao.z), 3)
                quaternion = vetor_finito((rotacao.x, rotacao.y, rotacao.z, rotacao.w), 4)
                norma = math.hypot(*quaternion)
                if not math.isfinite(norma) or abs(norma - 1.) > 1e-3:
                    raise ValueError('Quaternion estático deve ser unitário')
                self._buffer_estatico.set_transform_static(transformacao, 'modelo_virtual')
            except (ValueError, TransformException) as erro:
                self.get_logger().warning(f'TF estática inválida descartada: {erro}', throttle_duration_sec=2.)

    def _obter_extrinseca(self):
        try:
            transformacao = self._buffer_estatico.lookup_transform(
                self._parametros.referencial_base, self._parametros.referencial_laser, Time()
            ).transform
            translacao, rotacao = transformacao.translation, transformacao.rotation
            return extrair_pose_planar(
                (translacao.x, translacao.y, translacao.z),
                (rotacao.x, rotacao.y, rotacao.z, rotacao.w),
            )
        except (TransformException, ValueError):
            # Lookup latest sem timeout: descarta a referência até o RSP/TF estática estar pronto.
            return None

    def _receber_referencia(self, mensagem):
        if (mensagem.header.frame_id != 'simulacao_mundo'
                or mensagem.child_frame_id != self._parametros.referencial_base):
            return
        marca = mensagem.header.stamp
        if marca.sec < 0 or not 0 <= marca.nanosec < 1_000_000_000:
            return
        pose = mensagem.pose.pose
        posicao, rotacao = pose.position, pose.orientation
        try:
            pose_base = extrair_pose_planar(
                (posicao.x, posicao.y, posicao.z), (rotacao.x, rotacao.y, rotacao.z, rotacao.w)
            )
            extrinseca = self._obter_extrinseca()
            if not self._limitador.admitir(
                marca.sec * 1_000_000_000 + marca.nanosec, pronto=extrinseca is not None
            ):
                return
            dados = self._gerador.varrer(pose_base, extrinseca)
        except ValueError as erro:
            self.get_logger().warning(f'Referência virtual inválida: {erro}', throttle_duration_sec=2.)
            return
        scan = LaserScan()
        preencher_mensagem_scan(scan, marca, dados, self._parametros)
        self._publicador.publish(scan)


def girar(no):
    # Não levantar KeyboardInterrupt dentro do cast pybind11 de take_message.
    # O sinal só muda a intenção; spin_once devolve o controle em até 0,1 s.
    interrompido=False
    def solicitar(numero,quadro):
        nonlocal interrompido
        interrompido=True
    anteriores={s:signal.signal(s,solicitar) for s in (signal.SIGINT,signal.SIGTERM)}
    try:
        while rclpy.ok() and not interrompido:rclpy.spin_once(no,timeout_sec=.1)
    finally:
        for s,handler in anteriores.items():signal.signal(s,handler)


def main(args=None):
    rclpy.init(args=args,signal_handler_options=SignalHandlerOptions.NO)
    no = None
    try:
        no = NoLidarSimulado()
        girar(no)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        if no is not None:
            no.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
