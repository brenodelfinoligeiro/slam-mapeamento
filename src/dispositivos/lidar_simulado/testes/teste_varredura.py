import math

import pytest

from lidar_simulado.mundo import Mundo


def mundo_retangular():
    return Mundo((-2, -3, 4, 5), ((-2, -3, 4, -3), (4, -3, 4, 5),
                                   (4, 5, -2, 5), (-2, 5, -2, -3)))


def teste_varredura_geometrica_tem_quatro_raios_sem_duplicar_extremos():
    from lidar_simulado.varredura import GeradorVarredura, ParametrosLidar
    gerador = GeradorVarredura(mundo_retangular(), ParametrosLidar(numero_raios=4, ruido_desvio=0.))
    dados = gerador.varrer((0, 0, 0), (0, 0, 0))
    assert dados.distancias == pytest.approx((2., 3., 4., 5.))
    assert dados.angulo_minimo == -math.pi
    assert dados.angulo_incremento == math.pi / 2
    assert dados.angulo_maximo == math.pi / 2
    assert dados.tempo_incremento == 0.
    assert dados.tempo_varredura == .1


def teste_pose_base_composta_com_deslocamento_e_rotacao_do_sensor():
    from lidar_simulado.varredura import GeradorVarredura, ParametrosLidar
    gerador = GeradorVarredura(mundo_retangular(), ParametrosLidar(numero_raios=4, ruido_desvio=0.))
    dados = gerador.varrer((1, 1, math.pi / 2), (.2, 0, math.pi / 2))
    assert dados.distancias == pytest.approx((3., 3.8, 3., 4.2))


@pytest.mark.parametrize('segmentos,esperado', [
    (((.02, -1, .02, 1), (2, -1, 2, 1)), -math.inf),
    (((.05, -1, .05, 1),), .05),
    (((10, -1, 10, 1),), 10.),
    (((10.01, -1, 10.01, 1),), math.inf),
    ((), math.inf),
])
def teste_alcance_e_oclusao_antes_do_minimo(segmentos, esperado):
    from lidar_simulado.varredura import GeradorVarredura, ParametrosLidar
    mundo = Mundo((-20, -20, 20, 20), segmentos)
    gerador = GeradorVarredura(mundo, ParametrosLidar(numero_raios=4, ruido_desvio=0.))
    assert gerador.varrer((0, 0, 0), (0, 0, 0)).distancias[2] == esperado


def teste_ruido_gaussiano_reproduzivel_sem_alterar_gerador_global():
    import random
    from lidar_simulado.varredura import GeradorVarredura, ParametrosLidar
    parametros = ParametrosLidar(numero_raios=4, ruido_desvio=.003, semente=11)
    primeiro = GeradorVarredura(mundo_retangular(), parametros)
    segundo = GeradorVarredura(mundo_retangular(), parametros)
    estado_global = random.getstate()
    oraculo = random.Random(11)
    esperado = tuple(distancia + oraculo.gauss(0., .003) for distancia in (2., 3., 4., 5.))
    resultado = primeiro.varrer((0, 0, 0), (0, 0, 0)).distancias
    assert resultado == pytest.approx(esperado)
    assert resultado == segundo.varrer((0, 0, 0), (0, 0, 0)).distancias
    assert primeiro.varrer((0, 0, 0), (0, 0, 0)).distancias != resultado
    assert random.getstate() == estado_global


@pytest.mark.parametrize('campo,valor', [
    ('numero_raios', 0), ('numero_raios', -1), ('numero_raios', 3.5),
    ('numero_raios', True), ('frequencia', 0.), ('frequencia', -1.),
    ('frequencia', math.nan), ('frequencia', math.inf), ('frequencia', 1e10),
    ('frequencia', 1e-320), ('alcance_minimo', -.1), ('alcance_maximo', .05),
    ('alcance_maximo', math.inf), ('ruido_desvio', -.001), ('ruido_desvio', math.nan),
    ('semente', 1.2), ('semente', True), ('referencial_laser', ''),
    ('referencial_base', 'map'), ('referencial_base', 'odom'),
    ('referencial_laser', 'base_footprint'), ('referencial_laser', '/laser'),
])
def teste_parametros_invalidos(campo, valor):
    from lidar_simulado.varredura import ParametrosLidar
    with pytest.raises(ValueError):
        ParametrosLidar(**{campo: valor})


@pytest.mark.parametrize('base,extrinseca', [
    ((math.nan, 0, 0), (0, 0, 0)),
    ((0, 0, 0), (math.inf, 0, 0)),
    ((0, 0), (0, 0, 0)),
])
def teste_pose_invalida_nao_produz_scan(base, extrinseca):
    from lidar_simulado.varredura import GeradorVarredura, ParametrosLidar
    with pytest.raises(ValueError):
        GeradorVarredura(mundo_retangular(), ParametrosLidar()).varrer(base, extrinseca)
