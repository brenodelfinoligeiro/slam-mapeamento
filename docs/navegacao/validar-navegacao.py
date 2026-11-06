"""Nav2 real sobre SLAM e planta virtual; nunca executar contra hardware.

Ground truth somente no oráculo; nenhum comando autônomo é sintetizado aqui.
"""
from pathlib import Path
import argparse,json,math,os,runpy,signal,subprocess,time,traceback
import yaml
import rclpy
from rclpy.action import ActionClient
from rclpy.time import Time
from rclpy.qos import QoSProfile,ReliabilityPolicy,DurabilityPolicy,qos_profile_sensor_data
from nav2_msgs.action import NavigateToPose
from nav_msgs.msg import OccupancyGrid,Path as Caminho
from sensor_msgs.msg import LaserScan
from std_msgs.msg import String
from std_srvs.srv import Trigger
from action_msgs.msg import GoalStatus
from lifecycle_msgs.srv import GetState
from ament_index_python.packages import get_package_share_directory
from oraculo import analisar_percurso

BASE=runpy.run_path(str(Path(__file__).parents[1]/'arbitro/validar-fluxo.py'))
pose=BASE['BASE']['pose'];angulo=BASE['BASE']['angulo'];diferenca=BASE['BASE']['diferenca']


class Sonda(BASE['Sonda']):
    def __init__(self):
        self.trajeto=[];self.navegacao=None;self.planos=[]
        super().__init__();self.destroy_publisher(self.autonomo)
        qos=QoSProfile(depth=1,reliability=ReliabilityPolicy.RELIABLE,durability=DurabilityPolicy.TRANSIENT_LOCAL)
        self.assinaturas.extend([
            self.create_subscription(LaserScan,'/scan',lambda m:self.receber('/scan',m),qos_profile_sensor_data),
            self.create_subscription(OccupancyGrid,'/map',lambda m:self.receber('/map',m),qos),
            self.create_subscription(String,'/navegacao/estado',self.estado_navegacao,qos),
            self.create_subscription(Caminho,'/plan',self.plano,10),
        ])
        self.cliente=ActionClient(self,NavigateToPose,'/navigate_to_pose')
    def receber(self,topico,m):
        super().receber(topico,m)
        if topico=='/simulacao/referencia':
            x,y,a=pose(m);self.trajeto.append([time.monotonic(),m.header.stamp.sec+m.header.stamp.nanosec*1e-9,x,y,a])
    def estado_navegacao(self,m):self.navegacao=json.loads(m.data)
    def plano(self,m):
        if m.poses:self.planos.append({'instante':time.monotonic(),'frame':m.header.frame_id,'pontos':[[p.pose.position.x,p.pose.position.y] for p in m.poses]})
    def global_(self):
        t=self.buffer.lookup_transform('map','base_footprint',Time()).transform
        return t.translation.x,t.translation.y,angulo(t.rotation)
    def chamar(self,tipo,nome,requisicao,prazo=15.):
        c=self.create_client(tipo,nome)
        try:
            assert c.wait_for_service(timeout_sec=prazo),nome
            f=c.call_async(requisicao);self.esperar(f.done,prazo=prazo);return f.result()
        finally:self.destroy_client(c)
    def modo(self,automatico):
        resposta=super().modo(automatico)
        if automatico:
            self.esperar(lambda:self.navegacao is not None and self.navegacao.get('aceita_objetivo') and self.navegacao.get('geracao')==self.estado.get('geracao'),prazo=15.)
        return resposta
    def objetivo(self,alvo):
        self.esperar(lambda:self.navegacao is not None and self.navegacao.get('aceita_objetivo'),prazo=15.)
        self.esperar(self.cliente.server_is_ready,prazo=15.)
        m=NavigateToPose.Goal();m.pose.header.frame_id='map';m.pose.header.stamp=self.get_clock().now().to_msg()
        m.pose.pose.position.x=float(alvo[0]);m.pose.pose.position.y=float(alvo[1])
        m.pose.pose.orientation.z=math.sin(alvo[2]/2);m.pose.pose.orientation.w=math.cos(alvo[2]/2)
        f=self.cliente.send_goal_async(m);self.esperar(f.done,prazo=10.);g=f.result();assert g.accepted
        return g,g.get_result_async()
    def aguardar_resultado(self,f,prazo=100.):
        self.esperar(f.done,prazo=prazo);return f.result()
    def em_movimento(self):
        m=self.ultimas.get('/cmd_vel')
        return m is not None and (abs(m.twist.linear.x)>.03 or abs(m.twist.angular.z)>.1)


