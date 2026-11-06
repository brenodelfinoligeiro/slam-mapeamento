from pathlib import Path
P=Path(__file__).parents[1]
def teste_nav2_nao_arranca_antes_dos_dados():
 t=(P/'inicializacao/navegacao.launch.py').read_text()
 assert "'autostart':False" in t and "executable='inicializar'" in t
 t=(P/'navegacao_autonoma/inicializar.py').read_text()
 assert '/navegacao/estado' in t and 'ManageLifecycleNodes' in t and 'monotonic' in t
 assert "get('pronto')" in t and 'STARTUP' in t

def teste_slam_com_um_unico_dono_nativo_de_lifecycle():
 t=(P/'inicializacao/navegacao_simulada.launch.py').read_text()
 assert 'lifecycle_slam_navegacao' in t and 'slam_simulado.launch.py' not in t
 assert "'use_lifecycle_manager': True" in t
