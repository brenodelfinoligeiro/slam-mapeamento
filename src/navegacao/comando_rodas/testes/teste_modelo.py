from pathlib import Path
import sys, importlib, math
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

def conversor(**opcoes):
    modelo = importlib.import_module('comando_rodas.modelo')
    return modelo.Conversor(raio=0.05, distancia=0.2, **opcoes)

def teste_avanco_e_rotacao():
    c = conversor()
    assert c.receber(0.2, 0.0, 1.0, 1.0, 10.0)
    assert c.rodas(1.0, 10.0) == pytest.approx((0.2/0.05, 0.2/0.05))
    assert c.receber(0.0, 1.0, 1.1, 1.1, 10.1)
    assert c.rodas(1.1, 10.1) == pytest.approx((-0.2/(2*0.05), 0.2/(2*0.05)))

def teste_limites_preservam_curvatura():
    c=conversor(maximo_linear=0.3, maximo_angular=1.0)
    assert c.receber(0.6, 1.0, 2.0, 2.0, 12.0)
    esquerda,direita=c.rodas(2.0,12.0)
    v=0.05*(esquerda+direita)/2
    w=0.05*(direita-esquerda)/0.2
    assert v==pytest.approx(0.3)
    assert w/v==pytest.approx(1/0.6)

@pytest.mark.parametrize('v,w,stamp,agora', [(float('nan'),0.,1.,1.),(0.,float('inf'),1.,1.),(0.1,0.,0.,1.),(0.1,0.,2.,1.)])
def teste_invalidos_zeram_referencia(v,w,stamp,agora):
    c=conversor();c.receber(.1,0.,1.,1.,10.)
    assert not c.receber(v,w,stamp,agora,10.)
    assert c.rodas(agora,10.)==(0.,0.)

def teste_expiracao_ros_parede_e_retrocesso():
    for ros,parede in [(1.5,10.1),(1.1,10.5),(.5,10.1)]:
        c=conversor(prazo=.4);c.receber(.1,0.,1.,1.,10.)
        assert c.rodas(ros,parede)==(0.,0.)

@pytest.mark.parametrize('parametros',[{'raio':0.},{'distancia':float('nan')},{'prazo':-1.}])
def teste_parametros_invalidos(parametros):
    modelo=importlib.import_module('comando_rodas.modelo')
    with pytest.raises(ValueError):modelo.Conversor(**parametros)


def teste_emissao_so_por_entrada_ou_transicao_de_parada():
    c=conversor()
    assert c.nova_referencia(1.,10.) is None
    c.receber(.1,0.,1.,1.,10.)
    assert c.nova_referencia(1.,10.) is not None
    assert c.nova_referencia(1.02,10.02) is None
    assert c.nova_referencia(1.5,10.5)==(0.,0.)
    assert c.nova_referencia(1.52,10.52) is None
    c.receber(.1,0.,1.6,1.6,10.6)
    assert c.nova_referencia(1.6,10.6) is not None
    c.rejeitar()
    assert c.nova_referencia(1.7,10.7)==(0.,0.)


def teste_repeticao_identica_nao_reemite_nem_renova_validade():
    c=conversor(prazo=.4);c.receber(.1,0.,1.,1.,10.)
    assert c.nova_referencia(1.,10.) is not None
    assert c.receber(.1,0.,1.,1.02,10.02)
    assert c.nova_referencia(1.02,10.02) is None
    assert not c.receber(.1,0.,1.,1.1,10.5)
    assert c.nova_referencia(1.1,10.5)==(0.,0.)

def teste_mesmo_carimbo_com_comando_diferente_revoga():
    c=conversor();c.receber(.1,0.,1.,1.,10.);c.nova_referencia(1.,10.)
    assert not c.receber(.2,0.,1.,1.,10.01)
    assert c.nova_referencia(1.,10.01)==(0.,0.)

def teste_novo_comando_apos_retrocesso_exige_nova_epoca():
    c=conversor();c.receber(.1,0.,10.,10.,100.);c.nova_referencia(10.,100.)
    assert c.rodas(.1,101.)==(0.,0.)
    assert c.receber(.1,0.,.2,.2,101.1)
    assert c.nova_referencia(.2,101.1) is not None
