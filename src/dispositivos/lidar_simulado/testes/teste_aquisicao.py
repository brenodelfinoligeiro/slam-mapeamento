import math

import pytest


def teste_fonte_50hz_produz_10hz_por_carimbo_de_aquisicao():
    from lidar_simulado.aquisicao import LimitadorAquisicao
    limitador = LimitadorAquisicao(10.)
    aceitos = [marca for marca in range(0, 1_000_000_000, 20_000_000)
               if limitador.admitir(marca, pronto=True)]
    assert aceitos == list(range(0, 1_000_000_000, 100_000_000))


def teste_repeticao_espera_tf_e_reinicio_da_epoca():
    from lidar_simulado.aquisicao import LimitadorAquisicao
    limitador = LimitadorAquisicao(10.)
    assert not limitador.admitir(1_000_000_000, pronto=False)
    assert limitador.admitir(1_020_000_000, pronto=True)
    assert not limitador.admitir(1_020_000_000, pronto=True)
    assert not limitador.admitir(1_040_000_000, pronto=True)
    # Retrocesso comparado à última referência observada, não só à última emitida.
    assert limitador.admitir(1_030_000_000, pronto=True)
    assert limitador.admitir(0, pronto=True)
    assert not limitador.admitir(0, pronto=True)
    assert limitador.admitir(100_000_000, pronto=True)


@pytest.mark.parametrize('marca', [-1, 0.1, True, math.nan])
def teste_carimbo_invalido_nao_muda_estado(marca):
    from lidar_simulado.aquisicao import LimitadorAquisicao
    limitador = LimitadorAquisicao(10.)
    assert limitador.admitir(0, pronto=True)
    with pytest.raises(ValueError):
        limitador.admitir(marca, pronto=True)
    assert not limitador.admitir(20_000_000, pronto=True)


@pytest.mark.parametrize('posicao,quaternion,esperado', [
    ((1, -2, .3), (0, 0, 0, 1), (1, -2, 0)),
    ((0, 0, .4), (0, 0, math.sqrt(2), math.sqrt(2)), (0, 0, math.pi / 2)),
])
def teste_extrai_pose_planar_normalizando_quaternion(posicao, quaternion, esperado):
    from lidar_simulado.aquisicao import extrair_pose_planar
    assert extrair_pose_planar(posicao, quaternion) == pytest.approx(esperado)


@pytest.mark.parametrize('posicao,quaternion', [
    ((math.nan, 0, 0), (0, 0, 0, 1)),
    ((0, 0, 0), (0, 0, 0, 0)),
    ((0, 0, 0), (0, 0, math.inf, 1)),
    ((0, 0, 0), (1, 0, 0, 0)),
    ((0, 0, 0), (0, .2, 0, 1)),
])
def teste_rejeita_pose_nao_planar_ou_invalida(posicao, quaternion):
    from lidar_simulado.aquisicao import extrair_pose_planar
    with pytest.raises(ValueError):
        extrair_pose_planar(posicao, quaternion)
