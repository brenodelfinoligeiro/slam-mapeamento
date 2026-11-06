import math

import pytest

from simulador_base_nos.nucleo import ParametrosSimulacao


NOMES = ['left_wheel_joint', 'right_wheel_joint']


def novo_controle():
    from simulador_base_nos.nucleo import ReferenciaRodas
    return ReferenciaRodas(ParametrosSimulacao(limite_velocidade_roda=3.0))


def teste_ordem_das_juntas_e_limite():
    controle = novo_controle()
    assert controle.receber(NOMES[::-1], [100.0, -100.0], 1.0, 1.0, 10.0)
    assert controle.obter(1.1, 10.1) == (-3.0, 3.0)


@pytest.mark.parametrize('nomes,velocidades,instante,ros,mono', [
    (NOMES[:1], [1.0, 2.0], 1.1, 1.1, 10.1),
    (NOMES + ['outra'], [1.0, 2.0], 1.1, 1.1, 10.1),
    (['left_wheel_joint'] * 2, [1.0, 2.0], 1.1, 1.1, 10.1),
    (['left_wheel_joint', 'inexistente'], [1.0, 2.0], 1.1, 1.1, 10.1),
    (NOMES, [1.0], 1.1, 1.1, 10.1),
    (NOMES, [math.nan, 2.0], 1.1, 1.1, 10.1),
    (NOMES, [1.0, math.inf], 1.1, 1.1, 10.1),
    (NOMES, [True, 2.0], 1.1, 1.1, 10.1),
    (NOMES, [1.0, 2.0], 0.0, 1.1, 10.1),
    (NOMES, [1.0, 2.0], math.nan, 1.1, 10.1),
    (NOMES, [1.0, 2.0], 0.5, 1.1, 10.1),
    (NOMES, [1.0, 2.0], 1.2, 1.1, 10.1),
    (NOMES, [1.0, 2.0], 1.05, math.nan, 10.1),
    (NOMES, [1.0, 2.0], 1.05, 1.1, math.inf),
    (NOMES, [1.0, 2.0], 0.99, 1.1, 10.1),  # Fora de ordem.
    (NOMES, [1.0, 2.0], 1.0, 1.1, 10.1),  # Repetição não renova validade.
])
def teste_referencia_invalida_zera_imediatamente(nomes, velocidades, instante, ros, mono):
    controle = novo_controle()
    assert controle.receber(NOMES, [1.0, 2.0], 1.0, 1.0, 10.0)
    assert not controle.receber(nomes, velocidades, instante, ros, mono)
    assert controle.obter(1.11, 10.11) == (0.0, 0.0)


@pytest.mark.parametrize('ros,mono', [
    (1.4, 10.1), (1.1, 10.4), (1.1, 12.0),
    (0.5, 10.1), (1.1, 9.0), (math.nan, 10.1), (1.1, math.nan),
])
def teste_expiracao_independente_ros_e_monotonico(ros, mono):
    controle = novo_controle()
    assert controle.receber(NOMES, [1.0, 2.0], 1.0, 1.0, 10.0)
    assert controle.obter(ros, mono) == (0.0, 0.0)
    assert controle.obter(1.2, 10.2) == (0.0, 0.0)  # Sem ressurreição.


def teste_marca_antiga_expira_pelo_header_nao_pela_recepcao():
    controle = novo_controle()
    assert controle.obter(1.0, 10.0) == (0.0, 0.0)
    assert controle.receber(NOMES, [1.0, 2.0], 1.0, 1.3, 10.0)
    assert controle.obter(1.41, 10.1) == (0.0, 0.0)


def teste_tolerancia_futura_explicita_absorve_ordem_de_entrega_dds():
    controle = novo_controle()
    assert controle.parametros.tolerancia_futuro >= 0.05
    assert controle.receber(NOMES, [1.0, 2.0], 1.04, 1.0, 10.0)
    assert controle.obter(1.0, 10.02) == (1.0, 2.0)
    assert not controle.receber(NOMES, [1.0, 2.0], 1.06, 1.0, 10.03)
    assert controle.obter(1.1, 10.04) == (0.0, 0.0)


def teste_referencia_nova_depois_de_expirar_precisa_de_header_mais_recente():
    controle = novo_controle()
    assert controle.receber(NOMES, [1.0, 2.0], 1.0, 1.0, 10.0)
    assert controle.obter(1.0, 10.5) == (0.0, 0.0)  # /clock pausado.
    assert not controle.receber(NOMES, [1.0, 2.0], 1.0, 1.0, 10.6)
    assert controle.obter(1.1, 10.7) == (0.0, 0.0)


def teste_tolerancia_futura_pequena_preserva_fluxo_normal():
    controle = novo_controle()
    assert controle.receber(NOMES, [1.0, 2.0], 1.01, 1.0, 10.0)
    assert controle.obter(1.02, 10.02) == (1.0, 2.0)
