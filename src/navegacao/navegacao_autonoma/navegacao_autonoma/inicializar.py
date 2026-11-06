"""Pré-voo de uma execução: inicia lifecycle Nav2 após dados/TF prontos."""
import json,time
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile,ReliabilityPolicy,DurabilityPolicy
from rclpy.signals import SignalHandlerOptions
from rcl_interfaces.msg import ParameterDescriptor
from std_msgs.msg import String
from nav2_msgs.srv import ManageLifecycleNodes


def main(args=None):
    rclpy.init(args=args,signal_handler_options=SignalHandlerOptions.NO)
    no=Node('inicializar_navegacao');estado={};codigo=2
    prazo=no.declare_parameter('prazo_inicializacao',30.,ParameterDescriptor(read_only=True)).value
    if not isinstance(prazo,(int,float)) or not 0<prazo<=120:raise ValueError('Prazo de inicialização inválido')
    limite=time.monotonic()+prazo
    qos=QoSProfile(depth=1,reliability=ReliabilityPolicy.RELIABLE,durability=DurabilityPolicy.TRANSIENT_LOCAL)
    def receber(m):
        try:estado.update(json.loads(m.data))
        except (ValueError,TypeError):estado.clear()
    sub=no.create_subscription(String,'/navegacao/estado',receber,qos)
    cliente=no.create_client(ManageLifecycleNodes,'/lifecycle_navegacao/manage_nodes')
    def esperar(condicao):
        while rclpy.ok() and not condicao():
            if time.monotonic()>=limite:raise TimeoutError(str(estado.get('motivo_prontidao','aguardando proteção')))
            rclpy.spin_once(no,timeout_sec=.05)
    try:
        esperar(lambda:bool(estado.get('pronto')) and cliente.service_is_ready())
        pedido=ManageLifecycleNodes.Request();pedido.command=ManageLifecycleNodes.Request.STARTUP
        futuro=cliente.call_async(pedido);esperar(futuro.done)
        if futuro.result() is None or futuro.result().success is not True:raise RuntimeError('Lifecycle Nav2 recusou STARTUP')
        no.get_logger().info('Nav2 ativo após confirmação de mapa, sensores e TF; autoridade permanece no árbitro.')
        codigo=0
    except (RuntimeError,TimeoutError) as erro:no.get_logger().error(f'Falha de inicialização: {erro}')
    except KeyboardInterrupt:codigo=130
    finally:
        no.destroy_subscription(sub);no.destroy_client(cliente);no.destroy_node()
        if rclpy.ok():rclpy.shutdown()
    return codigo
