"""Adaptador ROS 2 Jazzy; sensores sintéticos, sem TF, UART ou hardware."""

from dataclasses import fields
import math
import time

from builtin_interfaces.msg import Time
from nav_msgs.msg import Odometry
from rcl_interfaces.msg import ParameterDescriptor, SetParametersResult
import rclpy
from rclpy.clock import Clock, ClockType
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.parameter import Parameter
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy
from rosgraph_msgs.msg import Clock as MensagemClock
from sensor_msgs.msg import Imu, JointState

from simulador_base.msg import LeituraRodas
from simulador_base_nos.nucleo import (
    ModeloCinematico, ParametrosSimulacao, ReferenciaRodas,
)


class NoSimulador(Node):
    def __init__(self):
        super().__init__(
            'simulador_base',
            parameter_overrides=[Parameter('use_sim_time', value=True)],
        )
        if not self.get_parameter('use_sim_time').value:
            raise ValueError('simulador_base exige use_sim_time=True')
        padroes = ParametrosSimulacao()
        valores = {}
        for campo in fields(padroes):
            valores[campo.name] = self.declare_parameter(
                campo.name, getattr(padroes, campo.name),
                ParameterDescriptor(
                    read_only=True,
                    description='Parâmetro da simulação VIRTUAL; configurável na inicialização.',
                ),
            ).value
        self._parametros = ParametrosSimulacao(**valores)
        self.add_on_set_parameters_callback(self._proteger_relogio)
        self._modelo = ModeloCinematico(self._parametros)
        self._referencia = ReferenciaRodas(self._parametros)
        self._periodo_ns = round(1e9 / self._parametros.frequencia)
        self._dt = self._periodo_ns / 1e9
        self._tempo_ns = 0
        self._ultimo_clock_externo = None
        self._publicador_rodas = self.create_publisher(LeituraRodas, '/sensores/rodas', 10)
        self._publicador_imu = self.create_publisher(Imu, '/sensores/imu_bruta', 10)
        self._publicador_referencia = self.create_publisher(
            Odometry, '/simulacao/referencia', 10
        )
        self._publicador_clock = None
        if self._parametros.publicar_clock:
            self._publicador_clock = self.create_publisher(
                MensagemClock, '/clock', QoSProfile(depth=1, reliability=ReliabilityPolicy.BEST_EFFORT, durability=DurabilityPolicy.VOLATILE)
            )
        self._assinatura = self.create_subscription(
            JointState, '/rodas/referencia', self._receber_referencia,
            QoSProfile(depth=1),
        )
        # O dono de /clock não pode depender do relógio que ele próprio avança.
        self._relogio_estavel = Clock(clock_type=ClockType.STEADY_TIME)
        self._timer = self.create_timer(
            self._dt, self._atualizar, clock=self._relogio_estavel
        )
        self.get_logger().warning(
            'SIMULAÇÃO VIRTUAL: defaults geométricos de referência CAD, '
            'não calibração física; o launch pode fornecer raio_roda e distancia_rodas. '
            '720 pulsos/volta é resolução virtual, não medida. '
            'Contagens signed não certificam direção do encoder real de canal único. '
            'IMU planar idealizada, nivelada e alinhada ao corpo, sem braço de alavanca. '
            '/simulacao/referencia é ground truth para avaliação, nunca entrada do estimador.'
        )

    @staticmethod
    def _proteger_relogio(parametros):
        for parametro in parametros:
            if parametro.name == 'use_sim_time' and parametro.value is not True:
                return SetParametersResult(
                    successful=False, reason='A simulação exige use_sim_time=True'
                )
        return SetParametersResult(successful=True)

    def _agora_ros_ns(self):
        if self._parametros.publicar_clock:
            # Evita latência de loopback DDS do próprio /clock.
            return self._tempo_ns
        return self.get_clock().now().nanoseconds

    def _receber_referencia(self, mensagem):
        marca = mensagem.header.stamp
        if marca.sec < 0 or not 0 <= marca.nanosec < 1_000_000_000:
            self._referencia.invalidar()
            self._modelo.parar()
            return
        aceita = self._referencia.receber(
            mensagem.name, mensagem.velocity,
            marca.sec + marca.nanosec / 1e9,
            self._agora_ros_ns() / 1e9, time.monotonic(),
        )
        if not aceita:
            self._modelo.parar()  # Não aguarda o próximo timer para revogar movimento.
            self.get_logger().warning(
                'Referência rejeitada: nomes/velocidades/marca temporal inválidos, '
                'antigos, repetidos ou futuros além de tolerancia_futuro.',
                throttle_duration_sec=2.0,
            )

    @staticmethod
    def _marca(tempo_ns):
        segundos, nanossegundos = divmod(tempo_ns, 1_000_000_000)
        if not 0 <= segundos < 2**31:
            raise OverflowError('tempo simulado não cabe em builtin_interfaces/Time')
        return Time(sec=segundos, nanosec=nanossegundos)

    def _reiniciar_externo(self, agora_ns):
        self._modelo.parar()
        self._modelo = ModeloCinematico(self._parametros)
        self._referencia = ReferenciaRodas(self._parametros)
        self._tempo_ns = agora_ns
        self.get_logger().warning(
            'Salto do /clock externo: nova sessão, pose e contagens zeradas; '
            'é necessária nova referência.'
        )

    def _atualizar(self):
        agora_monotonico = time.monotonic()
        if self._parametros.publicar_clock:
            if self.count_publishers('/clock') > 1:
                self._referencia.invalidar()
                self._modelo.parar()
                self._timer.cancel()
                raise RuntimeError('Há outro publicador de /clock; simulação interrompida')
            self._tempo_ns += self._periodo_ns
            marca = self._marca(self._tempo_ns)
            self._publicador_clock.publish(MensagemClock(clock=marca))
        else:
            # Modo seguidor: sem /clock externo não avança e não inventa timestamps.
            agora_ns = self._agora_ros_ns()
            self._referencia.obter(agora_ns / 1e9, agora_monotonico)
            if not self._referencia.ativa:
                self._modelo.parar()
            if agora_ns <= 0:
                self._referencia.invalidar()
                self._modelo.parar()
                return
            if self._ultimo_clock_externo is None:
                self._ultimo_clock_externo = self._tempo_ns = agora_ns
                return
            atraso = agora_ns - self._tempo_ns
            if (
                agora_ns < self._ultimo_clock_externo
                or atraso > max(round(self._parametros.prazo_comando * 1e9),
                                100 * self._periodo_ns)
            ):
                self._reiniciar_externo(agora_ns)
                self._ultimo_clock_externo = agora_ns
                return
            self._ultimo_clock_externo = agora_ns
            if atraso < self._periodo_ns:
                return
            # Um passo fixo por chamada; não integra movimento retroativamente
            # com uma referência recebida no futuro do passo em atraso.
            self._tempo_ns += self._periodo_ns
            marca = self._marca(self._tempo_ns)
        esquerda, direita = self._referencia.obter(
            self._tempo_ns / 1e9, agora_monotonico
        )
        if not self._referencia.ativa:
            self._modelo.parar()
        estado = self._modelo.passo(esquerda, direita, self._dt)
        self._publicar_sensores(estado, marca)

    def _publicar_sensores(self, estado, marca):
        rodas = LeituraRodas()
        rodas.header.stamp = marca
        rodas.header.frame_id = 'base_link'
        rodas.sessao = estado.sessao
        if not all(-2**63 <= c < 2**63 for c in (
            estado.contagem_esquerda, estado.contagem_direita
        )):
            self._modelo.parar()
            raise OverflowError('Contagem virtual excedeu int64; reinicie a sessão')
        rodas.contagem_esquerda = estado.contagem_esquerda
        rodas.contagem_direita = estado.contagem_direita
        rodas.pulsos_por_volta = self._parametros.pulsos_por_volta
        self._publicador_rodas.publish(rodas)

        imu = Imu()
        imu.header.stamp = marca
        imu.header.frame_id = 'imu_mount_link'
        # Não há magnetômetro nem uma orientação absoluta medida.
        imu.orientation_covariance[0] = -1.0
        imu.angular_velocity.z = estado.giroscopio_z
        imu.angular_velocity_covariance[8] = self._parametros.ruido_giroscopio ** 2
        imu.linear_acceleration.x = estado.aceleracao_x
        imu.linear_acceleration.y = estado.aceleracao_y
        imu.linear_acceleration.z = estado.aceleracao_z
        # Covariância de aceleração não caracterizada: zeros = desconhecida.
        self._publicador_imu.publish(imu)

        referencia = Odometry()
        referencia.header.stamp = marca
        referencia.header.frame_id = 'simulacao_mundo'
        referencia.child_frame_id = 'base_footprint'
        referencia.pose.pose.position.x = estado.x
        referencia.pose.pose.position.y = estado.y
        referencia.pose.pose.orientation.z = math.sin(estado.angulo / 2.0)
        referencia.pose.pose.orientation.w = math.cos(estado.angulo / 2.0)
        referencia.twist.twist.linear.x = estado.velocidade_linear
        referencia.twist.twist.angular.z = estado.velocidade_angular
        # Verdade do modelo, não odometria dos sensores; nenhum TF é publicado.
        self._publicador_referencia.publish(referencia)


def main(args=None):
    rclpy.init(args=args)
    no = None
    try:
        no = NoSimulador()
        rclpy.spin(no)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        if no is not None:
            no.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
