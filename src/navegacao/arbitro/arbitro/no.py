"""Adaptador ROS do árbitro; watchdog usa relógio monotônico independente."""
import json,math,time
import rclpy
from rclpy.node import Node
from rclpy.clock import Clock,ClockType
from rclpy.executors import ExternalShutdownException
from rclpy.qos import QoSProfile,DurabilityPolicy,ReliabilityPolicy
from rcl_interfaces.msg import ParameterDescriptor
from geometry_msgs.msg import TwistStamped
from std_msgs.msg import String
from std_srvs.srv import SetBool,Trigger
from .modelo import Arbitro
from .contrato import extrair_comando

class NoArbitro(Node):
    def __init__(self):
        super().__init__('arbitro')
        descritor=ParameterDescriptor(read_only=True)
        prazo=self.declare_parameter('prazo_comando',.3,descritor).value
        futuro=self.declare_parameter('tolerancia_futuro',.05,descritor).value
        self.modelo=Arbitro(prazo,futuro);self.carimbo=None;self.ultimo_estado=None
        self.publicador=self.create_publisher(TwistStamped,'/cmd_vel',10)
        qos=QoSProfile(depth=1,reliability=ReliabilityPolicy.RELIABLE,durability=DurabilityPolicy.TRANSIENT_LOCAL)
        self.estado=self.create_publisher(String,'/arbitro/estado',qos)
        self.assinaturas=[self.create_subscription(TwistStamped,topico,lambda m,o=origem:self.receber(o,m),10)
            for origem,topico in [('manual','/cmd_vel_manual'),('autonomo','/cmd_vel_autonomo')]]
        self.servicos=[self.create_service(SetBool,'/arbitro/automatico',self.selecionar),
                       self.create_service(Trigger,'/arbitro/parar',self.parar)]
        self.timer=self.create_timer(.02,self.publicar,clock=Clock(clock_type=ClockType.STEADY_TIME))
        self.publicar()
    def tempos(self):return self.get_clock().now().nanoseconds*1e-9,time.monotonic()
    def receber(self,origem,mensagem):
        try:
            linear,angular,instante=extrair_comando(mensagem)
            if self.modelo.receber(origem,linear,angular,instante,*self.tempos()):self.carimbo=mensagem.header.stamp
        except ValueError:self.modelo.rejeitar(origem)
        self.publicar()
    def selecionar(self,requisicao,resposta):
        resposta.success=self.modelo.selecionar('autonomo' if requisicao.data else 'manual',*self.tempos())
        self.carimbo=None;self.publicar()
        resposta.message='Época nova; envie comando novo após a tolerância de clock.' if resposta.success else 'Relógio não iniciado ou retrocesso detectado; sem permissão.'
        return resposta
    def parar(self,requisicao,resposta):
        self.modelo.parar(*self.tempos());self.carimbo=None;self.publicar()
        resposta.success=True;resposta.message='Parada travada; selecionar modo explicitamente para retomar.'
        return resposta
    def publicar(self):
        linear,angular,_=self.modelo.saida(*self.tempos())
        mensagem=TwistStamped();mensagem.header.frame_id='base_footprint'
        # Preserva o carimbo inteiro original, sem roundtrip float em nanossegundos.
        mensagem.header.stamp=self.carimbo if self.modelo.comando is not None and self.carimbo is not None else self.get_clock().now().to_msg()
        mensagem.twist.linear.x=linear;mensagem.twist.angular.z=angular
        self.publicador.publish(mensagem)
        estado=json.dumps({'modo':self.modelo.modo,'ativo':self.modelo.comando is not None,
                           'motivo':self.modelo.motivo,'geracao':self.modelo.geracao},ensure_ascii=False,sort_keys=True)
        if estado!=self.ultimo_estado:
            self.estado.publish(String(data=estado));self.ultimo_estado=estado

def main(args=None):
    rclpy.init(args=args);no=NoArbitro()
    try:rclpy.spin(no)
    except (KeyboardInterrupt,ExternalShutdownException):pass
    except RuntimeError as erro:
        if rclpy.ok() or not str(erro).startswith('Unable to convert call argument'):raise
    finally:
        if rclpy.ok():no.modelo.parar(*no.tempos());no.carimbo=None;no.publicar()
        no.destroy_node()
        if rclpy.ok():rclpy.shutdown()
