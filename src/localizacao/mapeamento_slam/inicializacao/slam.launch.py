"""SLAM sobre /scan e TF odom->base_footprint; não inicia sensores/controle."""
from pathlib import Path
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, EmitEvent, OpaqueFunction, RegisterEventHandler
from launch.conditions import IfCondition
from launch.events import matches_action
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import LifecycleNode, Node
from launch_ros.event_handlers import OnStateTransition
from launch_ros.events.lifecycle import ChangeState
from lifecycle_msgs.msg import Transition
from mapeamento_slam.validacao import parametros_do_modo


def configurar(contexto):
    modo = LaunchConfiguration('modo').perform(contexto)
    parametros = parametros_do_modo(modo, LaunchConfiguration('arquivo_grafo').perform(contexto))
    pasta = Path(get_package_share_directory('mapeamento_slam'))
    no = LifecycleNode(
        package='slam_toolbox', namespace='', name='slam_toolbox', output='screen',
        executable='async_slam_toolbox_node' if modo == 'mapeamento' else 'localization_slam_toolbox_node',
        parameters=[str(pasta / 'configuracao/slam.yaml'), parametros,
                    {'use_sim_time': True, 'use_lifecycle_manager': False}])
    # Mesmas transições do launch oficial Jazzy, registradas antes do configure.
    ativar = RegisterEventHandler(OnStateTransition(
        target_lifecycle_node=no, start_state='configuring', goal_state='inactive',
        entities=[EmitEvent(event=ChangeState(
            lifecycle_node_matcher=matches_action(no),
            transition_id=Transition.TRANSITION_ACTIVATE))]))
    configurar_no = EmitEvent(event=ChangeState(
        lifecycle_node_matcher=matches_action(no),
        transition_id=Transition.TRANSITION_CONFIGURE))
    # Componente nativo persistente: sem ros2 run/system() dentro do SLAM.
    salvador = LifecycleNode(
        package='nav2_map_server', executable='map_saver_server', namespace='',
        name='salvador_mapa', output='screen', parameters=[{
            'use_sim_time': True, 'save_map_timeout': 2.0,
            'map_subscribe_transient_local': True,
            'free_thresh_default': 0.196, 'occupied_thresh_default': 0.65}])
    ativar_salvador = RegisterEventHandler(OnStateTransition(
        target_lifecycle_node=salvador, start_state='configuring', goal_state='inactive',
        entities=[EmitEvent(event=ChangeState(
            lifecycle_node_matcher=matches_action(salvador),
            transition_id=Transition.TRANSITION_ACTIVATE))]))
    configurar_salvador = EmitEvent(event=ChangeState(
        lifecycle_node_matcher=matches_action(salvador),
        transition_id=Transition.TRANSITION_CONFIGURE))
    return [ativar, ativar_salvador, no, salvador, configurar_no, configurar_salvador,
            Node(package='rviz2', executable='rviz2', name='rviz_slam', output='screen',
                 parameters=[{'use_sim_time': True}],
                 arguments=['-d', str(pasta / 'visualizacao/slam.rviz')],
                 condition=IfCondition(LaunchConfiguration('rviz')))]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('rviz', default_value='true'),
        DeclareLaunchArgument('modo', default_value='mapeamento'),
        # Prefixo .posegraph + .data; localização exige ambos antes de iniciar nós.
        DeclareLaunchArgument('arquivo_grafo', default_value=''),
        OpaqueFunction(function=configurar),
    ])
