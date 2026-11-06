"""Converte comando corporal carimbado em referência angular das rodas."""
import math,time
import signal
import rclpy
from rclpy.node import Node
from rclpy.clock import Clock,ClockType
from rclpy.executors import ExternalShutdownException
from rclpy.signals import SignalHandlerOptions
from geometry_msgs.msg import TwistStamped
from sensor_msgs.msg import JointState
from .modelo import Conversor

class ComandoRodas(Node):
    def __init__(self):
        super().__init__('comando_rodas')
        padroes={'raio_roda':.05,'distancia_rodas':.2,'maximo_linear':.3,'maximo_angular':1.5,'prazo_comando':.4}
        p={n:self.declare_parameter(n,v).value for n,v in padroes.items()}
        self.modelo=Conversor(raio=p['raio_roda'],distancia=p['distancia_rodas'],maximo_linear=p['maximo_linear'],maximo_angular=p['maximo_angular'],prazo=p['prazo_comando'])
        self.carimbo=None
        self.publicador=self.create_publisher(JointState,'/rodas/referencia',10)
        self.assinatura=self.create_subscription(TwistStamped,'/cmd_vel',self.receber,10)
        self.temporizador=self.create_timer(.02,self.publicar,clock=Clock(clock_type=ClockType.STEADY_TIME))

    def receber(self,mensagem):
        self.carimbo=mensagem.header.stamp
        v=mensagem.twist
        valores=(v.linear.x,v.linear.y,v.linear.z,v.angular.x,v.angular.y,v.angular.z)
        if not all(math.isfinite(x) for x in valores) or any(abs(x)>1e-12 for x in (v.linear.y,v.linear.z,v.angular.x,v.angular.y)):
            self.modelo.rejeitar();return
        instante=mensagem.header.stamp.sec+mensagem.header.stamp.nanosec*1e-9
        valido=self.modelo.receber(v.linear.x,v.angular.z,instante,self.get_clock().now().nanoseconds*1e-9,time.monotonic())
        # Mesmo para rejeição, preservar o carimbo de origem; não rejuvenescer comandos.

    def publicar(self):
        velocidades=self.modelo.nova_referencia(self.get_clock().now().nanoseconds*1e-9,time.monotonic())
        if velocidades is None:return
        mensagem=JointState();mensagem.name=['left_wheel_joint','right_wheel_joint'];mensagem.velocity=list(velocidades)
        # Preservar idade do comando não nulo, sem rejuvenescer seu carimbo a cada timer.
        mensagem.header.stamp=self.carimbo if self.carimbo is not None else self.get_clock().now().to_msg()
        mensagem.header.frame_id='base_footprint';self.publicador.publish(mensagem)

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
    rclpy.init(args=args,signal_handler_options=SignalHandlerOptions.NO);no=ComandoRodas()
    try:girar(no)
    except (KeyboardInterrupt, ExternalShutdownException):pass
    except RuntimeError as erro:
        if rclpy.ok() or not str(erro).startswith('Unable to convert call argument'):raise
    finally:
        no.modelo.invalidar()
        if rclpy.ok():no.publicar()
        no.destroy_node()
        if rclpy.ok():rclpy.shutdown()
