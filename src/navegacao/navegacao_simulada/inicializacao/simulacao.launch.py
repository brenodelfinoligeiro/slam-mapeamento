"""Simulação cinemática: sensores virtuais -> odometria/IMU -> EKF."""
from pathlib import Path
import yaml
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument,IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pasta=Path(get_package_share_directory('navegacao_simulada'))
    descricao=Path(get_package_share_directory('robo_movel'))
    fusao=Path(get_package_share_directory('fusao_sensores'))
    configuracao=yaml.safe_load((pasta/'configuracao/simulacao.yaml').read_text())
    geometria=configuracao['geometria']; tempo={'use_sim_time':True}
    def incluir(arquivo,argumentos=None):
        return IncludeLaunchDescription(PythonLaunchDescriptionSource(str(arquivo)),launch_arguments=(argumentos or {}).items())
    return LaunchDescription([
        DeclareLaunchArgument('rviz',default_value='true'),
        DeclareLaunchArgument('origem_virtual',default_value='true'),
        incluir(descricao/'inicializacao/descricao.launch.py',{'usar_tempo_simulado':'true'}),
        Node(package='simulador_base',executable='simular',name='simulador_base',output='screen',parameters=[tempo,geometria,configuracao['simulador']]),
        Node(package='comando_rodas',executable='converter_velocidade',name='comando_rodas',output='screen',parameters=[tempo,geometria,configuracao['comandos']]),
        Node(package='odometria_rodas',executable='calcular_odometria',name='odometria_rodas',output='screen',parameters=[tempo,geometria,configuracao['odometria']]),
        Node(package='processamento_imu',executable='tratar_imu',name='processamento_imu',output='screen',parameters=[tempo,configuracao['imu']]),
        incluir(fusao/'inicializacao/fusao.launch.py'),
        # Coincidência de origens definida apenas para o cenário virtual; não é medição.
        Node(package='tf2_ros',executable='static_transform_publisher',name='origem_virtual',
             condition=IfCondition(LaunchConfiguration('origem_virtual')),
             output='screen',parameters=[tempo],arguments=['--x','0','--y','0','--z','0','--roll','0','--pitch','0','--yaw','0',
                 '--frame-id','simulacao_mundo','--child-frame-id','odom']),
        Node(package='navegacao_simulada',executable='trajetorias',name='trajetorias',output='screen',parameters=[tempo]),
        Node(package='rviz2',executable='rviz2',name='rviz2',output='screen',parameters=[tempo],
             arguments=['-d',str(pasta/'visualizacao/simulacao.rviz')],condition=IfCondition(LaunchConfiguration('rviz'))),
    ])
