"""Exercita objetos launch reais, sem iniciar processos nem simular dados ROS."""
import importlib.util
from pathlib import Path
import pytest

pytest.importorskip('launch_ros', reason='requer launch ROS 2 instalado')
from launch import LaunchContext
from launch_ros.actions import LifecycleNode, Node

RAIZ = Path(__file__).resolve().parents[1]


def carregar(nome):
    especificacao = importlib.util.spec_from_file_location(nome, RAIZ / 'inicializacao' / nome)
    modulo = importlib.util.module_from_spec(especificacao)
    especificacao.loader.exec_module(modulo)
    return modulo


def contexto(modo='mapeamento', grafo=''):
    resultado = LaunchContext()
    resultado.launch_configurations.update({'modo': modo, 'arquivo_grafo': grafo,
                                          'rviz': 'false', 'arquivo_mundo': ''})
    return resultado


@pytest.mark.parametrize('arquivo', ['slam.launch.py', 'slam_simulado.launch.py'])
@pytest.mark.parametrize('modo,grafo', [('invalido', ''), ('localizacao', ''), ('localizacao', '/ausente')])
def teste_launch_invalido_falha_antes_de_criar_nos(monkeypatch, arquivo, modo, grafo):
    modulo = carregar(arquivo)
    def proibido(*args, **kwargs):
        pytest.fail('validação deveria anteceder descoberta de pacotes e criação de nós')
    monkeypatch.setattr(modulo, 'get_package_share_directory', proibido)
    monkeypatch.setattr(modulo, 'Node', proibido)
    if hasattr(modulo, 'LifecycleNode'):
        monkeypatch.setattr(modulo, 'LifecycleNode', proibido)
    with pytest.raises(ValueError):
        (modulo.configurar if arquivo == 'slam.launch.py' else modulo.compor)(contexto(modo, grafo))


@pytest.mark.parametrize('modo', ['mapeamento', 'localizacao'])
def teste_launch_tecnico_constroi_lifecycle_real(monkeypatch, tmp_path, modo):
    modulo = carregar('slam.launch.py')
    grafo = ''
    if modo == 'localizacao':
        grafo = str(tmp_path / 'sala')
        for extensao in ('.posegraph', '.data'):
            Path(grafo + extensao).write_bytes(b'fixture nao desserializada neste teste')
    monkeypatch.setattr(modulo, 'get_package_share_directory', lambda _: str(RAIZ))
    acoes = modulo.configurar(contexto(modo, grafo))
    assert len([a for a in acoes if isinstance(a, LifecycleNode)]) == 2
    assert len([a for a in acoes if isinstance(a, Node)]) == 3


def teste_composicao_resolve_yaml_instalado_do_lidar(monkeypatch, tmp_path):
    modulo = carregar('slam_simulado.launch.py')
    pasta_lidar = tmp_path / 'lidar_simulado'
    (pasta_lidar / 'configuracao').mkdir(parents=True)
    (pasta_lidar / 'configuracao/mundo.yaml').write_text('cenario: teste\n')
    monkeypatch.setattr(modulo, 'get_package_share_directory',
                        lambda pacote: str(pasta_lidar if pacote == 'lidar_simulado' else RAIZ))
    acoes = modulo.compor(contexto())
    assert len(acoes) == 5
    assert len([a for a in acoes if isinstance(a, Node)]) == 3


def teste_include_da_base_nao_sobrescreve_rviz_do_slam(monkeypatch,tmp_path):
    from launch import LaunchService,LaunchDescription
    from launch.actions import SetLaunchConfiguration,OpaqueFunction
    modulo=carregar('slam_simulado.launch.py')
    base=tmp_path/'base';(base/'inicializacao').mkdir(parents=True)
    (base/'inicializacao/simulacao.launch.py').write_text("from launch import LaunchDescription\nfrom launch.actions import DeclareLaunchArgument\ndef generate_launch_description():\n    return LaunchDescription([DeclareLaunchArgument('rviz',default_value='true')])\n")
    lidar=tmp_path/'lidar';(lidar/'configuracao').mkdir(parents=True)
    (lidar/'configuracao/mundo.yaml').write_text('limites: [0,0,1,1]\nsegmentos: []\n')
    monkeypatch.setattr(modulo,'get_package_share_directory',lambda pacote:str(base if pacote=='navegacao_simulada' else lidar if pacote=='lidar_simulado' else RAIZ))
    ctx=contexto();ctx.launch_configurations['rviz']='true'
    acao_base=modulo.compor(ctx)[0]
    observados=[]
    def observar(c):observados.append(c.launch_configurations['rviz'])
    servico=LaunchService(argv=[])
    servico.include_launch_description(LaunchDescription([SetLaunchConfiguration('rviz','true'),acao_base,OpaqueFunction(function=observar)]))
    assert servico.run()==0
    assert observados==['true']
