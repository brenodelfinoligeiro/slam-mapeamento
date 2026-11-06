"""Verifica os recursos destinados ao share e o executável ament_python."""
from pathlib import Path
import runpy
import setuptools

RAIZ = Path(__file__).resolve().parents[1]


def teste_setup_instala_recursos_e_executavel(monkeypatch):
    configuracao = {}
    monkeypatch.chdir(RAIZ)
    monkeypatch.setattr(setuptools, 'setup', lambda **kwargs: configuracao.update(kwargs))
    runpy.run_path(str(RAIZ / 'setup.py'))
    destinos = dict(configuracao['data_files'])
    assert destinos['share/ament_index/resource_index/packages'] == ['recursos/mapeamento_slam']
    for subpasta, esperados in {
            'inicializacao': {'slam.launch.py', 'slam_simulado.launch.py'},
            'configuracao': {'slam.yaml'}, 'visualizacao': {'slam.rviz'}}.items():
        assert {Path(p).name for p in destinos[f'share/mapeamento_slam/{subpasta}']} == esperados
    assert configuracao['entry_points']['console_scripts'] == [
        'salvar_mapa = mapeamento_slam.salvar_mapa:main']
    assert configuracao['extras_require']['test'] == ['pytest']
    assert (RAIZ / 'recursos/mapeamento_slam').is_file()
