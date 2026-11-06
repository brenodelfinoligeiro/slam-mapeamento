from arbitro.modelo import Arbitro

def teste_manual_padrao_nao_aceita_entrada_autonoma():
    a=Arbitro()
    assert a.modo=='manual'
    assert not a.receber('autonomo',.2,.1,1.,1.,10.)
    assert a.saida(1.,10.)[:2]==(0.,0.)
    assert a.receber('manual',.15,.3,1.1,1.1,10.1)
    assert a.saida(1.1,10.1)==(.15,.3,1.1)


def teste_troca_e_parada_exigem_comando_novo_sem_fallback():
    a=Arbitro()
    a.receber('manual',.1,0.,1.,1.,10.)
    assert a.selecionar('autonomo',1.1,10.1)
    assert a.saida(1.1,10.1)[:2]==(0.,0.)
    assert not a.receber('autonomo',.2,0.,1.1,1.1,10.1)
    assert a.receber('autonomo',.2,0.,1.16,1.16,10.16)
    assert not a.receber('manual',.3,0.,1.17,1.17,10.17)
    assert a.saida(1.17,10.17)[:2]==(.2,0.)
    a.parar(1.2,10.2)
    assert a.modo=='parado' and not a.receber('autonomo',.2,0.,1.3,1.3,10.3)
    assert a.selecionar('manual',1.4,10.4)
    assert not a.receber('manual',.1,0.,1.3,1.4,10.4)
    assert a.receber('manual',.1,0.,1.46,1.46,10.46)


def teste_expiracao_ros_e_parede_nao_renovada_por_duplicata():
    a=Arbitro()
    assert a.receber('manual',.1,0.,1.,1.,10.)
    assert a.receber('manual',.1,0.,1.,1.1,10.1)
    assert a.saida(1.1,10.31)[:2]==(0.,0.)
    assert not a.receber('manual',.1,0.,1.,1.1,10.32)
    b=Arbitro();b.receber('manual',.1,0.,1.,1.,10.)
    assert b.saida(1.31,10.1)[:2]==(0.,0.)

def teste_conflito_de_carimbo_revoga_sem_ressuscitar_replay():
    a=Arbitro();a.receber('manual',.1,0.,1.,1.,10.)
    assert not a.receber('manual',.2,0.,1.,1.01,10.01)
    assert a.saida(1.01,10.01)[:2]==(0.,0.)
    assert not a.receber('manual',.1,0.,1.,1.02,10.02)
    assert a.receber('manual',.1,0.,1.03,1.03,10.03)


import math
import pytest

@pytest.mark.parametrize('valores',[(math.nan,0.,1.,1.,10.),(.1,math.inf,1.,1.,10.),(.1,0.,0.,1.,10.),(.1,0.,2.,1.,10.),(.1,0.,.1,1.,10.)])
def teste_entrada_invalida_para_origem_selecionada_revoga(valores):
    a=Arbitro();a.receber('manual',.1,0.,1.,1.,10.)
    assert not a.receber('manual',*valores)
    assert a.saida(1.,10.)[:2]==(0.,0.)

def teste_falha_inativa_nao_interrompe_origem_selecionada():
    a=Arbitro();a.receber('manual',.1,0.,1.,1.,10.)
    assert not a.receber('autonomo',math.nan,0.,1.,1.,10.)
    assert a.saida(1.,10.)[:2]==(.1,0.)

@pytest.mark.parametrize('novo_ros,novo_parede',[(.5,10.1),(1.1,9.)])
def teste_retrocesso_de_relogio_trava_parado_sem_rearme_automatico(novo_ros,novo_parede):
    a=Arbitro();a.receber('manual',.1,0.,1.,1.,10.)
    assert a.saida(novo_ros,novo_parede)[:2]==(0.,0.) and a.modo=='parado'
    assert not a.receber('manual',.2,0.,2.,2.,11.)
    assert a.selecionar('manual',2.1,11.1)
    assert a.receber('manual',.1,0.,2.16,2.16,11.16)

@pytest.mark.parametrize('opcoes',[{'prazo':0.},{'prazo':True},{'prazo':float('nan')},{'tolerancia_futuro':-.1}])
def teste_parametro_invalido(opcoes):
    with pytest.raises(ValueError):Arbitro(**opcoes)


@pytest.mark.parametrize('ros',[float('nan'),float('inf'),-1.])
def teste_relogio_invalido_nao_emite_carimbo_invalido(ros):
    a=Arbitro();saida=a.saida(ros,10.)
    assert saida[:2]==(0.,0.) and math.isfinite(saida[2]) and saida[2]>=0
    assert a.modo=='parado'


def teste_estado_parado_nao_e_nome_de_fonte_admissivel():
    a=Arbitro();a.parar(1.,10.)
    assert not a.receber('parado',.2,0.,1.1,1.1,10.1)
    assert a.saida(1.1,10.1)[:2]==(0.,0.)
