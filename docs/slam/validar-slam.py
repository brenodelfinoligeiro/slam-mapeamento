"""Ensaio ROS real de SLAM e recarga; não usar contra robô físico.

A referência perfeita só gera raios no simulador e serve ao oráculo deste teste.
O estimador recebe LaserScan e TF de odometria, nunca a pose perfeita.
"""
from pathlib import Path
import argparse, hashlib, json, math, os, re, runpy, signal, subprocess, time, traceback
import yaml
import rclpy
from rclpy.time import Time
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy, qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import OccupancyGrid
from lifecycle_msgs.srv import GetState
from nav2_msgs.srv import SaveMap as SalvarOcupacao
from ament_index_python.packages import get_package_share_directory
from metricas_mapa import analisar

BASE=runpy.run_path(str(Path(__file__).parents[1]/'simulacao/validar-fluxo.py'))
SondaBase=BASE['Sonda'];pose=BASE['pose'];angulo=BASE['angulo'];diferenca=BASE['diferenca']


class SondaSlam(SondaBase):
    def __init__(self):
        self.contagem_tf_mapa=0
        super().__init__()
        self.assinaturas.append(self.create_subscription(LaserScan,'/scan',lambda m:self.receber('/scan',m),qos_profile_sensor_data))
        qos=QoSProfile(depth=1,reliability=ReliabilityPolicy.RELIABLE,durability=DurabilityPolicy.TRANSIENT_LOCAL)
        self.assinaturas.append(self.create_subscription(OccupancyGrid,'/map',lambda m:self.receber('/map',m),qos))

    def receber_tf(self,mensagem):
        super().receber_tf(mensagem)
        for tf in mensagem.transforms:
            if tf.header.frame_id=='map' and tf.child_frame_id=='odom':self.contagem_tf_mapa+=1

    def comandar_tempo_simulado(self,linear,angular,duracao):
        inicio=self.get_clock().now().nanoseconds
        fim_parede=time.monotonic()+duracao*4+8
        proximo=0.
        while (self.get_clock().now().nanoseconds-inicio)*1e-9<duracao:
            if time.monotonic()>fim_parede:raise TimeoutError('Clock não avançou no percurso de ensaio')
            if time.monotonic()>=proximo:
                self.enviar(linear,angular);proximo=time.monotonic()+.05
            rclpy.spin_once(self,timeout_sec=.01)
        for _ in range(4):self.enviar(0.,0.);self.girar(.06)

    def estado_global(self):
        tf=self.buffer.lookup_transform('map','base_footprint',Time()).transform
        return tf.translation.x,tf.translation.y,angulo(tf.rotation)

    def grade(self):
        m=self.ultimas['/map'];p=m.info.origin
        return {'largura':m.info.width,'altura':m.info.height,'resolucao':m.info.resolution,
                'origem':[p.position.x,p.position.y,angulo(p.orientation)],'dados':list(m.data)}

    def chamar(self,cliente,requisicao,prazo=15.):
        assert cliente.wait_for_service(timeout_sec=prazo),'Serviço não disponível'
        futuro=cliente.call_async(requisicao)
        self.esperar(futuro.done,prazo=prazo)
        resultado=futuro.result()
        assert resultado is not None
        return resultado


