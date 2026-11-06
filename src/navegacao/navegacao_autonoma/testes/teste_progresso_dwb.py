from pathlib import Path
import yaml
P=Path(__file__).parents[1]
def teste_seguidor_nao_depende_de_minimo_local_por_celula():
 c=yaml.safe_load((P/'configuracao/nav2.yaml').read_text())['controller_server']['ros__parameters']['FollowPath']
 assert c['plugin']=='nav2_regulated_pure_pursuit_controller::RegulatedPurePursuitController'
 assert c['use_collision_detection'] and c['stateful']
