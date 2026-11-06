import sys,math
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).parents[1]))
from oraculo import distancia_segmentos,analisar_percurso

def teste_interseccao_inclui_colinear_e_pontas():
 assert distancia_segmentos((0,0),(2,0),(1,-1),(1,1))==0
 assert distancia_segmentos((0,0),(2,0),(1,0),(3,0))==0
 assert distancia_segmentos((0,0),(1,0),(1,0),(1,1))==0
 assert distancia_segmentos((0,0),(1,0),(0,2),(1,2))==pytest.approx(2)

def teste_distancia_com_segmentos_degenerados():
 assert distancia_segmentos((0,0),(0,0),(2,0),(2,1))==pytest.approx(2)
 assert distancia_segmentos((0,0),(0,0),(0,0),(0,0))==0

def teste_percurso_audita_trecho_entre_amostras_nao_so_pontos():
 r=analisar_percurso([(-1,0),(1,0)],[(0,-1,0,1)],.18)
 assert r['folga_minima_m']<0
 assert not r['sem_interseccao_com_envoltoria']

def teste_percurso_seguro_e_comprimento():
 r=analisar_percurso([(0,0),(1,0),(1,1)],[(0,2,2,2)],.18)
 assert r['sem_interseccao_com_envoltoria']
 assert r['comprimento_m']==pytest.approx(2)
 assert r['folga_minima_m']==pytest.approx(.815)

@pytest.mark.parametrize('pontos,raio',[([], .18), ([(math.nan,0),(1,0)],.18), ([(0,0)],-.1)])
def teste_dados_invalidos_rejeitados(pontos,raio):
 with pytest.raises(ValueError):analisar_percurso(pontos,[(0,2,2,2)],raio)

def teste_envoltoria_reproduzida_das_malhas_e_configuracao():
 import json,yaml
 from medir_envoltoria import medir
 raiz=Path(__file__).resolve().parents[3]
 medido=medir(raiz)
 salvo=json.loads((raiz/'docs/navegacao/geometria-planejamento.json').read_text())
 assert medido==salvo
 c=yaml.safe_load((raiz/'src/navegacao/navegacao_autonoma/configuracao/nav2.yaml').read_text())
 for nome in ['global_costmap','local_costmap']:
  assert c[nome][nome]['ros__parameters']['robot_radius']==medido['raio_planejamento_m']