def verificar_basico(sonda,modo):
    sonda.esperar(lambda:sonda.contagens['/scan']>10 and sonda.contagens['/map']>0 and sonda.contagem_tf_mapa>5 and sonda.contagens['/odom']>10,prazo=40.)
    sonda.esperar(lambda:sonda.buffer.can_transform('map','base_footprint',Time()) and sonda.buffer.can_transform('base_footprint','laser_simulado',Time()),prazo=12.)
    for topico,autor in [('/map','slam_toolbox'),('/scan','lidar_simulado')]:
        fontes={x.node_name for x in sonda.get_publishers_info_by_topic(topico)}
        assert fontes=={autor},(topico,fontes)
    assinaturas={t for t,_ in sonda.get_subscriber_names_and_types_by_node('slam_toolbox','/')}
    assert '/scan' in assinaturas and '/simulacao/referencia' not in assinaturas,assinaturas
    assert sonda.count_publishers('/clock')==1,[(p.node_name,p.node_namespace) for p in sonda.get_publishers_info_by_topic('/clock')]
    assert not any(n in {'planner_server','controller_server','bt_navigator','amcl'} for n in sonda.get_node_names())
    scan=sonda.ultimas['/scan'];assert scan.header.frame_id=='laser_simulado'
    assert len(scan.ranges)>=180 and scan.angle_increment>0
    validos=[v for v in scan.ranges if math.isfinite(v)]
    assert len(validos)>len(scan.ranges)*.7
    assert all(scan.range_min<=v<=scan.range_max for v in validos)
    assert abs(scan.angle_max-(scan.angle_min+(len(scan.ranges)-1)*scan.angle_increment))<1e-5
    cliente=sonda.create_client(GetState,'/slam_toolbox/get_state')
    estado=sonda.chamar(cliente,GetState.Request()).current_state
    assert estado.id==3,('Lifecycle não ativo',estado.id,estado.label)
    sonda.destroy_client(cliente)
    cliente=sonda.create_client(GetState,'/salvador_mapa/get_state')
    assert sonda.chamar(cliente,GetState.Request()).current_state.id==3
    sonda.destroy_client(cliente)
    esperado='localization_slam_toolbox_node' if modo=='localizacao' else 'async_slam_toolbox_node'
    processos=[]
    for cmdline in Path('/proc').glob('[0-9]*/cmdline'):
        try:args=cmdline.read_bytes().split(b'\0')
        except (OSError,ProcessLookupError):continue
        if args and args[0].decode(errors='replace')=='/opt/ros/jazzy/lib/slam_toolbox/'+esperado:processos.append(int(cmdline.parent.name))
    assert len(processos)==1,processos
    return processos[0]


def comparar(sonda,pasta):
    arquivo=Path(get_package_share_directory('lidar_simulado'))/'configuracao/mundo.yaml'
    mundo=yaml.safe_load(arquivo.read_text());grade=sonda.grade()
    metricas=analisar(grade,mundo['segmentos'],tolerancia=.15)
    assert metricas['celulas_ocupadas']>100 and metricas['celulas_livres']>500,metricas
    assert metricas['fracao_ocupados_proximos_parede']>.75,metricas
    assert metricas['fracao_parede_proxima_ocupado']>.60,metricas
    (pasta/'grade.json').write_text(json.dumps(grade)+'\n')
    estimada=sonda.estado_global();referencia=pose(sonda.ultimas['/simulacao/referencia'])
    erro={'posicao_m':math.hypot(estimada[0]-referencia[0],estimada[1]-referencia[1]),
          'orientacao_rad':abs(diferenca(estimada[2],referencia[2]))}
    assert erro['posicao_m']<.25 and erro['orientacao_rad']<.2,(erro,estimada,referencia)
    return {'mapa':metricas,'erro_pose':erro,'pose_estimada':estimada,'referencia_oraculo':referencia}


