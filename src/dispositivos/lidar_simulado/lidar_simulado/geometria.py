"""Geometria planar sem dependência do ROS."""

import math


def numero_finito(valor):
    return isinstance(valor, (int, float)) and not isinstance(valor, bool) and math.isfinite(valor)


def vetor_finito(valores, tamanho):
    if not isinstance(valores, (tuple, list)) or len(valores) != tamanho:
        raise ValueError(f'Esperado vetor de {tamanho} números finitos')
    if not all(numero_finito(valor) for valor in valores):
        raise ValueError('Coordenadas devem ser números finitos')
    return tuple(float(valor) for valor in valores)


def distancia_raio_segmento(origem, angulo, segmento):
    origem = vetor_finito(origem, 2)
    segmento = vetor_finito(segmento, 4)
    if not numero_finito(angulo):
        raise ValueError('Ângulo deve ser finito')
    direcao_x, direcao_y = math.cos(angulo), math.sin(angulo)
    x1, y1, x2, y2 = segmento
    vetor_x, vetor_y = x2 - x1, y2 - y1
    delta_x, delta_y = x1 - origem[0], y1 - origem[1]
    determinante = direcao_x * vetor_y - direcao_y * vetor_x
    tolerancia = 1e-12
    if abs(determinante) <= tolerancia * math.hypot(vetor_x, vetor_y):
        perpendicular = delta_x * direcao_y - delta_y * direcao_x
        if abs(perpendicular) > tolerancia * max(1., math.hypot(delta_x, delta_y)):
            return math.inf
        projecao1 = delta_x * direcao_x + delta_y * direcao_y
        projecao2 = projecao1 + vetor_x * direcao_x + vetor_y * direcao_y
        inicio, fim = sorted((projecao1, projecao2))
        return max(0., inicio) if fim >= -tolerancia else math.inf
    distancia = (delta_x * vetor_y - delta_y * vetor_x) / determinante
    proporcao = (delta_x * direcao_y - delta_y * direcao_x) / determinante
    if distancia >= -tolerancia and -tolerancia <= proporcao <= 1 + tolerancia:
        return max(0., distancia)
    return math.inf
