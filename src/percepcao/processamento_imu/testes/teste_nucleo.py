import math

import pytest


def novo_nucleo(**parametros):
    from processamento_imu.nucleo import ProcessamentoImu
    return ProcessamentoImu(**parametros)


def tratar(nucleo, tempo=1_000_000_000, agora=1_000_000_000,
           giro=(0.0, 0.0, 0.01), aceleracao=(0.0, 0.0, 9.80665),
           frame="imu_mount_link"):
    return nucleo.processar(tempo, agora, giro, aceleracao, frame)


def teste_bias_virtual_removido_sem_inventar_orientacao():
    resultado = tratar(novo_nucleo(), giro=(0.1, -0.2, 0.11))
    assert resultado.giroscopio == pytest.approx((0.1, -0.2, 0.1))
    assert resultado.acelerometro == (0.0, 0.0, 9.80665)
    assert resultado.tempo_ns == 1_000_000_000
    assert resultado.frame_id == "imu_mount_link"
    assert resultado.covariancia_orientacao == (-1.0,) + (0.0,) * 8


def teste_covariancias_diagonais_e_bias_configuravel_estatico():
    nucleo = novo_nucleo(bias_giroscopio_z=-0.2,
                         variancia_giroscopio=0.03, variancia_acelerometro=0.4)
    a = tratar(nucleo, giro=(0, 0, 1.0))
    b = tratar(nucleo, tempo=1_100_000_000, agora=1_100_000_000, giro=(0, 0, 2.0))
    assert a.giroscopio[2] == pytest.approx(1.2)
    assert b.giroscopio[2] == pytest.approx(2.2)
    assert a.covariancia_giroscopio == (0.03, 0, 0, 0, 0.03, 0, 0, 0, 0.03)
    assert a.covariancia_acelerometro == (0.4, 0, 0, 0, 0.4, 0, 0, 0, 0.4)


@pytest.mark.parametrize("tempo,agora", [(1_000_000_000, 1_300_000_001),
                                         (1_050_000_001, 1_000_000_000),
                                         (0, 1), (1, 0), (-1, 1)])
def teste_rejeita_aquisicao_vencida_futura_ou_clock_sem_inicio(tempo, agora):
    with pytest.raises(ValueError):
        tratar(novo_nucleo(), tempo=tempo, agora=agora)


def teste_limite_tolerancia_e_ordem_de_aquisicao():
    nucleo = novo_nucleo(tolerancia_atraso=0.3)
    tratar(nucleo, tempo=1_000_000_000, agora=1_300_000_000)
    for tempo in (1_000_000_000, 999_999_999):
        with pytest.raises(ValueError):
            tratar(nucleo, tempo=tempo, agora=1_300_000_000)
    assert tratar(nucleo, tempo=1_100_000_000, agora=1_300_000_000).tempo_ns == 1_100_000_000


@pytest.mark.parametrize("campo,valor", [("giro", (math.nan, 0, 0)),
                                         ("giro", (0, math.inf, 0)),
                                         ("aceleracao", (0, 0, -math.inf)),
                                         ("aceleracao", (1, 2)),
                                         ("frame", ""), ("frame", "base_link"),
                                         ("tempo", 1.5), ("agora", True)])
def teste_rejeita_leituras_invalidas_sem_consumir_stamp(campo, valor):
    nucleo = novo_nucleo()
    with pytest.raises(ValueError):
        tratar(nucleo, **{campo: valor})
    assert tratar(nucleo).tempo_ns == 1_000_000_000


def teste_retrocesso_clock_ros_abre_nova_epoca_sem_trocar_stamp():
    nucleo = novo_nucleo()
    tratar(nucleo, tempo=10_000_000_000, agora=10_000_000_000)
    estado = tratar(nucleo, tempo=1_000_000_000, agora=1_000_000_000)
    assert estado.tempo_ns == 1_000_000_000
    with pytest.raises(ValueError):
        tratar(nucleo, tempo=999_999_999, agora=1_000_000_000)


@pytest.mark.parametrize("parametro", ["variancia_giroscopio", "variancia_acelerometro"])
@pytest.mark.parametrize("valor", [0, -1, math.nan, math.inf, True, None])
def teste_covariancias_exigem_valores_positivos_finitos(parametro, valor):
    with pytest.raises(ValueError):
        novo_nucleo(**{parametro: valor})


@pytest.mark.parametrize("parametro,valor", [("bias_giroscopio_z", math.nan),
                                             ("bias_giroscopio_z", math.inf),
                                             ("bias_giroscopio_z", True),
                                             ("tolerancia_atraso", -1),
                                             ("tolerancia_atraso", math.nan),
                                             ("tolerancia_atraso", math.inf)])
def teste_calibracao_e_tolerancia_validas(parametro, valor):
    with pytest.raises(ValueError):
        novo_nucleo(**{parametro: valor})


def teste_epsilon_positivo_e_tolerancia_zero():
    estado = tratar(novo_nucleo(variancia_giroscopio=1e-30, tolerancia_atraso=0))
    assert estado.covariancia_giroscopio[0] >= 1e-12


def teste_correcao_nao_finita_e_rejeitada_sem_consumir_stamp():
    nucleo = novo_nucleo(bias_giroscopio_z=-1e308)
    with pytest.raises(ValueError):
        tratar(nucleo, giro=(0, 0, 1e308))
    assert math.isfinite(tratar(nucleo).giroscopio[2])


@pytest.mark.parametrize("campo,valor", [("tempo", 2**31 * 10**9),
                                         ("agora", 2**31 * 10**9),
                                         ("giro", None), ("aceleracao", 1),
                                         ("giro", (10**400, 0, 0))])
def teste_intervalo_ros_e_formato_dos_vetores(campo, valor):
    nucleo = novo_nucleo(tolerancia_atraso=2**31-1)
    parametros = {campo: valor}
    if campo == "tempo":
        parametros["agora"] = valor
    with pytest.raises(ValueError):
        tratar(nucleo, **parametros)


def teste_defaults_de_covariancia_preservados():
    estado = tratar(novo_nucleo())
    assert estado.covariancia_giroscopio[0] == 0.000016
    assert estado.covariancia_acelerometro[0] == 0.01


@pytest.mark.parametrize("adiantamento", [1, 20_000_000, 50_000_000])
def teste_tolerancia_futura_padrao_para_inversao_dds(adiantamento):
    estado = tratar(novo_nucleo(), tempo=1_000_000_000 + adiantamento)
    assert estado.tempo_ns == 1_000_000_000 + adiantamento


def teste_tolerancia_futura_explicita_configuravel_e_ordenacao():
    nucleo = novo_nucleo(tolerancia_futuro=0.1)
    tratar(nucleo, tempo=1_100_000_000)
    with pytest.raises(ValueError):
        tratar(nucleo, tempo=1_100_000_001)
    with pytest.raises(ValueError):
        tratar(nucleo, tempo=1_090_000_000)
    with pytest.raises(ValueError):
        tratar(novo_nucleo(tolerancia_futuro=0), tempo=1_000_000_001)


@pytest.mark.parametrize("valor", [-1, math.nan, math.inf, True])
def teste_tolerancia_futura_deve_ser_finita_nao_negativa(valor):
    with pytest.raises(ValueError):
        novo_nucleo(tolerancia_futuro=valor)
