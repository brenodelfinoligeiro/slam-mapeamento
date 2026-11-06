import math

import pytest


def novo_nucleo(**parametros):
    from odometria_rodas.nucleo import OdometriaRodas
    configuracao = {"raio_roda": 0.1, "distancia_rodas": 0.5}
    configuracao.update(parametros)
    return OdometriaRodas(**configuracao)


def ler(nucleo, tempo=1_000_000_000, esquerda=0, direita=0, sessao=1, pulsos=100):
    return nucleo.processar(tempo, sessao, esquerda, direita, pulsos)


def teste_primeira_leitura_e_baseline_sem_movimento():
    nucleo = novo_nucleo()
    estado = ler(nucleo, esquerda=500, direita=-300)
    assert (estado.x, estado.y, estado.angulo) == (0.0, 0.0, 0.0)
    assert (estado.velocidade, estado.rotacao) == (0.0, 0.0)
    assert estado.posicoes == (0.0, 0.0)
    assert estado.velocidades == (0.0, 0.0)
    assert estado.tempo_ns == 1_000_000_000


@pytest.mark.parametrize("pulsos", [100, -100, 0])
def teste_linha_re_e_parada_derivadas_dos_incrementos(pulsos):
    nucleo = novo_nucleo()
    origem = 2**60
    ler(nucleo, esquerda=origem, direita=origem)
    estado = ler(nucleo, tempo=3_000_000_000,
                 esquerda=origem+pulsos, direita=origem+pulsos)
    distancia = pulsos * (2.0 * math.pi / 100) * 0.1
    assert (estado.x, estado.y, estado.angulo) == pytest.approx((distancia, 0, 0))
    assert estado.velocidade == pytest.approx(distancia / 2)
    assert estado.rotacao == 0.0
    assert estado.posicoes == pytest.approx((pulsos * 2 * math.pi / 100,) * 2)
    assert estado.velocidades == pytest.approx((pulsos * math.pi / 100,) * 2)


@pytest.mark.parametrize("esquerda,direita", [(0, 100), (100, 0), (-50, 50), (-10, -80)])
def teste_arco_se2_e_rotacao_no_proprio_eixo(esquerda, direita):
    nucleo = novo_nucleo()
    ler(nucleo)
    estado = ler(nucleo, tempo=2_000_000_000, esquerda=esquerda, direita=direita)
    de = esquerda * 2 * math.pi / 100 * 0.1
    dd = direita * 2 * math.pi / 100 * 0.1
    giro = (dd - de) / 0.5
    raio = (de + dd) / (2 * giro)
    assert (estado.x, estado.y) == pytest.approx((raio * math.sin(giro),
                                                raio * (1 - math.cos(giro))))
    assert estado.angulo == pytest.approx(giro)
    assert estado.rotacao == pytest.approx(giro)
    seguinte = ler(nucleo, tempo=3_000_000_000,
                   esquerda=esquerda+25, direita=direita+25)
    reta = math.pi * 0.05
    assert seguinte.x == pytest.approx(estado.x + reta * math.cos(giro))
    assert seguinte.y == pytest.approx(estado.y + reta * math.sin(giro))
    assert seguinte.angulo == pytest.approx(giro)


def teste_nova_sessao_reinicia_pose_e_origem_mesmo_com_retrocesso_do_clock():
    nucleo = novo_nucleo()
    ler(nucleo)
    ler(nucleo, tempo=2_000_000_000, esquerda=100, direita=100)
    reinicio = ler(nucleo, tempo=100_000_000, esquerda=-90, direita=50, sessao=2)
    assert (reinicio.x, reinicio.y, reinicio.angulo) == (0.0, 0.0, 0.0)
    assert reinicio.posicoes == (0.0, 0.0)
    estado = ler(nucleo, tempo=1_100_000_000, esquerda=10, direita=150, sessao=2)
    assert estado.x == pytest.approx(0.2 * math.pi)


