"""Parar movimento e encerrar lifecycle antes de sinalizar processos."""
import json,time
import rclpy
from rclpy.node import Node
from rclpy.signals import SignalHandlerOptions
from std_srvs.srv import Trigger
from nav2_msgs.srv import ManageLifecycleNodes
from lifecycle_msgs.srv import GetState


def encerrar(no,prazo=12.):
    recibo={}
    for tipo,nome in [(Trigger,'/arbitro/parar'),
                      (ManageLifecycleNodes,'/lifecycle_navegacao/manage_nodes'),
                      (ManageLifecycleNodes,'/lifecycle_slam_navegacao/manage_nodes')]:
        cliente=no.create_client(tipo,nome)
        try:
            if not cliente.wait_for_service(timeout_sec=prazo):raise TimeoutError('Serviço ausente: '+nome)
            pedido=tipo.Request()
            if tipo is ManageLifecycleNodes:pedido.command=ManageLifecycleNodes.Request.SHUTDOWN
            futuro=cliente.call_async(pedido);limite=time.monotonic()+prazo
            while not futuro.done():
                if time.monotonic()>=limite:raise TimeoutError('Sem confirmação de encerramento: '+nome)
                rclpy.spin_once(no,timeout_sec=.05)
            resposta=futuro.result()
            if resposta is None or resposta.success is not True:raise RuntimeError('Encerramento recusado: '+nome)
            recibo[nome]=True
        finally:no.destroy_client(cliente)
    estados={}
    for nome in ['controller_server','planner_server','behavior_server','bt_navigator','slam_toolbox','salvador_mapa']:
        cliente=no.create_client(GetState,'/'+nome+'/get_state')
        try:
            if not cliente.wait_for_service(timeout_sec=prazo):raise TimeoutError('Sem leitura final de '+nome)
            futuro=cliente.call_async(GetState.Request());limite=time.monotonic()+prazo
            while not futuro.done():
                if time.monotonic()>=limite:raise TimeoutError('Estado final não respondeu: '+nome)
                rclpy.spin_once(no,timeout_sec=.05)
            estado=futuro.result().current_state
            if estado.id!=4:raise RuntimeError('Lifecycle não finalizado: '+nome+' '+estado.label)
            estados[nome]=estado.label
        finally:no.destroy_client(cliente)
    recibo['estados_confirmados']=estados
    return recibo


def main(args=None):
    rclpy.init(args=args,signal_handler_options=SignalHandlerOptions.NO)
    no=Node('encerrar_navegacao');codigo=2
    try:
        print(json.dumps(encerrar(no),ensure_ascii=False));codigo=0
    except (RuntimeError,TimeoutError) as erro:no.get_logger().error(str(erro))
    finally:
        no.destroy_node()
        if rclpy.ok():rclpy.shutdown()
    return codigo
