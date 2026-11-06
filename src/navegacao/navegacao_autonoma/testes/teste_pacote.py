from pathlib import Path
import ast,xml.etree.ElementTree as ET
P=Path(__file__).parents[1]
def teste_manifesto_e_dependencias():
 r=ET.parse(P/'package.xml').getroot();assert r.findtext('name')=='navegacao_autonoma'
 ds={e.text for e in r.findall('exec_depend')}
 assert {'arbitro','nav2_planner','nav2_controller','nav2_bt_navigator','nav2_behaviors','nav2_lifecycle_manager','nav2_navfn_planner','nav2_regulated_pure_pursuit_controller','tf2_ros_py','action_msgs'}<=ds
 assert r.findtext('export/build_type')=='ament_python'
def teste_recursos_composicao_e_cli():
 assert (P/'recursos/navegacao_autonoma').is_file()
 s=(P/'setup.py').read_text();assert 'proteger = navegacao_autonoma.no_protecao:main' in s and 'ir_para = navegacao_autonoma.ir_para:main' in s
 for rel in ['inicializacao/navegacao.launch.py','inicializacao/navegacao_simulada.launch.py','navegacao_autonoma/ir_para.py']:
  ast.parse((P/rel).read_text())
 c=(P/'inicializacao/navegacao.launch.py').read_text()
 for nome in ['planner_server','controller_server','behavior_server','bt_navigator','/cmd_vel_nav2','arbitro','proteger']:assert nome in c
 assert (P/'inicializacao/navegacao_simulada.launch.py').read_text().count('GroupAction')>=2
