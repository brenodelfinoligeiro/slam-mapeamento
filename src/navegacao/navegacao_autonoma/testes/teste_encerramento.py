import ast
from pathlib import Path
P=Path(__file__).parents[1]
def teste_encerramento_lifecycle_antes_de_invalidar_contextos():
 f=P/'navegacao_autonoma/encerrar.py';assert f.is_file();t=f.read_text();ast.parse(t)
 assert '/arbitro/parar' in t and 'SHUTDOWN' in t
 assert t.index('/lifecycle_navegacao/manage_nodes')<t.index('/lifecycle_slam_navegacao/manage_nodes')
 assert 'success is not True' in t
 assert 'encerrar = navegacao_autonoma.encerrar:main' in (P/'setup.py').read_text()
