import importlib.util,math
from pathlib import Path
import pytest
P=Path(__file__).parents[1]
spec=importlib.util.spec_from_file_location('cli_objetivo',P/'navegacao_autonoma/ir_para.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def teste_objetivo_finito_e_timeout_positivo():
 o=m.argumentos(['--x','1.5','--y','-2','--yaw','.4','--prazo','80'])
 assert (o.x,o.y,o.yaw,o.prazo)==(1.5,-2.,.4,80.)
@pytest.mark.parametrize('args',[
 ['--x','nan','--y','0'],['--x','0','--y','inf'],['--x','0','--y','0','--yaw','nan'],
 ['--x','0','--y','0','--prazo','0'],['--x','0','--y','0','--prazo','-1']])
def teste_cli_rejeita_invalido(args):
 with pytest.raises(SystemExit):m.argumentos(args)
def teste_cliente_nao_rearma_automaticamente():
 t=(P/'navegacao_autonoma/ir_para.py').read_text()
 assert 'SetBool' not in t and 'geracao' in t and 'cancel_goal_async' in t

def teste_cliente_espera_gate_sem_rearmar():
 t=(P/'navegacao_autonoma/ir_para.py').read_text()
 assert '/navegacao/estado' in t and "get('aceita_objetivo')" in t
