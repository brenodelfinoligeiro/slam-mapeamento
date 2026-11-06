"""Teleop em terminal real; manter tecla pressionada e espaço para parar."""
import os,sys,select,termios,tty,time
import rclpy
from rclpy.node import Node
from rclpy.clock import Clock,ClockType
from geometry_msgs.msg import TwistStamped
from .modelo import EstadoTeclado

class Teclado(Node):
    def __init__(self):
        super().__init__('teleoperacao_teclado')
        linear=self.declare_parameter('velocidade_linear',.15).value
        angular=self.declare_parameter('velocidade_angular',.6).value
        prazo=self.declare_parameter('prazo_tecla',.4).value
        self.estado=EstadoTeclado(linear,angular,prazo)
        self.publicador=self.create_publisher(TwistStamped,'/cmd_vel',10)
        self.temporizador=self.create_timer(.05,self.publicar,clock=Clock(clock_type=ClockType.STEADY_TIME))
    def publicar(self):
        v,w=self.estado.velocidade(time.monotonic());mensagem=TwistStamped()
        mensagem.header.stamp=self.get_clock().now().to_msg();mensagem.header.frame_id='base_footprint'
        mensagem.twist.linear.x=v;mensagem.twist.angular.z=w;self.publicador.publish(mensagem)

def main(args=None):
    if not sys.stdin.isatty():raise RuntimeError('Teleop exige terminal interativo (docker exec -it).')
    rclpy.init(args=args);no=Teclado();descritor=sys.stdin.fileno();anterior=termios.tcgetattr(descritor)
    print('w/s: frente/ré | a/d: giro | e/c: curvas | espaço: parar | q: sair. Mantenha tecla pressionada.',flush=True)
    try:
        tty.setraw(descritor)
        while rclpy.ok() and not no.estado.sair:
            rclpy.spin_once(no,timeout_sec=.01)
            if select.select([descritor],[],[],0)[0]:
                tecla=os.read(descritor,1).decode('utf-8',errors='ignore')
                no.estado.receber(tecla,time.monotonic());no.publicar()
    except (KeyboardInterrupt,EOFError):pass
    finally:
        no.estado.receber(' ',time.monotonic())
        if rclpy.ok():
            no.publicar()
            for _ in range(3):rclpy.spin_once(no,timeout_sec=.02)
        termios.tcsetattr(descritor,termios.TCSADRAIN,anterior);no.destroy_node()
        if rclpy.ok():rclpy.shutdown()
