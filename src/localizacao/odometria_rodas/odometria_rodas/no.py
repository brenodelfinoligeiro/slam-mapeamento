"""Adaptador ROS 2: contagens idealizadas → odometria e juntas, sem TF."""

import math

import rclpy
from nav_msgs.msg import Odometry
from rcl_interfaces.msg import ParameterDescriptor
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.parameter import Parameter
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import JointState
from simulador_base.msg import LeituraRodas

from odometria_rodas.nucleo import OdometriaRodas


class CalcularOdometria(Node):
    def __init__(self):
        super().__init__("calcular_odometria", parameter_overrides=[
            Parameter("use_sim_time", value=True)])
        # Geometria obrigatória: fornecida pelo launch a partir do CAD, sem chute.
        self.declare_parameter("raio_roda", Parameter.Type.DOUBLE,
                               ParameterDescriptor(read_only=True, description="Raio da roda [m]"))
        self.declare_parameter("distancia_rodas", Parameter.Type.DOUBLE,
                               ParameterDescriptor(read_only=True, description="Distância entre rodas [m]"))
        self.declare_parameter("variancia_velocidade", 0.0025,
                               ParameterDescriptor(read_only=True, description="Variância linear [(m/s)²]"))
        self.declare_parameter("variancia_rotacao", 0.04,
                               ParameterDescriptor(read_only=True, description="Variância angular [(rad/s)²]"))
        self._nucleo = OdometriaRodas(**{
            nome: self.get_parameter(nome).value
            for nome in ("raio_roda", "distancia_rodas", "variancia_velocidade", "variancia_rotacao")})
        self._odometria = self.create_publisher(Odometry, "/odometria/rodas", 10)
        self._juntas = self.create_publisher(JointState, "/joint_states", 10)
        self._assinatura = self.create_subscription(
            LeituraRodas, "/sensores/rodas", self._receber, qos_profile_sensor_data)

    def _receber(self, mensagem):
        try:
            stamp = mensagem.header.stamp
            if not 0 <= stamp.nanosec < 1_000_000_000 or stamp.sec < 0:
                raise ValueError("Stamp ROS malformado")
            estado = self._nucleo.processar(
                stamp.sec * 1_000_000_000 + stamp.nanosec,
                mensagem.sessao, mensagem.contagem_esquerda,
                mensagem.contagem_direita, mensagem.pulsos_por_volta)
        except ValueError as erro:
            self.get_logger().warning(f"Leitura de rodas rejeitada: {erro}", throttle_duration_sec=2.0)
            return
        if estado is None:
            self.get_logger().warning("Baseline de rodas ressincronizado; intervalo descartado",
                                      throttle_duration_sec=2.0)
            return
        saida = Odometry()
        saida.header.stamp = mensagem.header.stamp
        saida.header.frame_id = "odom"
        saida.child_frame_id = "base_footprint"
        saida.pose.pose.position.x = estado.x
        saida.pose.pose.position.y = estado.y
        saida.pose.pose.orientation.z = math.sin(estado.angulo / 2.0)
        saida.pose.pose.orientation.w = math.cos(estado.angulo / 2.0)
        saida.pose.covariance = list(self._nucleo.covariancia_pose)
        saida.twist.twist.linear.x = estado.velocidade
        saida.twist.twist.linear.y = 0.0  # Restrição diferencial ideal, sem derrapagem.
        saida.twist.twist.angular.z = estado.rotacao
        saida.twist.covariance = list(self._nucleo.covariancia_velocidade)
        juntas = JointState()
        juntas.header.stamp = mensagem.header.stamp
        juntas.header.frame_id = "base_footprint"
        juntas.name = ["left_wheel_joint", "right_wheel_joint"]
        juntas.position = list(estado.posicoes)
        juntas.velocity = list(estado.velocidades)
        self._odometria.publish(saida)
        self._juntas.publish(juntas)


def main(args=None):
    rclpy.init(args=args)
    no = None
    try:
        no = CalcularOdometria()
        rclpy.spin(no)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        if no is not None:
            no.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
