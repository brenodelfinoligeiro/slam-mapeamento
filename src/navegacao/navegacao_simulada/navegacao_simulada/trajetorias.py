"""Histórico visual limitado; referência de simulação não alimenta o EKF."""
from collections import deque
import signal
import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from rclpy.signals import SignalHandlerOptions
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry,Path

class Trajetorias(Node):
    def __init__(self):
        super().__init__('trajetorias')
        self.assinaturas=[];self.historicos={};self.publicadores={};self.tempos={}
        for entrada,saida in [('/odom','/trajetoria/estimada'),('/odometria/rodas','/trajetoria/rodas'),('/simulacao/referencia','/trajetoria/referencia')]:
            self.historicos[saida]=deque(maxlen=3000);self.tempos[saida]=None
            self.publicadores[saida]=self.create_publisher(Path,saida,10)
            self.assinaturas.append(self.create_subscription(Odometry,entrada,lambda msg,chave=saida:self.receber(chave,msg),10))
    def receber(self,chave,mensagem):
        instante=mensagem.header.stamp.sec+mensagem.header.stamp.nanosec*1e-9
        anterior=self.tempos[chave]
        if anterior is not None and instante<anterior:self.historicos[chave].clear()
        if anterior is not None and 0<=instante-anterior<.1:return
        self.tempos[chave]=instante
        pose=PoseStamped();pose.header=mensagem.header;pose.pose=mensagem.pose.pose
        self.historicos[chave].append(pose)
        caminho=Path();caminho.header=mensagem.header;caminho.poses=list(self.historicos[chave]);self.publicadores[chave].publish(caminho)

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
    rclpy.init(args=args,signal_handler_options=SignalHandlerOptions.NO);no=Trajetorias()
    try:girar(no)
    except (KeyboardInterrupt,ExternalShutdownException):pass
    except RuntimeError as erro:
        # Jazzy pode falhar no take_message durante invalidação do contexto por SIGINT.
        if rclpy.ok() or not str(erro).startswith('Unable to convert call argument'):
            raise
    finally:
        no.destroy_node()
        if rclpy.ok():rclpy.shutdown()