@pytest.mark.parametrize("tempo", [1_000_000_000, 500_000_000])
def teste_clock_nao_monotonico_ressincroniza_sem_salto(tempo):
    nucleo = novo_nucleo()
    ler(nucleo)
    estado = ler(nucleo, tempo=2_000_000_000, esquerda=100, direita=100)
    assert ler(nucleo, tempo=tempo, esquerda=900, direita=900) is None
    seguinte = ler(nucleo, tempo=tempo+1_000_000_000, esquerda=1000, direita=1000)
    assert seguinte.x == pytest.approx(estado.x + 0.2 * math.pi)
    assert seguinte.posicoes == pytest.approx((4 * math.pi, 4 * math.pi))
    assert seguinte.velocidade == pytest.approx(0.2 * math.pi)


def teste_mudanca_resolucao_ressincroniza_sem_reinterpretar_contagens():
    nucleo = novo_nucleo()
    ler(nucleo)
    assert ler(nucleo, tempo=2_000_000_000, esquerda=100, direita=100, pulsos=200) is None
    estado = ler(nucleo, tempo=3_000_000_000, esquerda=300, direita=300, pulsos=200)
    assert estado.x == pytest.approx(0.2 * math.pi)


@pytest.mark.parametrize("parametro", ["raio_roda", "distancia_rodas",
                                      "variancia_velocidade", "variancia_rotacao"])
@pytest.mark.parametrize("valor", [0, -0.1, math.nan, math.inf, True, None])
def teste_parametros_devem_ser_finitos_e_positivos(parametro, valor):
    with pytest.raises(ValueError):
        novo_nucleo(**{parametro: valor})


def teste_covariancias_sem_falsa_certeza_em_eixos_nao_observados():
    nucleo = novo_nucleo(variancia_velocidade=0.2, variancia_rotacao=0.3)
    assert len(nucleo.covariancia_velocidade) == 36
    assert nucleo.covariancia_velocidade[0] == 0.2
    assert nucleo.covariancia_velocidade[35] == 0.3
    assert nucleo.covariancia_velocidade[7] == 0.2  # Restrição cinemática vy=0.
    for indice in (14, 21, 28):
        assert nucleo.covariancia_velocidade[indice] >= 1e3
    assert all(nucleo.covariancia_pose[i * 7] > 0 for i in range(6))


@pytest.mark.parametrize("campo,valor", [("pulsos", 0), ("pulsos", -1),
                                         ("pulsos", 2**32), ("pulsos", True),
                                         ("esquerda", -(2**63)-1),
                                         ("direita", 2**63), ("esquerda", 0.5),
                                         ("direita", math.nan),
                                         ("sessao", -1), ("sessao", 2**64),
                                         ("tempo", 0), ("tempo", -1),
                                         ("tempo", math.inf)])
def teste_entrada_invalida_nao_altera_baseline(campo, valor):
    nucleo = novo_nucleo()
    ler(nucleo)
    with pytest.raises(ValueError):
        ler(nucleo, tempo=2_000_000_000, **{campo: valor}) if campo != "tempo" else ler(nucleo, tempo=valor)
    estado = ler(nucleo, tempo=2_000_000_000, esquerda=100, direita=100)
    assert estado.x == pytest.approx(0.2 * math.pi)


def teste_overflow_derivado_rejeita_sem_corromper_estado():
    nucleo = novo_nucleo(raio_roda=1e308)
    ler(nucleo)
    with pytest.raises(ValueError):
        ler(nucleo, tempo=2_000_000_000, esquerda=100, direita=100)
    assert ler(nucleo, tempo=2_000_000_000).x == 0.0


def teste_arco_quase_reto_continua_finito_e_pose_nao_e_truth():
    nucleo = novo_nucleo()
    ler(nucleo, pulsos=2**32-1)
    estado = ler(nucleo, tempo=1_000_000_001, esquerda=1000, direita=1001, pulsos=2**32-1)
    assert estado.x > 0 and estado.y > 0
    assert all(math.isfinite(v) for v in (estado.x, estado.y, estado.velocidade, estado.rotacao))
    assert novo_nucleo().covariancia_velocidade[0] == 0.0025
    assert novo_nucleo().covariancia_velocidade[35] == 0.04
