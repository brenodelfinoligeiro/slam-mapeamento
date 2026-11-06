"""Estima pose relativa usando somente odometria e giroscópio."""
from pathlib import Path
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    pasta=Path(get_package_share_directory('fusao_sensores'))
    return LaunchDescription([Node(package='robot_localization',executable='ekf_node',name='estimador_local',
        output='screen',parameters=[str(pasta/'configuracao/estimador.yaml')],
        remappings=[('odometry/filtered','/odom')])])
