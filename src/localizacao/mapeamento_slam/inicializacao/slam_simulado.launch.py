"""Cenário virtual + LiDAR + SLAM; não inicia navegação autônoma."""
from pathlib import Path
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction, IncludeLaunchDescription, OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from mapeamento_slam.validacao import parametros_do_modo


def compor(contexto):
    parametros_do_modo(LaunchConfiguration('modo').perform(contexto),
                      LaunchConfiguration('arquivo_grafo').perform(contexto))
    pasta = Path(get_package_share_directory('mapeamento_slam'))
    simulacao = Path(get_package_share_directory('navegacao_simulada'))
    mundo = LaunchConfiguration('arquivo_mundo').perform(contexto)
    if not mundo:
        mundo = str(Path(get_package_share_directory('lidar_simulado')) / 'configuracao/mundo.yaml')
    if not Path(mundo).is_file():
        raise ValueError(f'arquivo_mundo não encontrado: {mundo}')
    tempo = {'use_sim_time': True}
    return [
        # Escopo impede o rviz:=false da base de apagar a escolha do SLAM.
        GroupAction(actions=[IncludeLaunchDescription(
            PythonLaunchDescriptionSource(str(simulacao / 'inicializacao/simulacao.launch.py')),
            launch_arguments={'rviz': 'false', 'origem_virtual': 'false'}.items())], scoped=True),
        Node(package='lidar_simulado', executable='simular_lidar', name='lidar_simulado',
             output='screen', parameters=[tempo, {'arquivo_mundo': mundo}]),
        # Identidade VIRTUAL do dado laser; não representa calibração do C1 físico.
        Node(package='tf2_ros', executable='static_transform_publisher', name='laser_virtual',
             parameters=[tempo], arguments=['--x', '0', '--y', '0', '--z', '0',
                 '--roll', '0', '--pitch', '0', '--yaw', '0',
                 '--frame-id', 'lidar_mount_link', '--child-frame-id', 'laser_simulado']),
        # Coincidência de origens DO cenário, só para visualizar ground truth.
        # Nenhuma pose do simulador alimenta o estimador do SLAM.
        Node(package='tf2_ros', executable='static_transform_publisher', name='origem_cenario_slam',
             parameters=[tempo], arguments=['--x', '0', '--y', '0', '--z', '0',
                 '--roll', '0', '--pitch', '0', '--yaw', '0',
                 '--frame-id', 'simulacao_mundo', '--child-frame-id', 'map']),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(str(pasta / 'inicializacao/slam.launch.py')),
            launch_arguments={nome: LaunchConfiguration(nome)
                              for nome in ('rviz', 'modo', 'arquivo_grafo')}.items()),
    ]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('rviz', default_value='true'),
        DeclareLaunchArgument('modo', default_value='mapeamento'),
        DeclareLaunchArgument('arquivo_grafo', default_value=''),
        DeclareLaunchArgument('arquivo_mundo', default_value=''),
        OpaqueFunction(function=compor),
    ])
