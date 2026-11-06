"""Publica a descrição e TFs; estados das rodas devem vir da fonte real."""
from pathlib import Path
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pasta = Path(get_package_share_directory('robo_movel'))
    modelo = (pasta / 'descricao/robo_movel.urdf').read_text(encoding='utf-8')
    return LaunchDescription([
        DeclareLaunchArgument('usar_tempo_simulado', default_value='false'),
        Node(package='robot_state_publisher', executable='robot_state_publisher',
             name='robot_state_publisher', output='screen',
             parameters=[{'robot_description': modelo,
                          'use_sim_time': ParameterValue(LaunchConfiguration('usar_tempo_simulado'), value_type=bool)}]),
    ])
