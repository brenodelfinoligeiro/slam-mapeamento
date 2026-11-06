"""Contrato compartilhado do cenário geométrico; não publica OccupancyGrid."""

from dataclasses import dataclass
from pathlib import Path

import yaml

from .geometria import vetor_finito


@dataclass(frozen=True)
class Mundo:
    limites: tuple
    segmentos: tuple

    def __post_init__(self):
        limites = vetor_finito(self.limites, 4)
        minimo_x, minimo_y, maximo_x, maximo_y = limites
        if minimo_x >= maximo_x or minimo_y >= maximo_y:
            raise ValueError('Limites devem formar um retângulo de área positiva')
        if not isinstance(self.segmentos, (tuple, list)):
            raise ValueError('segmentos deve ser uma sequência')
        segmentos = tuple(vetor_finito(segmento, 4) for segmento in self.segmentos)
        for x1, y1, x2, y2 in segmentos:
            if not (minimo_x <= x1 <= maximo_x and minimo_x <= x2 <= maximo_x
                    and minimo_y <= y1 <= maximo_y and minimo_y <= y2 <= maximo_y):
                raise ValueError('Segmento fora dos limites do mundo')
        object.__setattr__(self, 'limites', limites)
        object.__setattr__(self, 'segmentos', segmentos)


def carregar_mundo(caminho):
    try:
        dados = yaml.safe_load(Path(caminho).read_text(encoding='utf-8'))
    except yaml.YAMLError as erro:
        raise ValueError('YAML do mundo inválido') from erro
    if not isinstance(dados, dict) or set(dados) != {'limites', 'segmentos'}:
        raise ValueError('Mundo exige somente limites e segmentos')
    return Mundo(dados['limites'], dados['segmentos'])