def ensaiar(sonda,pasta,modo,grafo):
    pid=verificar_basico(sonda,modo)
    if modo=='mapeamento':
        for _ in range(4):
            sonda.comandar_tempo_simulado(.20,0.,5.)
            sonda.comandar_tempo_simulado(0.,.60,math.pi/(2*.60))
    else:
        sonda.comandar_tempo_simulado(.16,0.,3.)
        sonda.comandar_tempo_simulado(-.16,0.,3.)
    sonda.enviar(0.,0.);sonda.girar(2.5)
    resultado=comparar(sonda,pasta)
    # Prova causal da aresta map->odom dentro deste namespace de PID isolado.
    comando=Path(f'/proc/{pid}/cmdline').read_bytes()
    assert b'/slam_toolbox/' in comando
    os.kill(pid,signal.SIGSTOP)
    try:
        sonda.girar(.25);antes=sonda.contagem_tf_mapa;odom_antes=len(sonda.marcas_tf)
        sonda.girar(.4)
        assert sonda.contagem_tf_mapa==antes
        assert len(sonda.marcas_tf)>odom_antes
    finally:os.kill(pid,signal.SIGCONT)
    sonda.esperar(lambda:sonda.contagem_tf_mapa>antes,prazo=8.)
    if modo=='mapeamento':
        grafo.parent.mkdir(parents=True,exist_ok=True)
        res=subprocess.run(['ros2','run','mapeamento_slam','salvar_mapa','--arquivo',str(grafo)],capture_output=True,text=True,timeout=60)
        (pasta/'salvar-console.log').write_text(res.stdout+'\n'+res.stderr)
        assert res.returncode==0,(res.stdout,res.stderr)
        cliente=sonda.create_client(SalvarOcupacao,'/salvador_mapa/save_map')
        try:
            for indice in range(3):
                req=SalvarOcupacao.Request();req.map_topic='/map'
                req.map_url=str(pasta/f'ocupacao-repetida-{indice}')
                req.image_format='pgm';req.map_mode='trinary'
                req.free_thresh=.196;req.occupied_thresh=.65
                assert sonda.chamar(cliente,req).result is True
                assert Path(req.map_url+'.pgm').stat().st_size>0
        finally:sonda.destroy_client(cliente)
        resultado['salvamentos_nativos_consecutivos']=3
    arquivos={}
    for extensao in ['.posegraph','.data','.pgm','.yaml']:
        arquivo=Path(str(grafo)+extensao)
        assert arquivo.is_file() and arquivo.stat().st_size>0,str(arquivo)
        arquivos[extensao]={'bytes':arquivo.stat().st_size,'sha256':hashlib.sha256(arquivo.read_bytes()).hexdigest()}
    metadados=yaml.safe_load(Path(str(grafo)+'.yaml').read_text())
    assert metadados['resolution']>0 and len(metadados['origin'])==3
    imagem=Path(metadados['image'])
    if not imagem.is_absolute():imagem=grafo.parent/imagem
    assert imagem.is_file()
    resultado.update({'modo':modo,'lifecycle_ativo':True,'fonte_mapa':'slam_toolbox',
        'fonte_scan':'lidar_simulado','referencia_perfeita_fora_das_entradas_slam':True,
        'tf_map_odom_autoria_causal':True,'arquivos_salvos_ou_carregados':arquivos,
        'limite':'Cenário e raios virtuais; não é medição física ou navegação autônoma.'})
    return resultado


def main():
    parser=argparse.ArgumentParser();parser.add_argument('saida');parser.add_argument('--modo',choices=['mapeamento','localizacao'],default='mapeamento');parser.add_argument('--grafo',required=True)
    opcoes=parser.parse_args();pasta=Path(opcoes.saida);pasta.mkdir(parents=True,exist_ok=True);grafo=Path(opcoes.grafo)
    anteriores={ext:hashlib.sha256(Path(str(grafo)+ext).read_bytes()).hexdigest() for ext in ['.posegraph','.data']} if opcoes.modo=='localizacao' else {}
    log=(pasta/'lancamento.log').open('w')
    argumentos=['ros2','launch','mapeamento_slam','slam_simulado.launch.py','rviz:=false','modo:='+opcoes.modo]
    if opcoes.modo=='localizacao':argumentos.append('arquivo_grafo:='+str(grafo))
    processo=subprocess.Popen(argumentos,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    rclpy.init();sonda=SondaSlam();resultado=None
    try:resultado=ensaiar(sonda,pasta,opcoes.modo,grafo)
    except Exception:
        (pasta/'falha.txt').write_text(traceback.format_exc());raise
    finally:
        sonda.destroy_node();rclpy.shutdown()
        if processo.poll() is None:processo.send_signal(signal.SIGINT)
        try:processo.wait(timeout=25)
        except subprocess.TimeoutExpired:os.killpg(processo.pid,signal.SIGTERM);processo.wait(timeout=8)
        log.close()
    assert processo.returncode==0,processo.returncode
    texto=(pasta/'lancamento.log').read_text()
    assert 'Traceback' not in texto and 'process has died' not in texto,texto
    if anteriores:
        assert all(hashlib.sha256(Path(str(grafo)+ext).read_bytes()).hexdigest()==digest for ext,digest in anteriores.items())
        resultado['grafo_original_preservado']=True
    resultado['status']='OK';resultado['encerramento_limpo']=True
    (pasta/'resultado.json').write_text(json.dumps(resultado,ensure_ascii=False,indent=2)+'\n');print(json.dumps(resultado,ensure_ascii=False))


if __name__=='__main__':main()
