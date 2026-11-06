from pathlib import Path

import pytest
import yaml


RAIZ = Path(__file__).resolve().parents[1]


def teste_carrega_mundo_instalavel_assimetrico_com_corredor_livre():
    from lidar_simulado.mundo import carregar_mundo
    caminho = RAIZ / 'configuracao' / 'mundo.yaml'
    dados = yaml.safe_load(caminho.read_text())
    assert set(dados) == {'limites', 'segmentos'}
    mundo = carregar_mundo(caminho)
    assert mundo.limites == (-2.5, -2., 3.5, 3.)
    assert len(mundo.segmentos) >= 16
    contorno = {(-2.5, -2., 3.5, -2.), (3.5, -2., 3.5, 3.),
                (3.5, 3., -2.5, 3.), (-2.5, 3., -2.5, -2.)}
    assert contorno <= set(mundo.segmentos)
    for x1, y1, x2, y2 in mundo.segmentos:
        # Cada obstáculo inteiro fica num semiplano externo ao corredor.
        assert max(x1, x2) < -.3 or min(x1, x2) > 1.3 or max(y1, y2) < -.3 or min(y1, y2) > 1.3


@pytest.mark.parametrize('dados', [
    {}, {'limites': [0, 0, 1, 1]},
    {'limites': [0, 0, 1, 1], 'segmentos': [], 'extra': 1},
    {'limites': [1, 0, 0, 1], 'segmentos': []},
    {'limites': [0, 0, float('nan'), 1], 'segmentos': []},
    {'limites': [False, 0, 1, 1], 'segmentos': []},
    {'limites': [0, 0, 1, 1], 'segmentos': [[0, 0, 2, 1]]},
    {'limites': [0, 0, 1, 1], 'segmentos': [[0, 0, 1]]},
    {'limites': [0, 0, 1, 1], 'segmentos': 'incorreto'},
])
def teste_rejeita_mundo_invalido(tmp_path, dados):
    from lidar_simulado.mundo import carregar_mundo
    caminho = tmp_path / 'mundo.yaml'
    caminho.write_text(yaml.safe_dump(dados))
    with pytest.raises(ValueError):
        carregar_mundo(caminho)
