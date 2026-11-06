import ast
from pathlib import Path

def extrair():
 p=Path(__file__).parents[1]/'validar-navegacao.py'
 r=ast.parse(p.read_text());f=next((n for n in r.body if isinstance(n,ast.FunctionDef) and n.name=='argumentos_lancamento'),None)
 assert f is not None,'Extrair montagem dos argumentos para testar contrato do CLI ros2 launch'
 escopo={};exec(compile(ast.Module(body=[f],type_ignores=[]),str(p),'exec'),escopo)
 return escopo['argumentos_lancamento']

def teste_launch_nao_recebe_atribuicao_vazia():
 montar=extrair();a=montar('mapeamento','')
 assert not any(v.endswith(':=') for v in a)
 b=montar('localizacao','/workspace/docs/slam/mapas/ensaio')
 assert 'arquivo_grafo:=/workspace/docs/slam/mapas/ensaio' in b


def teste_helper_restaura_sigint_ignorado_pelo_background():
 t=(Path(__file__).parents[1]/'iniciar-conteiner.sh').read_text()
 assert 'setsid env --default-signal=INT,TERM' in t
 assert 'ros2 run navegacao_autonoma encerrar' in t
