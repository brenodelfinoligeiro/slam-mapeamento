"""Base existente + árbitro, sem Nav2; teclado externo requer TTY real."""
from pathlib import Path
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument,GroupAction,IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    base=Path(get_package_share_directory('navegacao_simulada'))
    # Teleop externo remapeia /cmd_vel para /cmd_vel_manual em TTY real.
    return LaunchDescription([DeclareLaunchArgument('rviz',default_value='false'),
        GroupAction(actions=[IncludeLaunchDescription(PythonLaunchDescriptionSource(str(base/'inicializacao/simulacao.launch.py')),
            launch_arguments={'rviz':LaunchConfiguration('rviz')}.items())],scoped=True),
        Node(package='arbitro',executable='arbitrar',name='arbitro',output='screen',parameters=[{'use_sim_time':True}])])
