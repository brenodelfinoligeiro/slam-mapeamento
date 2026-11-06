"""Visualização local: aqui os estados de juntas são exemplos, não telemetria."""
from pathlib import Path
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pasta = Path(get_package_share_directory('robo_movel'))
    modelo = (pasta / 'descricao/robo_movel.urdf').read_text(encoding='utf-8')
    tempo = ParameterValue(LaunchConfiguration('usar_tempo_simulado'), value_type=bool)
    return LaunchDescription([
        DeclareLaunchArgument('gui', default_value='true'),
        DeclareLaunchArgument('rviz', default_value='true'),
        DeclareLaunchArgument('usar_tempo_simulado', default_value='false'),
        IncludeLaunchDescription(PythonLaunchDescriptionSource(str(pasta / 'inicializacao/descricao.launch.py')),
             launch_arguments={'usar_tempo_simulado': LaunchConfiguration('usar_tempo_simulado')}.items()),
        Node(package='joint_state_publisher_gui', executable='joint_state_publisher_gui',
             name='joint_state_publisher_gui', condition=IfCondition(LaunchConfiguration('gui')),
             parameters=[{'robot_description': modelo, 'use_sim_time': tempo}]),
        Node(package='joint_state_publisher', executable='joint_state_publisher',
             name='joint_state_publisher', condition=UnlessCondition(LaunchConfiguration('gui')),
             parameters=[{'robot_description': modelo, 'use_sim_time': tempo}]),
        Node(package='rviz2', executable='rviz2', name='rviz2',
             condition=IfCondition(LaunchConfiguration('rviz')),
             arguments=['-d', str(pasta / 'visualizacao/robo_movel.rviz')],
             parameters=[{'use_sim_time': tempo}]),
    ])