def grafo(s):
    s.esperar(lambda:s.estado is not None and s.contagens['/map']>0 and s.contagens['/scan']>10 and s.contagens['/odom']>10 and s.contagens['/simulacao/referencia']>10,prazo=40.)
    s.esperar(lambda:s.buffer.can_transform('map','base_footprint',Time()),prazo=15.)
    assert s.estado['modo']=='manual',s.estado
    assert math.hypot(*pose(s.ultimas['/simulacao/referencia'])[:2])<.005
    estados={}
    for nome in ['slam_toolbox','planner_server','controller_server','behavior_server','bt_navigator']:
        cliente=s.create_client(GetState,f'/{nome}/get_state')
        try:
            assert cliente.wait_for_service(timeout_sec=20.),nome
            limite=time.monotonic()+25.
            while True:
                f=cliente.call_async(GetState.Request());s.esperar(f.done,prazo=5.)
                e=f.result().current_state
                if e.id==3:break
                assert time.monotonic()<limite,(nome,e.id,e.label,s.navegacao)
                s.girar(.1)
            estados[nome]=e.label
        finally:s.destroy_client(cliente)
    for topico,autores in [('/cmd_vel',{'arbitro'}),('/cmd_vel_autonomo',{'protecao_autonomia'}),('/map',{'slam_toolbox'})]:
        s.esperar(lambda t=topico,a=autores:{x.node_name for x in s.get_publishers_info_by_topic(t)}==a,prazo=10.)
    origens={x.node_name for x in s.get_publishers_info_by_topic('/cmd_vel_nav2')}
    assert 'controller_server' in origens and origens<={'controller_server','behavior_server'},origens
    for nome in ['slam_toolbox','planner_server','controller_server','bt_navigator','protecao_autonomia']:
        assert '/simulacao/referencia' not in {t for t,_ in s.get_subscriber_names_and_types_by_node(nome,'/')},nome
    assert s.count_publishers('/clock')==1
    s.girar(1.)
    return {'lifecycle':estados,'saida_final_exclusiva':'arbitro','fontes_velocidade_nav2':sorted(origens),'ground_truth_fora_dos_consumidores_autonomos':True}


def ir(s,alvo,pasta,indice):
    inicio=time.monotonic();n=len(s.trajeto);np=len(s.planos)
    g,f=s.objetivo(alvo);res=s.aguardar_resultado(f,100.)
    assert res.status==GoalStatus.STATUS_SUCCEEDED,(res.status,res.result,s.navegacao,s.estado)
    s.esperar(s.parada,prazo=3.);s.girar(.35)
    estimada=s.global_();real=pose(s.ultimas['/simulacao/referencia'])
    e_estimado=math.dist(estimada[:2],alvo[:2]);e_real=math.dist(real[:2],alvo[:2])
    assert e_estimado<.14,(estimada,alvo)
    assert e_real<.25,(real,alvo,estimada)
    assert abs(diferenca(estimada[2],alvo[2]))<.23,(estimada,alvo)
    assert math.dist(real[:2],estimada[:2])<.20
    planos=s.planos[np:];assert planos and all(p['frame']=='map' for p in planos)
    (pasta/f'planos-{indice}.json').write_text(json.dumps(planos)+'\n')
    return {'alvo':alvo,'status':res.status,'error_code':res.result.error_code,'pose_estimada':estimada,'pose_oraculo':real,
            'erro_estimado_m':e_estimado,'erro_real_m':e_real,'duracao_parede_s':time.monotonic()-inicio,
            'amostras_movimento':len(s.trajeto)-n,'planos_reais_nav2':len(planos)}


def cancelar(s,g,f):
    c=g.cancel_goal_async();s.esperar(c.done,prazo=8.);assert c.result().goals_canceling
    res=s.aguardar_resultado(f,10.);assert res.status==GoalStatus.STATUS_CANCELED,res.status
    s.esperar(lambda:s.zero() and s.parada(),prazo=3.)
    s.girar(.5);assert s.zero() and s.parada()


def pid_proprio(executavel):
    alvos=[]
    for f in Path('/proc').glob('[0-9]*/cmdline'):
        try:args=f.read_bytes().split(b'\0')
        except OSError:continue
        if executavel.encode() in args:alvos.append(int(f.parent.name))
    assert len(alvos)==1,(executavel,alvos)
    return alvos[0]


