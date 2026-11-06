"""Ensaio ROS real isolado: RSP sem juntas fictícias; depois JointState de teste.
Uso no ambiente ROS instalado: python3 validar-tf.py PASTA_RESULTADOS
"""
from pathlib import Path
import sys,subprocess,signal,time,json,math,os
import xml.etree.ElementTree as ET
import rclpy
from rclpy.node import Node
from rclpy.time import Time
from rclpy.qos import QoSProfile,ReliabilityPolicy,DurabilityPolicy
from sensor_msgs.msg import JointState
from std_msgs.msg import String
from tf2_ros import Buffer,TransformListener
from ament_index_python.packages import get_package_share_directory
OUT=Path(sys.argv[1]);OUT.mkdir(parents=True,exist_ok=True);share=Path(get_package_share_directory('slamderson'));meta=json.loads((share/'descricao/origem-cad.json').read_text())
log=(OUT/'robot-state-publisher.log').open('w');proc=subprocess.Popen(['ros2','launch','slamderson','descricao.launch.py'],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
rclpy.init();node=Node('verificar_descricao_r05');buf=Buffer();listener=TransformListener(buf,node);texts=[]
qos=QoSProfile(depth=1,reliability=ReliabilityPolicy.RELIABLE,durability=DurabilityPolicy.TRANSIENT_LOCAL)
sub=node.create_subscription(String,'/robot_description',lambda x:texts.append(x.data),qos)
def aguardar(cond,timeout=15):
 end=time.monotonic()+timeout
 while time.monotonic()<end:
  if proc.poll() is not None:raise RuntimeError('robot_state_publisher terminou: '+str(proc.returncode))
  rclpy.spin_once(node,timeout_sec=.1)
  if cond():return
 raise TimeoutError('TF/robot_description não chegaram no prazo')
try:
 aguardar(lambda:bool(texts) and buf.can_transform('base_footprint','imu_mount_link',Time()) and buf.can_transform('base_footprint','lidar_mount_link',Time()))
 assert len(ET.fromstring(texts[-1]).findall('link'))==7
 assert texts[-1]==(share/'descricao/slamderson.urdf').read_text()
 assert not buf.can_transform('base_link','left_wheel_link',Time()),'Fonte fictícia de rodas indevida'
 assert not any('joint_state_publisher' in n for n in node.get_node_names())
 states=node.create_publisher(JointState,'/joint_states',10);angles={'left_wheel_joint':.4,'right_wheel_joint':-.2}
 for _ in range(20):
  msg=JointState();msg.header.stamp=node.get_clock().now().to_msg();msg.name=list(angles);msg.position=list(angles.values());states.publish(msg);rclpy.spin_once(node,timeout_sec=.1)
 aguardar(lambda:buf.can_transform('base_link','left_wheel_link',Time()) and buf.can_transform('base_link','right_wheel_link',Time()))
 transforms=[]
 for side in ('left','right'):
  child=side+'_wheel_link';tf=buf.lookup_transform('base_link',child,Time()).transform;xyz=[tf.translation.x,tf.translation.y,tf.translation.z];quat=[tf.rotation.x,tf.rotation.y,tf.rotation.z,tf.rotation.w];angle=angles[side+'_wheel_joint']
  expected=[0,math.sin(angle/2),0,math.cos(angle/2)]
  assert all(abs(a-b)<1e-9 for a,b in zip(quat,expected)),(child,quat)
  assert all(abs(a-b)<1e-9 for a,b in zip(xyz,meta['frames_ROS_relativos_base_m'][child]))
  transforms.append({'filho':child,'xyz_m':xyz,'quaternion_xyzw':quat,'angulo_teste_rad':angle})
 report={'status':'OK','ROS_DISTRO':os.environ.get('ROS_DISTRO'),'robot_description_recebido':True,'links':7,'sem_juntas_ficticias_no_launch_de_descricao':True,'TFs_rodas':transforms,'limites':'ROS isolado sem rede/hardware; JointState publicado apenas pelo teste. Sem dados reais de sensores/motores.'}
 (OUT/'validacao-tf.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
finally:
 node.destroy_node();rclpy.shutdown()
 if proc.poll() is None:proc.send_signal(signal.SIGINT)
 try:proc.wait(timeout=12)
 except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGTERM);proc.wait(timeout=5)
 log.close()
