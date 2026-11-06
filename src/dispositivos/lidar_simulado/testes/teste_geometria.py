import importlib
import math

import pytest


def teste_intersecao_frontal_retorna_distancia():
    modulo = importlib.import_module('lidar_simulado.geometria')
    assert modulo.distancia_raio_segmento((0., 0.), 0., (2., -1., 2., 1.)) == 2.


@pytest.mark.parametrize('origem,angulo,segmento,esperado', [
    ((0, 0), 0, (2, 0, 4, 0), 2),
    ((0, 0), 0, (4, 0, 2, 0), 2),
    ((0, 0), 0, (-1, 0, 2, 0), 0),
    ((0, 0), 0, (-4, 0, -2, 0), math.inf),
    ((0, 0), 0, (1, 1, 3, 1), math.inf),
    ((0, 0), 0, (-2, -1, -2, 1), math.inf),
    ((0, 0), 0, (2, 0, 2, 0), 2),
    ((0, 0), 0, (2, 0, 2, 2), 2),
    ((-3, -2), math.pi / 2, (-4, 1, -3, 1), 3),
    ((0, 0), 0, (2, -1e-10, 2, 1e-10), 2),
    ((0, 0), 0, (1, 1e-8, 2, 1e-8 + 1e-15), math.inf),
])
def teste_intersecao_limites_geometricos(origem, angulo, segmento, esperado):
    from lidar_simulado.geometria import distancia_raio_segmento
    assert distancia_raio_segmento(origem, angulo, segmento) == pytest.approx(esperado)


@pytest.mark.parametrize('origem,angulo,segmento', [
    ((math.nan, 0), 0, (1, -1, 1, 1)),
    ((0, 0), math.inf, (1, -1, 1, 1)),
    ((0, 0), 0, (math.nan, -1, 1, 1)),
    ((0, 0), 0, (1, -1, 1)),
    ((True, 0), 0, (1, -1, 1, 1)),
])
def teste_intersecao_rejeita_entrada_invalida(origem, angulo, segmento):
    from lidar_simulado.geometria import distancia_raio_segmento
    with pytest.raises(ValueError):
        distancia_raio_segmento(origem, angulo, segmento)