def perda_dado(s,tipo,executavel):
    s.modo(True);s.girar(.15);g,f=s.objetivo((2.4,.5,0.));s.esperar(s.em_movimento,prazo=15.)
    pid=pid_proprio(executavel);antes=time.monotonic();origem=pose(s.ultimas['/simulacao/referencia'])
    os.kill(pid,signal.SIGSTOP)
    try:
        s.esperar(lambda:s.estado['modo']=='parado' and s.zero(),prazo=3.)
        latencia=time.monotonic()-antes;assert latencia<1.8,(tipo,latencia,s.navegacao)
        res=s.aguardar_resultado(f,10.);assert res.status==GoalStatus.STATUS_CANCELED,(tipo,res.status)
        s.girar(.3)
    finally:os.kill(pid,signal.SIGCONT)
    s.girar(1.0);s.esperar(s.parada,prazo=3.)
    assert s.estado['modo']=='parado' and s.zero(),(tipo,s.estado)
    real=pose(s.ultimas['/simulacao/referencia']);distancia=math.dist(origem[:2],real[:2]);assert distancia<.3,(tipo,distancia)
    s.modo(True);s.girar(.5);assert s.zero(),'Recuperação/rearme retomou objetivo antigo'
    return {'dado':tipo,'latencia_parada_s':latencia,'deslocamento_ate_parar_m':distancia,'objetivo_cancelado':True,'recuperacao_sem_retomada_automatica':True}


def ensaiar(s,pasta,reinicio):
    resultado=grafo(s)
    s.modo(True);s.girar(.15)
    if reinicio:
        # Exercita o entry point público real, não só o ActionClient do ensaio.
        with (pasta/'cliente-publico.log').open('w') as saida:
            cli=subprocess.Popen(['ros2','run','navegacao_autonoma','ir_para','--x','.6','--y','.15','--prazo','70'],stdout=saida,stderr=subprocess.STDOUT)
            try:s.esperar(lambda:cli.poll() is not None,prazo=80.)
            finally:
                if cli.poll() is None:cli.send_signal(signal.SIGINT);cli.wait(timeout=8.)
        assert cli.returncode==0,(pasta/'cliente-publico.log').read_text()
        s.esperar(s.parada,prazo=3.)
        assert math.dist(s.global_()[:2],(.6,.15))<.14
        assert math.dist(pose(s.ultimas['/simulacao/referencia'])[:2],(.6,.15))<.25
        resultado['cliente_publico_ir_para_exercitado']=True
        resultado['reinicio_manual_sem_objetivos_antigos']=True
        return resultado
    # Expande o mapa por condução MANUAL curta em área livre; não é comando autônomo sintético.
    # O mapa continua vindo exclusivamente de scans e TF odométrico.
    s.modo(False);s.girar(.12)
    for _ in range(4):
        s.dirigir(.20,0.,4.8);s.dirigir(0.,.6,math.pi/(2*.6))
    s.dirigir(0.,0.,.25);s.esperar(s.parada,prazo=3.);s.girar(1.)
    s.modo(True);s.girar(.15)
    resultado['objetivos']=[ir(s,alvo,pasta,i) for i,alvo in enumerate([(-2.,1.4,0.),(2.8,2.4,0.),(0.,0.,0.)])]
    mundo=yaml.safe_load((Path(get_package_share_directory('lidar_simulado'))/'configuracao/mundo.yaml').read_text())
    resultado['reta_para_primeiro_alvo']=analisar_percurso([(0.,0.),(-2.,1.4)],mundo['segmentos'],.18)
    assert not resultado['reta_para_primeiro_alvo']['sem_interseccao_com_envoltoria'],'Cenário não exige desvio'
    # Cancelamento explícito durante execução.
    g,f=s.objetivo((2.4,.5,0.));s.esperar(s.em_movimento,prazo=15.);cancelar(s,g,f)
    resultado['cancelamento_em_movimento']=True
    # Tomada manual cancela ação; retornar ao auto não ressuscita o objetivo.
    g,f=s.objetivo((2.4,.5,0.));s.esperar(s.em_movimento,prazo=15.)
    s.modo(False);s.girar(.12);s.dirigir(-.08,0.,.65)
    assert abs(s.ultimas['/cmd_vel'].twist.linear.x+.08)<1e-8,s.ultimas['/cmd_vel']
    assert s.aguardar_resultado(f,8.).status==GoalStatus.STATUS_CANCELED
    s.girar(.6);s.esperar(s.parada,prazo=3.);s.modo(True);s.girar(.7);assert s.zero()
    resultado['manual_cancela_objetivo_sem_retomada_automatica']=True
    resultado['perdas_de_dados']=[perda_dado(s,tipo,exe) for tipo,exe in [
        ('scan','/work/install/lidar_simulado/lib/lidar_simulado/simular_lidar'),
        ('tf_global','/opt/ros/jazzy/lib/slam_toolbox/async_slam_toolbox_node'),
        ('odometria','/opt/ros/jazzy/lib/robot_localization/ekf_node'),
        ('clock','/work/install/simulador_base/lib/simulador_base/simular')]]
    # Objetivo impossível é ABORTED pelo Nav2, não sucesso baseado só em distância.
    s.modo(True);s.girar(.15);g,f=s.objetivo((20.,20.,0.));r=s.aguardar_resultado(f,35.)
    assert r.status==GoalStatus.STATUS_ABORTED,r.status
    s.esperar(lambda:s.zero() and s.parada(),prazo=3.);resultado['objetivo_fora_do_mapa_abortado']=True
    resultado['ultimo_error_code']=r.result.error_code
    return resultado


