"""Varredura instantânea do sensor virtual, sem posição publicada."""

from dataclasses import dataclass
import math
import random

from .geometria import distancia_raio_segmento, numero_finito, vetor_finito


@dataclass(frozen=True)
class ParametrosLidar:
    frequencia: float = 10.
    numero_raios: int = 360
    alcance_minimo: float = .05
    alcance_maximo: float = 10.
    ruido_desvio: float = .003
    semente: int = 11
    referencial_laser: str = 'laser_simulado'
    referencial_base: str = 'base_footprint'

    def __post_init__(self):
        if type(self.numero_raios) is not int or self.numero_raios < 1:
            raise ValueError('numero_raios deve ser inteiro positivo')
        if type(self.semente) is not int:
            raise ValueError('semente deve ser inteira')
        for nome in ('frequencia', 'alcance_minimo', 'alcance_maximo', 'ruido_desvio'):
            if not numero_finito(getattr(self, nome)):
                raise ValueError(f'{nome} deve ser número finito')
        if self.frequencia <= 0 or not math.isfinite(1e9 / self.frequencia) or 1e9 / self.frequencia < 1:
            raise ValueError('frequencia deve ter período finito de ao menos 1 ns')
        if not 0 <= self.alcance_minimo < self.alcance_maximo:
            raise ValueError('Exigido 0 <= alcance_minimo < alcance_maximo')
        if self.ruido_desvio < 0:
            raise ValueError('ruido_desvio não pode ser negativo')
        for nome in ('referencial_base', 'referencial_laser'):
            referencial = getattr(self, nome)
            if (not isinstance(referencial, str) or not referencial
                    or referencial.startswith('/') or any(c.isspace() for c in referencial)
                    or referencial in {'map', 'odom', 'simulacao_mundo'}):
                raise ValueError(f'{nome} deve identificar um frame local do robô')
        if self.referencial_base == self.referencial_laser:
            raise ValueError('Sensor e base devem ter referenciais distintos')


@dataclass(frozen=True)
class Varredura:
    angulo_minimo: float
    angulo_incremento: float
    angulo_maximo: float
    tempo_incremento: float
    tempo_varredura: float
    distancias: tuple


class GeradorVarredura:
    def __init__(self, mundo, parametros):
        self.mundo = mundo
        self.parametros = parametros
        self._aleatorio = random.Random(parametros.semente)

    def varrer(self, pose_base, extrinseca):
        base_x, base_y, base_angulo = vetor_finito(pose_base, 3)
        deslocamento_x, deslocamento_y, rotacao = vetor_finito(extrinseca, 3)
        cosseno, seno = math.cos(base_angulo), math.sin(base_angulo)
        origem = (base_x + cosseno * deslocamento_x - seno * deslocamento_y,
                  base_y + seno * deslocamento_x + cosseno * deslocamento_y)
        angulo_sensor = base_angulo + rotacao
        incremento = 2 * math.pi / self.parametros.numero_raios
        distancias = []
        for indice in range(self.parametros.numero_raios):
            angulo = angulo_sensor - math.pi + indice * incremento
            distancia = min((distancia_raio_segmento(origem, angulo, segmento)
                             for segmento in self.mundo.segmentos), default=math.inf)
            # A primeira superfície oclui as demais mesmo abaixo do alcance mínimo.
            if distancia < self.parametros.alcance_minimo:
                distancia = -math.inf  # REP-117: objeto próximo demais.
            elif distancia > self.parametros.alcance_maximo:
                distancia = math.inf
            else:
                distancia += self._aleatorio.gauss(0., self.parametros.ruido_desvio)
                if distancia < self.parametros.alcance_minimo:
                    distancia = -math.inf
                elif distancia > self.parametros.alcance_maximo:
                    distancia = math.inf
            distancias.append(distancia)
        return Varredura(-math.pi, incremento,
                         -math.pi + (self.parametros.numero_raios - 1) * incremento,
                         0., 1. / self.parametros.frequencia, tuple(distancias))
