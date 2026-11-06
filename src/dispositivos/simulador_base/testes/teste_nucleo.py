import math

import pytest


@pytest.mark.parametrize(
    'esquerda,direita,dt,x,y,angulo',
    [
        (0.0, 5.0, math.pi, 0.0, 0.5, math.pi),
        (-2.0, -2.0, 1.0, -0.2, 0.0, 0.0),
        (-2.5, 2.5, 1.0, 0.0, 0.0, 1.0),
        (5.0, 0.0, math.pi / 2, 0.25, -0.25, -math.pi / 2),
        (2.0, 2.0 + 1e-12, 1.0, 0.2, 0.0, 2e-13),
    ],
)
def teste_se2_exato_curva_re_rotacao(esquerda, direita, dt, x, y, angulo):
    from simulador_base_nos.nucleo import ModeloCinematico, ParametrosSimulacao

    modelo = ModeloCinematico(ParametrosSimulacao(raio_roda=0.1, distancia_rodas=0.5))
    estado = modelo.passo(esquerda, direita, dt)
    assert (estado.x, estado.y, estado.angulo) == pytest.approx((x, y, angulo), abs=1e-10)


def teste_curva_independe_subdivisao_com_velocidade_constante():
    from simulador_base_nos.nucleo import ModeloCinematico, ParametrosSimulacao

    parametros = ParametrosSimulacao(raio_roda=0.1, distancia_rodas=0.5)
    inteiro, dividido = ModeloCinematico(parametros), ModeloCinematico(parametros)
    esperado = inteiro.passo(1.0, 3.0, 1.0)
    for _ in range(100):
        obtido = dividido.passo(1.0, 3.0, 0.01)
    assert (obtido.x, obtido.y, obtido.angulo) == pytest.approx(
        (esperado.x, esperado.y, esperado.angulo)
    )


def teste_validacao_de_passo_nao_corrompe_estado():
    from simulador_base_nos.nucleo import ModeloCinematico, ParametrosSimulacao

    modelo = ModeloCinematico(ParametrosSimulacao())
    inicial = modelo.passo(1.0, 1.0, 0.1)
    for esquerda, direita, dt in [
        (1, 1, 0), (1, 1, -0.1), (1, 1, float('nan')),
        (1, 1, float('inf')), (float('nan'), 1, 0.1),
        (1, float('inf'), 0.1), (True, 1, 0.1),
    ]:
        with pytest.raises(ValueError):
            modelo.passo(esquerda, direita, dt)
        assert (modelo.x, modelo.y, modelo.angulo) == (
            inicial.x, inicial.y, inicial.angulo
        )


@pytest.mark.parametrize('campo,valor', [
    ('raio_roda', 0.0), ('raio_roda', float('nan')),
    ('distancia_rodas', -1.0), ('distancia_rodas', float('inf')),
    ('frequencia', 0.0), ('frequencia', 1e12), ('prazo_comando', -0.1),
    ('pulsos_por_volta', 0), ('pulsos_por_volta', 2**32),
    ('pulsos_por_volta', 1.5), ('pulsos_por_volta', True),
    ('escala_encoder_esquerda', 0.0), ('escala_encoder_direita', float('nan')),
    ('ruido_giroscopio', -1.0), ('bias_giroscopio', float('inf')),
    ('semente', 2.5), ('publicar_clock', 1),
    ('limite_velocidade_roda', 0.0), ('limite_aceleracao_roda', -1.0),
])
def teste_parametro_invalido_rejeitado(campo, valor):
    from simulador_base_nos.nucleo import ParametrosSimulacao

    with pytest.raises(ValueError):
        ParametrosSimulacao(**{campo: valor})


def teste_aceleracao_e_velocidade_sao_limitadas_virtualmente():
    from simulador_base_nos.nucleo import ModeloCinematico, ParametrosSimulacao

    modelo = ModeloCinematico(ParametrosSimulacao(
        raio_roda=0.1, limite_velocidade_roda=3.0, limite_aceleracao_roda=2.0
    ))
    primeiro = modelo.passo(100.0, 100.0, 0.5)
    assert primeiro.velocidade_linear == pytest.approx(0.1)
    for _ in range(10):
        ultimo = modelo.passo(100.0, 100.0, 0.5)
    assert ultimo.velocidade_linear == pytest.approx(0.3)
    modelo.parar()
    parado = modelo.passo(0.0, 0.0, 0.5)
    assert parado.velocidade_linear == 0.0
    assert parado.x == ultimo.x


def teste_defaults_geometricos_correspondem_a_referencia_cad_confirmada():
    from simulador_base_nos.nucleo import ParametrosSimulacao

    parametros = ParametrosSimulacao()
    assert parametros.raio_roda == 0.03446139931678772
    assert parametros.distancia_rodas == 0.13238015174865722


def teste_avanco_reto_em_metros():
    from simulador_base_nos.nucleo import ModeloCinematico, ParametrosSimulacao

    modelo = ModeloCinematico(ParametrosSimulacao(raio_roda=0.1, distancia_rodas=0.5))
    estado = modelo.passo(2.0, 2.0, 1.0)
    assert estado.x == pytest.approx(0.2)
    assert estado.y == pytest.approx(0.0)
    assert estado.angulo == pytest.approx(0.0)
    assert estado.velocidade_linear == pytest.approx(0.2)
    assert estado.velocidade_angular == pytest.approx(0.0)