def argumentos_lancamento(modo,grafo):
    argumentos=['ros2','launch','navegacao_autonoma','navegacao_simulada.launch.py','rviz:=false','modo:='+modo]
    if grafo:argumentos.append('arquivo_grafo:='+grafo)
    return argumentos


def main():
    p=argparse.ArgumentParser();p.add_argument('saida');p.add_argument('--reinicio',action='store_true');p.add_argument('--modo',choices=['mapeamento','localizacao'],default='mapeamento');p.add_argument('--grafo',default='');o=p.parse_args()
    pasta=Path(o.saida);pasta.mkdir(parents=True,exist_ok=True)
    log=(pasta/'lancamento.log').open('w')
    proc=subprocess.Popen(argumentos_lancamento(o.modo,o.grafo),stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    rclpy.init();s=Sonda();resultado=None;falha_encerramento=None
    try:resultado=ensaiar(s,pasta,o.reinicio)
    except Exception:
        (pasta/'falha.txt').write_text(traceback.format_exc())
        (pasta/'estado-falha.json').write_text(json.dumps({'arbitro':s.estado,'navegacao':s.navegacao,'pose':pose(s.ultimas['/simulacao/referencia']) if '/simulacao/referencia' in s.ultimas else None},ensure_ascii=False,indent=2));raise
    finally:
        if proc.poll() is None and s.estado is not None and rclpy.ok():
            from navegacao_autonoma.encerrar import encerrar
            try:
                recibo=encerrar(s)
                (pasta/'encerramento-lifecycle.json').write_text(json.dumps(recibo,indent=2)+'\n')
            except (RuntimeError,TimeoutError) as erro:
                falha_encerramento=erro
                (pasta/'falha-encerramento.txt').write_text(str(erro))
        if resultado is not None:(pasta/'resultado-preliminar.json').write_text(json.dumps(resultado,ensure_ascii=False,indent=2)+'\n')
        (pasta/'trajeto.json').write_text(json.dumps(s.trajeto)+'\n')
        s.cliente.destroy();s.destroy_node()
        if rclpy.ok():rclpy.shutdown()
        if proc.poll() is None:proc.send_signal(signal.SIGINT)
        try:proc.wait(timeout=30)
        except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGTERM);proc.wait(timeout=8)
        log.close()
    assert falha_encerramento is None,str(falha_encerramento)
    assert proc.returncode==0,proc.returncode
    texto=(pasta/'lancamento.log').read_text();assert 'Traceback' not in texto and 'process has died' not in texto
    mundo=yaml.safe_load((Path(get_package_share_directory('lidar_simulado'))/'configuracao/mundo.yaml').read_text())
    pontos=[(p[2],p[3]) for p in s.trajeto]
    resultado['oraculo_contato']=analisar_percurso(pontos,mundo['segmentos'],.18)
    assert resultado['oraculo_contato']['sem_interseccao_com_envoltoria'],resultado['oraculo_contato']
    intervalos=[b[1]-a[1] for a,b in zip(s.trajeto,s.trajeto[1:])]
    assert max(intervalos)<.25,max(intervalos)
    resultado.update({'modo_slam':o.modo,'status':'OK','encerramento_limpo':True,'max_intervalo_amostras_ros_s':max(intervalos),
                      'limite':'Nav2/SLAM reais em ROS Jazzy AMD64, sensores/planta cinemáticos. Não é teste físico nem prova de segurança funcional.'})
    (pasta/'resultado.json').write_text(json.dumps(resultado,ensure_ascii=False,indent=2)+'\n');print(json.dumps(resultado,ensure_ascii=False))


if __name__=='__main__':main()
