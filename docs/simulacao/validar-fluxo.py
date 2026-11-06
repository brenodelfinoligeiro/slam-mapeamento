"""Exercita a simulação instalada com DDS real, teleop PTY e medições.

Executar apenas no contêiner isolado, depois do build e source install/setup.bash.
Não fornece referência perfeita ao estimador e não acessa hardware.
"""
from pathlib import Path
import argparse
from collections import defaultdict, deque
import json
import math
import os
import pty
import re
import signal
import subprocess
import time
import traceback

import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from rclpy.time import Time
from rclpy.qos import qos_profile_sensor_data
from geometry_msgs.msg import TwistStamped
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Imu, JointState
from rosgraph_msgs.msg import Clock
from tf2_msgs.msg import TFMessage
from tf2_ros import Buffer, TransformListener
from simulador_base.msg import LeituraRodas


def angulo(q):
    return math.atan2(2 * (q.w*q.z + q.x*q.y), 1 - 2*(q.y*q.y + q.z*q.z))


def diferenca(a, b):
    return math.atan2(math.sin(a-b), math.cos(a-b))


def pose(mensagem):
    p = mensagem.pose.pose
    return (p.position.x, p.position.y, angulo(p.orientation))


class Sonda(Node):
    def __init__(self):
        super().__init__('verificar_simulacao', parameter_overrides=[Parameter('use_sim_time', value=True)])
        self.ultimas = {}
        self.contagens = defaultdict(int)
        self.historico = defaultdict(lambda: deque(maxlen=10000))
        self.assinaturas = []
        self.marcas_tf = []
        self.quadros_tf = defaultdict(int)
        for topico, tipo in [('/odom', Odometry), ('/odometria/rodas', Odometry),
                             ('/simulacao/referencia', Odometry), ('/imu/data_raw', Imu),
                             ('/sensores/rodas', LeituraRodas), ('/joint_states', JointState),
                             ('/rodas/referencia', JointState), ('/cmd_vel', TwistStamped), ('/clock', Clock)]:
            self.assinaturas.append(self.create_subscription(tipo, topico, lambda m, t=topico: self.receber(t, m), qos_profile_sensor_data))
        self.assinaturas.append(self.create_subscription(TFMessage, '/tf', self.receber_tf, 100))
        self.publicador = self.create_publisher(TwistStamped, '/cmd_vel', 10)
        self.buffer = Buffer(node=self)
        self.ouvinte = TransformListener(self.buffer, self)

    def receber(self, topico, mensagem):
        self.ultimas[topico] = mensagem
        self.contagens[topico] += 1
        self.historico[topico].append((time.monotonic(), mensagem))

    def receber_tf(self, mensagem):
        for tf in mensagem.transforms:
            self.quadros_tf[tf.child_frame_id] += 1
            if tf.header.frame_id == 'odom' and tf.child_frame_id == 'base_footprint':
                self.marcas_tf.append(time.monotonic())

    def esperar(self, condicao, prazo=12.0):
        fim = time.monotonic()+prazo
        while time.monotonic()<fim:
            rclpy.spin_once(self, timeout_sec=.02)
            if condicao():
                return
        raise TimeoutError('Condição não atingida no prazo; contagens='+str(dict(self.contagens)))

    def girar(self, duracao):
        fim=time.monotonic()+duracao
        while time.monotonic()<fim:
            rclpy.spin_once(self, timeout_sec=.02)

    def enviar(self, linear=0., angular=0., atraso=0.):
        mensagem=TwistStamped()
        nanos=self.get_clock().now().nanoseconds-int(atraso*1e9)
        mensagem.header.stamp.sec=nanos//1000000000
        mensagem.header.stamp.nanosec=nanos%1000000000
        mensagem.header.frame_id='base_footprint'
        mensagem.twist.linear.x=linear
        mensagem.twist.angular.z=angular
        self.publicador.publish(mensagem)

    def dirigir(self, linear, angular, duracao):
        fim=time.monotonic()+duracao
        proximo=0.
        while time.monotonic()<fim:
            if time.monotonic()>=proximo:
                self.enviar(linear,angular)
                proximo=time.monotonic()+.05
            rclpy.spin_once(self, timeout_sec=.01)

    def parada(self):
        referencia=self.ultimas['/simulacao/referencia'].twist.twist
        rodas=self.ultimas['/rodas/referencia'].velocity
        return abs(referencia.linear.x)<.02 and abs(referencia.angular.z)<.04 and all(abs(v)<1e-9 for v in rodas)


