"""Exercício digital ROS/DDS do árbitro; não executar contra hardware."""
from pathlib import Path
import argparse,json,math,os,pty,runpy,signal,subprocess,time,traceback
import rclpy
from rclpy.qos import QoSProfile,ReliabilityPolicy,DurabilityPolicy
from geometry_msgs.msg import TwistStamped
from std_msgs.msg import String
from std_srvs.srv import SetBool,Trigger

BASE=runpy.run_path(str(Path(__file__).parents[1]/'simulacao/validar-fluxo.py'))

class Sonda(BASE['Sonda']):
    def __init__(self):
        super().__init__()
        self.destroy_publisher(self.publicador)
        self.publicador=self.create_publisher(TwistStamped,'/cmd_vel_manual',10)
        self.autonomo=self.create_publisher(TwistStamped,'/cmd_vel_autonomo',10)
        self.estado=None
        qos=QoSProfile(depth=1,reliability=ReliabilityPolicy.RELIABLE,durability=DurabilityPolicy.TRANSIENT_LOCAL)
        self.assinaturas.append(self.create_subscription(String,'/arbitro/estado',self.receber_estado,qos))
    def receber_estado(self,m):self.estado=json.loads(m.data)
    def mensagem(self,v,w=0.):
        m=TwistStamped();m.header.stamp=self.get_clock().now().to_msg();m.header.frame_id='base_footprint'
        m.twist.linear.x=v;m.twist.angular.z=w;return m
    def emitir(self,duracao,manual=None,autonomo=None,fixo=None):
        fim=time.monotonic()+duracao;proximo=0.
        while time.monotonic()<fim:
            if time.monotonic()>=proximo:
                if manual is not None:self.publicador.publish(fixo or self.mensagem(manual))
                if autonomo is not None:self.autonomo.publish(self.mensagem(autonomo))
                proximo=time.monotonic()+.04
            rclpy.spin_once(self,timeout_sec=.01)
    def servico(self,tipo,nome,requisicao):
        cliente=self.create_client(tipo,nome)
        try:
            assert cliente.wait_for_service(timeout_sec=8.)
            futuro=cliente.call_async(requisicao);self.esperar(futuro.done,prazo=8.)
            resposta=futuro.result();assert resposta.success,resposta.message
            return resposta.message
        finally:self.destroy_client(cliente)
    def modo(self,automatico):
        return self.servico(SetBool,'/arbitro/automatico',SetBool.Request(data=automatico))
    def zero(self):
        m=self.ultimas.get('/cmd_vel')
        return m is not None and m.twist.linear.x==0. and m.twist.angular.z==0.


def teclado_real(s):
    mestre,escravo=pty.openpty()
    processo=subprocess.Popen(['ros2','run','teleoperacao','teclado','--ros-args','-p','use_sim_time:=true','-r','/cmd_vel:=/cmd_vel_manual'],stdin=escravo,stdout=escravo,stderr=escravo,start_new_session=True)
    os.close(escravo);os.set_blocking(mestre,False)
    def drenar():
        try:
            while os.read(mestre,4096):pass
        except (OSError,BlockingIOError):pass
    try:
        s.esperar(lambda:any(x.node_name=='teleoperacao_teclado' for x in s.get_publishers_info_by_topic('/cmd_vel_manual')))
        fim=time.monotonic()+.8
        while time.monotonic()<fim:
            os.write(mestre,b'w');s.girar(.06);drenar()
        assert s.ultimas['/cmd_vel'].twist.linear.x>0
        os.write(mestre,b' ');s.girar(.15);os.write(mestre,b'q')
        processo.wait(timeout=5);assert processo.returncode==0
        s.girar(.5);assert s.zero()
    finally:
        if processo.poll() is None:
            os.killpg(processo.pid,signal.SIGINT);processo.wait(timeout=5)
        drenar();os.close(mestre)


