"""Adaptador ROS 2 para IMU virtual; preserva aquisição e não estima atitude."""

import rclpy
from rcl_interfaces.msg import ParameterDescriptor
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.parameter import Parameter
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Imu

from processamento_imu.nucleo import ProcessamentoImu


class TratarImu(Node):
    def __init__(self):
        super().__init__("tratar_imu", parameter_overrides=[
            Parameter("use_sim_time", value=True)])
        for nome, padrao, descricao in (
            ("bias_giroscopio_z", 0.01, "Bias virtual configurado, removido de gyroZ [rad/s]"),
            ("variancia_giroscopio", 0.000016, "Variância do giroscópio [(rad/s)²]; piso 1e-12"),
            ("variancia_acelerometro", 0.01, "Variância do acelerômetro [(m/s²)²]; piso 1e-12"),
            ("tolerancia_atraso", 0.3, "Idade máxima da aquisição no relógio ROS [s]"),
            ("tolerancia_futuro", 0.05, "Adiantamento máximo por ordem de entrega DDS [s]"),
        ):
            self.declare_parameter(nome, padrao,
                                   ParameterDescriptor(read_only=True, description=descricao))
        self._nucleo = ProcessamentoImu(**{
            nome: self.get_parameter(nome).value
            for nome in ("bias_giroscopio_z", "variancia_giroscopio",
                         "variancia_acelerometro", "tolerancia_atraso", "tolerancia_futuro")})
        self._publicador = self.create_publisher(Imu, "/imu/data_raw", 10)
        self._assinatura = self.create_subscription(
            Imu, "/sensores/imu_bruta", self._receber, qos_profile_sensor_data)

    def _receber(self, mensagem):
        try:
            stamp = mensagem.header.stamp
            if not 0 <= stamp.nanosec < 1_000_000_000 or stamp.sec < 0:
                raise ValueError("Stamp ROS malformado")
            if (mensagem.angular_velocity_covariance[0] == -1.0
                    or mensagem.linear_acceleration_covariance[0] == -1.0):
                raise ValueError("Giroscópio ou acelerômetro ausente na mensagem")
            g = mensagem.angular_velocity
            a = mensagem.linear_acceleration
            estado = self._nucleo.processar(
                stamp.sec * 1_000_000_000 + stamp.nanosec,
                self.get_clock().now().nanoseconds,
                (g.x, g.y, g.z), (a.x, a.y, a.z), mensagem.header.frame_id)
        except ValueError as erro:
            self.get_logger().warning(f"IMU rejeitada: {erro}", throttle_duration_sec=2.0)
            return
        saida = Imu()
        saida.header.stamp = mensagem.header.stamp
        saida.header.frame_id = estado.frame_id
        saida.angular_velocity.x, saida.angular_velocity.y, saida.angular_velocity.z = estado.giroscopio
        saida.linear_acceleration.x, saida.linear_acceleration.y, saida.linear_acceleration.z = estado.acelerometro
        saida.angular_velocity_covariance = list(estado.covariancia_giroscopio)
        saida.linear_acceleration_covariance = list(estado.covariancia_acelerometro)
        # Quaternion não fornecido: o sentinela -1 impede seu uso como atitude.
        saida.orientation_covariance = list(estado.covariancia_orientacao)
        self._publicador.publish(saida)


def main(args=None):
    rclpy.init(args=args)
    no = None
    try:
        no = TratarImu()
        rclpy.spin(no)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        if no is not None:
            no.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