def teleop_por_teclas(sonda, pasta):
    mestre, escravo=pty.openpty()
    processo=subprocess.Popen(['ros2','run','teleoperacao','teclado','--ros-args','-p','use_sim_time:=true'],
                             stdin=escravo, stdout=escravo, stderr=escravo, start_new_session=True)
    os.close(escravo)
    os.set_blocking(mestre, False)
    saida=bytearray()
    def drenar():
        try:
            while True:
                trecho=os.read(mestre,4096)
                if not trecho:break
                saida.extend(trecho)
        except (BlockingIOError, OSError):
            pass
    def tecla(tecla, duracao):
        fim=time.monotonic()+duracao
        proxima=0.
        while time.monotonic()<fim:
            if processo.poll() is not None:
                raise RuntimeError('Teleop encerrou antes do ensaio: '+saida.decode(errors='replace'))
            if time.monotonic()>=proxima:
                os.write(mestre,tecla.encode())
                proxima=time.monotonic()+.08
            rclpy.spin_once(sonda,timeout_sec=.01)
            drenar()
    try:
        sonda.esperar(lambda:sonda.get_publishers_info_by_topic('/cmd_vel') and any(p.node_name=='teleoperacao_teclado' for p in sonda.get_publishers_info_by_topic('/cmd_vel')))
        sonda.girar(.5)
        inicial=pose(sonda.ultimas['/simulacao/referencia'])
        tecla('w',1.6)
        sonda.girar(.9)
        avancou=pose(sonda.ultimas['/simulacao/referencia'])
        assert math.hypot(avancou[0]-inicial[0],avancou[1]-inicial[1])>.07
        sonda.esperar(sonda.parada,prazo=3.)
        tecla('a',1.3)
        sonda.girar(.9)
        girou=pose(sonda.ultimas['/simulacao/referencia'])
        assert diferenca(girou[2],avancou[2])>.2
        sonda.esperar(sonda.parada,prazo=3.)
        tecla('s',1.3)
        tecla(' ',.15)
        sonda.girar(.9)
        voltou=pose(sonda.ultimas['/simulacao/referencia'])
        projecao=(voltou[0]-girou[0])*math.cos(girou[2])+(voltou[1]-girou[1])*math.sin(girou[2])
        assert projecao<-.05
        sonda.esperar(sonda.parada,prazo=3.)
        os.write(mestre,b'q')
        processo.wait(timeout=5)
        assert processo.returncode==0
        drenar()
        return {'avanco':True,'giro':True,'re':True,'espaco_para_parar':True,
                'soltar_tecla_expira':True,'saida_q_limpa':True,'terminal_real_pty':True}
    finally:
        if processo.poll() is None:
            os.killpg(processo.pid,signal.SIGINT)
            try:processo.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(processo.pid,signal.SIGTERM);processo.wait(timeout=5)
        drenar();os.close(mestre)
        (pasta/'teleop-pty.log').write_bytes(saida)


