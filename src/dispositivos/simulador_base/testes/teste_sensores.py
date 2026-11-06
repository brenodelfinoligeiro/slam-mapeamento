import math

import pytest

from simulador_base_nos.nucleo import ModeloCinematico, ParametrosSimulacao


def teste_encoders_acumulam_quantizacao_signed_com_escalas_assimetricas():
    modelo = ModeloCinematico(ParametrosSimulacao(
        pulsos_por_volta=100, escala_encoder_esquerda=1.1,
        escala_encoder_direita=0.9, ruido_giroscopio=0.0,
    ))
    primeiro = modelo.passo(math.tau, math.tau, 1.0)
    assert primeiro.contagem_esquerda == 110
    assert primeiro.contagem_direita == 90
    assert primeiro.angulo == 0.0  # Erro do sensor não altera a verdade de referência.
    retorno = modelo.passo(-math.tau, -math.tau, 2.0)
    assert retorno.contagem_esquerda == -110
    assert retorno.contagem_direita == -90


def teste_subpulsos_nao_sao_descartados_a_cada_passo():
    modelo = ModeloCinematico(ParametrosSimulacao(
        pulsos_por_volta=100, escala_encoder_esquerda=1.0,
        escala_encoder_direita=1.0,
    ))
    for _ in range(100):
        estado = modelo.passo(math.tau / 100, math.tau / 100, 0.01)
    assert estado.contagem_esquerda == estado.contagem_direita == 1


def teste_giroscopio_bias_e_acelerometro_sao_sensores_nao_orientacao():
    modelo = ModeloCinematico(ParametrosSimulacao(
        raio_roda=0.1, distancia_rodas=0.5,
        ruido_giroscopio=0.0, bias_giroscopio=0.125,
    ))
    estado = modelo.passo(1.0, 3.0, 0.1)
    assert estado.giroscopio_z == pytest.approx(0.4 + 0.125)
    assert estado.aceleracao_x == pytest.approx(2.0)
    assert estado.aceleracao_y == pytest.approx(0.2 * 0.4)
    assert estado.aceleracao_z == pytest.approx(9.80665)
    assert not hasattr(estado, 'orientacao_imu')


def teste_ruido_reproduzivel_por_semente_independente_da_sessao():
    parametros = ParametrosSimulacao(semente=7)
    a, b = ModeloCinematico(parametros), ModeloCinematico(parametros)
    c = ModeloCinematico(ParametrosSimulacao(semente=8))
    serie_a, serie_b, serie_c = [], [], []
    for _ in range(12):
        serie_a.append(a.passo(1.0, 2.0, 0.1).giroscopio_z)
        serie_b.append(b.passo(1.0, 2.0, 0.1).giroscopio_z)
        serie_c.append(c.passo(1.0, 2.0, 0.1).giroscopio_z)
    assert serie_a == serie_b
    assert serie_a != serie_c
    assert len(set(serie_a)) > 1


def teste_reinicio_gera_nova_sessao_e_nao_reutiliza_contagens():
    a = ModeloCinematico(ParametrosSimulacao())
    movido = a.passo(2.0, 2.0, 1.0)
    b = ModeloCinematico(ParametrosSimulacao())
    reiniciado = b.passo(0.0, 0.0, 0.1)
    assert 0 < movido.sessao < 2**64
    assert 0 < reiniciado.sessao < 2**64
    assert reiniciado.sessao != movido.sessao
    assert reiniciado.contagem_esquerda == reiniciado.contagem_direita == 0
    assert a.passo(0.0, 0.0, 0.1).sessao == movido.sessao
