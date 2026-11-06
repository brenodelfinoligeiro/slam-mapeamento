"""Nav2 modular; exige mapa/scan/odom/TF externos. Não inicia hardware."""
from pathlib import Path
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument,OpaqueFunction,RegisterEventHandler,EmitEvent
from launch.event_handlers import OnProcessExit
from launch.events import Shutdown
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def compor(contexto):
    pasta=Path(get_package_share_directory('navegacao_autonoma'))
    arquivo=LaunchConfiguration('arquivo_parametros').perform(contexto) or str(pasta/'configuracao/nav2.yaml')
    if not Path(arquivo).is_file():raise ValueError('Arquivo de parâmetros Nav2 inexistente')
    tempo={'use_sim_time':ParameterValue(LaunchConfiguration('use_sim_time'),value_type=bool)}
    nos=[]
    for pacote,nome in [('nav2_planner','planner_server'),('nav2_controller','controller_server'),('nav2_behaviors','behavior_server'),('nav2_bt_navigator','bt_navigator')]:
        extras={'default_nav_to_pose_bt_xml':str(pasta/'configuracao/ir_para.xml')} if nome=='bt_navigator' else {}
        nos.append(Node(package=pacote,executable=nome,name=nome,output='screen',parameters=[arquivo,tempo,extras],
                        remappings=[('cmd_vel','/cmd_vel_nav2')]))
    nos.extend([
        Node(package='nav2_lifecycle_manager',executable='lifecycle_manager',name='lifecycle_navegacao',output='screen',
             parameters=[tempo,{'autostart':False,'bond_timeout':4.0,'attempt_respawn_reconnection':False,
                               'node_names':['controller_server','planner_server','behavior_server','bt_navigator']}]),
        Node(package='arbitro',executable='arbitrar',name='arbitro',output='screen',parameters=[tempo]),
        Node(package='navegacao_autonoma',executable='proteger',name='protecao_autonomia',output='screen',parameters=[tempo]),
    ])
    inicializador=Node(package='navegacao_autonoma',executable='inicializar',name='inicializar_navegacao',output='screen',parameters=[tempo])
    def terminou(evento,contexto):
        return [] if evento.returncode==0 else [EmitEvent(event=Shutdown(reason='Inicialização Nav2 falhou; composição encerrada'))]
    nos.extend([RegisterEventHandler(OnProcessExit(target_action=inicializador,on_exit=terminou)),inicializador])
    return nos


def generate_launch_description():
    return LaunchDescription([DeclareLaunchArgument('use_sim_time',default_value='false'),
        DeclareLaunchArgument('arquivo_parametros',default_value=''),OpaqueFunction(function=compor)])