def ensaiar(sonda, pasta, reinicio=False) -> dict[str, object]:
    obrigatorios=['/odom','/odometria/rodas','/simulacao/referencia','/imu/data_raw','/sensores/rodas','/joint_states','/clock']
    sonda.esperar(lambda: all(sonda.contagens[t]>10 for t in obrigatorios) and sonda.get_clock().now().nanoseconds>0, prazo=25.)
    sonda.esperar(lambda:sonda.buffer.can_transform('odom','base_link',Time()),prazo=8.)
    assert sonda.buffer.can_transform('odom','simulacao_mundo',Time())
    assert not any('joint_state_publisher' in n for n in sonda.get_node_names())
    assert sonda.ultimas['/imu/data_raw'].orientation_covariance[0]==-1
    inicial=pose(sonda.ultimas['/simulacao/referencia'])
    assert math.hypot(inicial[0],inicial[1])<.005
    if reinicio:
        sonda.dirigir(.1,0.,1.)
        sonda.girar(.9)
        sonda.esperar(sonda.parada,prazo=3.)
        return {'reinicio_do_lancamento':True,'origem_reinicializada':True,'movimento_e_expiracao':True}
    teclado=teleop_por_teclas(sonda,pasta)
    sonda.dirigir(.18,0.,3.)
    recentes=[m.twist.twist.linear.x for t,m in sonda.historico['/simulacao/referencia'] if t>time.monotonic()-.5]
    velocidade_media=sum(recentes)/len(recentes)
    assert abs(velocidade_media-.18)<.02,('Velocidade não acompanhou comando',velocidade_media)
    sonda.dirigir(.16,.6,3.)
    sonda.dirigir(-.12,0.,1.5)
    sonda.girar(1.)
    sonda.esperar(sonda.parada,prazo=3.)
    estimada=pose(sonda.ultimas['/odom']); rodas=pose(sonda.ultimas['/odometria/rodas']); referencia=pose(sonda.ultimas['/simulacao/referencia'])
    def erro(p):
        return {'posicao_m':math.hypot(p[0]-referencia[0],p[1]-referencia[1]),'orientacao_rad':abs(diferenca(p[2],referencia[2]))}
    erros={'fusao':erro(estimada),'rodas':erro(rodas)}
    assert erros['fusao']['posicao_m']<.20,erros
    assert erros['fusao']['orientacao_rad']<.15,erros
    assert erros['fusao']['orientacao_rad']+.02<erros['rodas']['orientacao_rad'],erros
    for valor,atraso,nome in [(float('nan'),0.,'NaN'),(.1,10.,'antigo'),(.1,-10.,'futuro')]:
        sonda.dirigir(.1,0.,.5)
        sonda.enviar(valor,0.,atraso)
        sonda.girar(.9)
        sonda.esperar(sonda.parada,prazo=3.)
    carimbos=[m.clock.sec+m.clock.nanosec*1e-9 for _,m in sonda.historico['/clock']]
    assert all(a<=b for a,b in zip(carimbos,carimbos[1:]))
    autores={p.node_name for p in sonda.get_publishers_info_by_topic('/tf')}
    assert autores=={'robot_state_publisher','estimador_local'},autores
    # Jazzy não expõe publisher_gid no MessageInfo. Prova causal: suspender só
    # o EKF interrompe essa aresta, mas o RSP continua transmitindo rodas.
    texto=(pasta/'lancamento.log').read_text()
    correspondencia=re.search(r'\[ekf_node-\d+\]: process started with pid \[(\d+)\]',texto)
    assert correspondencia is not None, 'PID do EKF não localizado no log próprio'
    identificador=int(correspondencia.group(1))
    comando=Path(f'/proc/{identificador}/cmdline').read_bytes()
    assert b'/robot_localization/ekf_node' in comando and b'__node:=estimador_local' in comando
    os.kill(identificador,signal.SIGSTOP)
    try:
        sonda.girar(.25)
        antes=len(sonda.marcas_tf);rodas_antes=sonda.quadros_tf['left_wheel_link']
        sonda.girar(.4)
        assert len(sonda.marcas_tf)==antes
        assert sonda.quadros_tf['left_wheel_link']>rodas_antes
    finally:os.kill(identificador,signal.SIGCONT)
    sonda.esperar(lambda:len(sonda.marcas_tf)>antes,prazo=5.)
    assert all(math.isfinite(v) for topico in ['/odom','/odometria/rodas','/simulacao/referencia'] for v in pose(sonda.ultimas[topico]))
    return {'teleop':teclado,'erros_medidos':erros,'referencia':referencia,'estimada':estimada,
            'odometria_rodas':rodas,'expiracao_comando':True,'invalido_nan_antigo_futuro':True,
            'um_unico_dono_tf_odom':True,'autor_tf_odom':'estimador_local','clock_simulado_monotonico':True,'velocidade_reta_media_m_s':velocidade_media,
            'falha_injetada':'EKF suspenso por 0.65 s para confirmar autoria TF; avisos de taxa na retomada são esperados',
            'orientacao_imu_indisponivel':True,'contagens_topicos':dict(sonda.contagens),
            'limite':'Ensaio cinemático com sensores virtuais e parâmetros sintéticos; não comprova desempenho físico ou localização global.'}


def main():
    argumentos=argparse.ArgumentParser()
    argumentos.add_argument('saida')
    argumentos.add_argument('--reinicio',action='store_true')
    opcoes=argumentos.parse_args()
    pasta=Path(opcoes.saida);pasta.mkdir(parents=True,exist_ok=True)
    log=(pasta/'lancamento.log').open('w')
    processo=subprocess.Popen(['ros2','launch','navegacao_simulada','simulacao.launch.py','rviz:=false'],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    rclpy.init();sonda=Sonda();resultado=None
    try:
        resultado=ensaiar(sonda,pasta,opcoes.reinicio)
    except Exception:
        (pasta/'falha.txt').write_text(traceback.format_exc())
        raise
    finally:
        sonda.destroy_node();rclpy.shutdown()
        if processo.poll() is None:processo.send_signal(signal.SIGINT)
        try:processo.wait(timeout=20)
        except subprocess.TimeoutExpired:
            os.killpg(processo.pid,signal.SIGTERM);processo.wait(timeout=8)
        log.close()
    assert processo.returncode==0,('Encerramento do launch',processo.returncode)
    texto=(pasta/'lancamento.log').read_text()
    assert 'Traceback' not in texto and 'process has died' not in texto,texto
    resultado['status']='OK';resultado['encerramento_limpo']=True
    (pasta/'resultado.json').write_text(json.dumps(resultado,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(resultado,ensure_ascii=False))


if __name__=='__main__':
    main()
