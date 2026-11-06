from pathlib import Path
import sys,importlib,math
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

def grade():
    dados=[100 if x in (0,4) or y in (0,4) else 0 for y in range(5) for x in range(5)]
    return {'largura':5,'altura':5,'resolucao':1.,'origem':[0.,0.,0.],'dados':dados}

def teste_mapa_quadrado_e_paredes_concordam():
    m=importlib.import_module('metricas_mapa')
    paredes=[[.5,.5,4.5,.5],[4.5,.5,4.5,4.5],[4.5,4.5,.5,4.5],[.5,4.5,.5,.5]]
    resultado=m.analisar(grade(),paredes,tolerancia=.6)
    assert resultado['fracao_ocupados_proximos_parede']==1.
    assert resultado['fracao_parede_proxima_ocupado']==1.
    assert resultado['celulas_livres']>0 and resultado['celulas_ocupadas']>0

def teste_rotacao_origem_e_distancia_segmento():
    m=importlib.import_module('metricas_mapa')
    assert m.transformar(.5,.5,[10.,20.,math.pi/2])==pytest.approx((10.-.5,20.+.5))
    assert m.distancia_segmento((2.,1.),[0.,0.,1.,0.])==pytest.approx(math.sqrt(2.))

@pytest.mark.parametrize('alteracao',[{'resolucao':0.},{'resolucao':float('nan')},{'largura':True},{'dados':[]},{'origem':[0.,0.,float('inf')]}])
def teste_grade_invalida_rejeitada(alteracao):
    m=importlib.import_module('metricas_mapa');g=grade();g.update(alteracao)
    with pytest.raises(ValueError):m.analisar(g,[[0.,0.,1.,0.]])

def teste_mapa_vazio_nao_e_aprovado():
    m=importlib.import_module('metricas_mapa');g=grade();g['dados']=[-1]*25
    with pytest.raises(ValueError):m.analisar(g,[[0.,0.,1.,0.]])
