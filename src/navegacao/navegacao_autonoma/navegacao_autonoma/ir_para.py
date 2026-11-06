"""Cliente NavigateToPose; exige modo autônomo explicitamente selecionado."""
import argparse,json,math,sys,time


def argumentos(args=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--x',type=float,required=True);p.add_argument('--y',type=float,required=True)
    p.add_argument('--yaw',type=float,default=0.);p.add_argument('--prazo',type=float,default=120.)
    o=p.parse_args(args)
    if not all(math.isfinite(v) for v in (o.x,o.y,o.yaw,o.prazo)) or o.prazo<=0:p.error('Coordenadas finitas e prazo positivo são obrigatórios')
    return o


def main(args=None):
    import rclpy
    from rclpy.utilities import remove_ros_args
    from rclpy.node import Node
    from rclpy.parameter import Parameter
    from rclpy.action import ActionClient
    from rclpy.qos import QoSProfile,ReliabilityPolicy,DurabilityPolicy
    from nav2_msgs.action import NavigateToPose
    from action_msgs.msg import GoalStatus
    from std_msgs.msg import String
    o=argumentos(remove_ros_args(args=sys.argv)[1:] if args is None else args)
    rclpy.init(args=args)
    no=Node('cliente_objetivo',parameter_overrides=[Parameter('use_sim_time',value=True)])
    estado={};protecao={};handle=None;fim=None
    qos=QoSProfile(depth=1,reliability=ReliabilityPolicy.RELIABLE,durability=DurabilityPolicy.TRANSIENT_LOCAL)
    def receber(m):
        try:estado.update(json.loads(m.data))
        except (ValueError,TypeError):estado.clear()
    assinatura=no.create_subscription(String,'/arbitro/estado',receber,qos)
    def receber_protecao(m):
        try:protecao.update(json.loads(m.data))
        except (ValueError,TypeError):protecao.clear()
    assinatura_protecao=no.create_subscription(String,'/navegacao/estado',receber_protecao,qos)
    cliente=ActionClient(no,NavigateToPose,'/navigate_to_pose')
    def esperar(condicao,prazo):
        limite=time.monotonic()+prazo
        while rclpy.ok() and not condicao():
            if time.monotonic()>=limite:raise TimeoutError('Prazo de navegação/comunicação expirado')
            rclpy.spin_once(no,timeout_sec=.05)
        if not rclpy.ok():raise RuntimeError('Contexto ROS encerrado')
    def cancelar():
        if handle is not None and (fim is None or not fim.done()):
            f=handle.cancel_goal_async()
            esperar(f.done,5.)
    codigo=2
    try:
        esperar(lambda:bool(estado) and no.get_clock().now().nanoseconds>0,10.)
        if estado.get('modo')!='autonomo':raise RuntimeError('Selecione autônomo explicitamente em /arbitro/automatico antes de enviar objetivo')
        geracao=estado.get('geracao')
        esperar(cliente.server_is_ready,10.)
        esperar(lambda:bool(protecao.get('aceita_objetivo')) and protecao.get('geracao')==geracao,10.)
        if estado.get('modo')!='autonomo' or estado.get('geracao')!=geracao:raise RuntimeError('Autoridade mudou durante preparação; objetivo descartado')
        objetivo=NavigateToPose.Goal();objetivo.pose.header.frame_id='map'
        objetivo.pose.header.stamp=no.get_clock().now().to_msg()
        objetivo.pose.pose.position.x=o.x;objetivo.pose.pose.position.y=o.y
        objetivo.pose.pose.orientation.z=math.sin(o.yaw/2);objetivo.pose.pose.orientation.w=math.cos(o.yaw/2)
        envio=cliente.send_goal_async(objetivo);esperar(envio.done,10.);handle=envio.result()
        if handle is None or not handle.accepted:raise RuntimeError('NavigateToPose recusou o objetivo')
        fim=handle.get_result_async();esperar(fim.done,o.prazo);res=fim.result()
        codigo=0 if res.status==GoalStatus.STATUS_SUCCEEDED else 2
        print(json.dumps({'status':res.status,'error_code':res.result.error_code,'error_msg':getattr(res.result,'error_msg','')},ensure_ascii=False))
    except (TimeoutError,RuntimeError,KeyboardInterrupt) as erro:
        print(f'Navegação interrompida: {erro}',file=sys.stderr)
        try:cancelar()
        except (RuntimeError,TimeoutError):pass
    finally:
        cliente.destroy();no.destroy_subscription(assinatura);no.destroy_subscription(assinatura_protecao);no.destroy_node()
        if rclpy.ok():rclpy.shutdown()
    return codigo


if __name__=='__main__':raise SystemExit(main())
