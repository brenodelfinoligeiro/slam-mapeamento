"""Simulação Nav2; lifecycle SLAM nativo, Nav2 inicia após pré-requisitos."""
from pathlib import Path
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument,GroupAction,IncludeLaunchDescription,OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch.conditions import IfCondition
from launch_ros.actions import Node
from mapeamento_slam.validacao import parametros_do_modo


def compor(contexto):
    nav=Path(get_package_share_directory('navegacao_autonoma'))
    slam=Path(get_package_share_directory('mapeamento_slam'))
    base=Path(get_package_share_directory('navegacao_simulada'))
    modo=LaunchConfiguration('modo').perform(contexto)
    parametros=parametros_do_modo(modo,LaunchConfiguration('arquivo_grafo').perform(contexto))
    mundo=LaunchConfiguration('arquivo_mundo').perform(contexto) or str(Path(get_package_share_directory('lidar_simulado'))/'configuracao/mundo.yaml')
    if not Path(mundo).is_file():raise ValueError('Arquivo de mundo inexistente')
    tempo={'use_sim_time':True}
    nos=[GroupAction(scoped=True,actions=[IncludeLaunchDescription(
        PythonLaunchDescriptionSource(str(base/'inicializacao/simulacao.launch.py')),
        launch_arguments={'rviz':'false','origem_virtual':'false'}.items())]),
        Node(package='lidar_simulado',executable='simular_lidar',name='lidar_simulado',output='screen',parameters=[tempo,{'arquivo_mundo':mundo}]),
        Node(package='slam_toolbox',executable='async_slam_toolbox_node' if modo=='mapeamento' else 'localization_slam_toolbox_node',
             name='slam_toolbox',output='screen',parameters=[str(slam/'configuracao/slam.yaml'),parametros,tempo,{'use_lifecycle_manager': True}]),
        Node(package='nav2_map_server',executable='map_saver_server',name='salvador_mapa',output='screen',
             parameters=[tempo,{'save_map_timeout':2.,'map_subscribe_transient_local':True,'free_thresh_default':.196,'occupied_thresh_default':.65}]),
        Node(package='nav2_lifecycle_manager',executable='lifecycle_manager',name='lifecycle_slam_navegacao',output='screen',
             parameters=[tempo,{'autostart':True,'bond_timeout':4.,'attempt_respawn_reconnection':False,'node_names':['slam_toolbox','salvador_mapa']}]),
        GroupAction(scoped=True,actions=[IncludeLaunchDescription(
            PythonLaunchDescriptionSource(str(nav/'inicializacao/navegacao.launch.py')),launch_arguments={'use_sim_time':'true','arquivo_parametros':LaunchConfiguration('arquivo_parametros')}.items())]),
        Node(package='rviz2',executable='rviz2',name='rviz_navegacao',output='screen',parameters=[tempo],
             arguments=['-d',str(nav/'visualizacao/navegacao.rviz')],condition=IfCondition(LaunchConfiguration('rviz')))]
    for nome,pai,filho in [('laser_virtual','lidar_mount_link','laser_simulado'),('origem_cenario_slam','simulacao_mundo','map')]:
        nos.append(Node(package='tf2_ros',executable='static_transform_publisher',name=nome,output='screen',parameters=[tempo],
                        arguments=['--x','0','--y','0','--z','0','--roll','0','--pitch','0','--yaw','0','--frame-id',pai,'--child-frame-id',filho]))
    return nos


def generate_launch_description():
    return LaunchDescription([DeclareLaunchArgument('rviz',default_value='true'),
        DeclareLaunchArgument('modo',default_value='mapeamento'),DeclareLaunchArgument('arquivo_grafo',default_value=''),
        DeclareLaunchArgument('arquivo_mundo',default_value=''),DeclareLaunchArgument('arquivo_parametros',default_value=''),OpaqueFunction(function=compor)])
