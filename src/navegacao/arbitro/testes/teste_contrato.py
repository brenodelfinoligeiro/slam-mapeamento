from types import SimpleNamespace as S
import math
import pytest

def mensagem():
    return S(header=S(frame_id='base_footprint',stamp=S(sec=1,nanosec=20)),twist=S(linear=S(x=.1,y=0.,z=0.),angular=S(x=0.,y=0.,z=.3)))

def teste_contrato_preserva_valores_e_carimbo():
    from arbitro.contrato import extrair_comando
    assert extrair_comando(mensagem())==(.1,.3,1.+20e-9)

@pytest.mark.parametrize('defeito',['frame','lateral','vertical','roll','pitch','nan','sec','nanosec'])
def teste_contrato_rejeita_comando_invalido(defeito):
    from arbitro.contrato import extrair_comando
    m=mensagem()
    if defeito=='frame':m.header.frame_id='map'
    elif defeito=='lateral':m.twist.linear.y=.1
    elif defeito=='vertical':m.twist.linear.z=.1
    elif defeito=='roll':m.twist.angular.x=.1
    elif defeito=='pitch':m.twist.angular.y=.1
    elif defeito=='nan':m.twist.linear.x=math.nan
    elif defeito=='sec':m.header.stamp.sec=-1
    else:m.header.stamp.nanosec=1000000000
    with pytest.raises(ValueError):extrair_comando(m)