def ensaiar(s,reinicio):
    s.esperar(lambda:s.contagens['/odom']>10 and s.contagens['/simulacao/referencia']>10 and s.estado is not None,prazo=25.)
    s.esperar(lambda:{x.node_name for x in s.get_publishers_info_by_topic('/cmd_vel')}=={'arbitro'})
    assert s.estado['modo']=='manual'
    origem=BASE['pose'](s.ultimas['/simulacao/referencia'])
    assert math.hypot(origem[0],origem[1])<.005
    s.emitir(.35,autonomo=.2);assert s.zero()
    s.emitir(.65,manual=.15,autonomo=-.15)
    assert abs(s.ultimas['/cmd_vel'].twist.linear.x-.15)<1e-8
    assert BASE['pose'](s.ultimas['/simulacao/referencia'])[0]-origem[0]>.04
    if reinicio:return {'reinicio_completo_manual':True,'movimento_manual':True}
    # Mudança exige nova época; fila antiga não pode manter movimento.
    s.modo(True);s.girar(.12);assert s.zero()
    antes=BASE['pose'](s.ultimas['/simulacao/referencia'])[0]
    s.emitir(.85,manual=.25,autonomo=-.1)
    assert abs(s.ultimas['/cmd_vel'].twist.linear.x+.1)<1e-8
    assert BASE['pose'](s.ultimas['/simulacao/referencia'])[0]-antes<-.04
    s.emitir(.65,manual=.2);assert s.zero(),'Não pode haver fallback manual após expirar o autônomo'
    s.autonomo.publish(s.mensagem(float('nan')));s.girar(.1);assert s.zero()
    s.servico(Trigger,'/arbitro/parar',Trigger.Request())
    s.emitir(.25,manual=.2,autonomo=.2);assert s.zero() and s.estado['modo']=='parado'
    s.modo(False);s.girar(.08)
    fixo=s.mensagem(.1);s.emitir(.65,manual=.1,fixo=fixo);assert s.zero(),'Replay não pode renovar liveness'
    s.emitir(.3,manual=.1);assert not s.zero()
    # Timestamp exato, não roundtrip float no adaptador.
    entrada=s.mensagem(.12);s.publicador.publish(entrada)
    s.esperar(lambda:s.ultimas['/cmd_vel'].header.stamp==entrada.header.stamp and abs(s.ultimas['/cmd_vel'].twist.linear.x-.12)<1e-8)
    # Pausa apenas da planta própria no namespace PID privado. Watchdog deve parar sem /clock.
    alvos=[]
    for f in Path('/proc').glob('[0-9]*/cmdline'):
        try:argumentos=f.read_bytes().split(b'\0')
        except OSError:continue
        if b'/work/install/simulador_base/lib/simulador_base/simular' in argumentos:alvos.append(int(f.parent.name))
    assert len(alvos)==1,alvos
    os.kill(alvos[0],signal.SIGSTOP)
    try:s.girar(.55);assert s.zero(),'Watchdog dependeu indevidamente do clock ROS'
    finally:os.kill(alvos[0],signal.SIGCONT)
    s.girar(.2);s.emitir(.4,manual=.1);assert not s.zero()
    s.emitir(.65);s.esperar(s.parada,prazo=3.)
    teclado_real(s)
    return {'manual_e_autonomo_exclusivos':True,'sem_ultima_mensagem_vence':True,'sem_fallback_implicito':True,
        'troca_neutra':True,'parada_travada':True,'expiracao':True,'replay_nao_renova':True,'nan_rejeitado':True,
        'carimbo_inteiro_preservado':True,'watchdog_com_clock_pausado':True,'base_se_move_com_saida_arbitrada':True,'teclado_real_remapeado':True}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('saida');parser.add_argument('--reinicio',action='store_true');op=parser.parse_args()
    pasta=Path(op.saida);pasta.mkdir(parents=True,exist_ok=True);log=(pasta/'lancamento.log').open('w')
    processo=subprocess.Popen(['ros2','launch','arbitro','simulacao_arbitrada.launch.py','rviz:=false'],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    rclpy.init();s=Sonda();resultado=None
    try:resultado=ensaiar(s,op.reinicio)
    except Exception:(pasta/'falha.txt').write_text(traceback.format_exc());raise
    finally:
        s.destroy_node();rclpy.shutdown()
        if processo.poll() is None:processo.send_signal(signal.SIGINT)
        try:processo.wait(timeout=25)
        except subprocess.TimeoutExpired:os.killpg(processo.pid,signal.SIGTERM);processo.wait(timeout=8)
        log.close()
    assert processo.returncode==0
    texto=(pasta/'lancamento.log').read_text();assert 'Traceback' not in texto and 'process has died' not in texto,texto
    resultado.update({'status':'OK','encerramento_limpo':True,'limite':'Comandos autônomos são entradas sintéticas de teste; nenhum Nav2 ou hardware.'})
    (pasta/'resultado.json').write_text(json.dumps(resultado,ensure_ascii=False,indent=2)+'\n');print(json.dumps(resultado,ensure_ascii=False))

if __name__=='__main__':main()
