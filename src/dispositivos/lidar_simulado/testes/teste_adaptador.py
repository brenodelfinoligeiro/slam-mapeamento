"""Testes unitários do adaptador com E/S substituída, NÃO testes ROS/DDS."""

import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from lidar_simulado.aquisicao import (
    LimitadorAquisicao, extrair_pose_planar, preencher_mensagem_scan,
)
from lidar_simulado.geometria import vetor_finito
from lidar_simulado.mundo import carregar_mundo
from lidar_simulado.varredura import GeradorVarredura, ParametrosLidar


RAIZ = Path(__file__).resolve().parents[1]


@pytest.fixture
def adaptador():
    # Compila a classe de produção sem importar as bibliotecas ROS ausentes.
    arvore = ast.parse((RAIZ / 'lidar_simulado' / 'no_lidar.py').read_text())
    classe = next(no for no in arvore.body if isinstance(no, ast.ClassDef))
    import math
    ambiente = dict(Node=object, Time=lambda: 0, TransformException=LookupError,
                    extrair_pose_planar=extrair_pose_planar, vetor_finito=vetor_finito,
                    preencher_mensagem_scan=preencher_mensagem_scan, math=math,
                    LaserScan=lambda: SimpleNamespace(header=SimpleNamespace()),
                    SetParametersResult=SimpleNamespace)
    exec(compile(ast.Module(body=[classe], type_ignores=[]), '<adaptador-unitario>', 'exec'), ambiente)
    no = ambiente['NoLidarSimulado'].__new__(ambiente['NoLidarSimulado'])
    no._parametros = ParametrosLidar(numero_raios=4, ruido_desvio=0.)
    no._gerador = GeradorVarredura(carregar_mundo(RAIZ / 'configuracao' / 'mundo.yaml'), no._parametros)
    no._limitador = LimitadorAquisicao(10.)
    no._buffer_estatico = Mock()
    no._buffer_estatico.lookup_transform.side_effect = LookupError('ainda sem TF')
    no._publicador = Mock()
    no.get_logger = Mock(return_value=Mock())
    return no


def mensagem_referencia(tempo_ns):
    return SimpleNamespace(
        header=SimpleNamespace(frame_id='simulacao_mundo',
                               stamp=SimpleNamespace(sec=tempo_ns // 1_000_000_000,
                                                     nanosec=tempo_ns % 1_000_000_000)),
        child_frame_id='base_footprint',
        pose=SimpleNamespace(pose=SimpleNamespace(
            position=SimpleNamespace(x=0., y=0., z=0.),
            orientation=SimpleNamespace(x=0., y=0., z=0., w=1.))),
    )


def disponibilizar_extrinseca(no):
    no._buffer_estatico.lookup_transform.side_effect = None
    no._buffer_estatico.lookup_transform.return_value = SimpleNamespace(transform=SimpleNamespace(
        translation=SimpleNamespace(x=0., y=0., z=.2),
        rotation=SimpleNamespace(x=0., y=0., z=0., w=1.)))


def teste_callback_descarta_sem_tf_e_publica_com_aquisicao_original(adaptador):
    adaptador._receber_referencia(mensagem_referencia(0))
    adaptador._publicador.publish.assert_not_called()
    disponibilizar_extrinseca(adaptador)
    mensagem = mensagem_referencia(20_000_000)
    adaptador._receber_referencia(mensagem)
    scan = adaptador._publicador.publish.call_args.args[0]
    assert scan.header.stamp is mensagem.header.stamp
    assert scan.header.frame_id == 'laser_simulado'
    assert scan.ranges == pytest.approx([2.5, 2., 3.5, 3.])
    assert adaptador._buffer_estatico.lookup_transform.call_args.args == ('base_footprint', 'laser_simulado', 0)


def teste_callback_throttle_duplicatas_e_retrocesso(adaptador):
    disponibilizar_extrinseca(adaptador)
    for tempo in (0, 0, 20_000_000, 100_000_000, 120_000_000, 0):
        adaptador._receber_referencia(mensagem_referencia(tempo))
    marcas = [chamada.args[0].header.stamp for chamada in adaptador._publicador.publish.call_args_list]
    assert [(marca.sec, marca.nanosec) for marca in marcas] == [(0, 0), (0, 100_000_000), (0, 0)]


@pytest.mark.parametrize('alteracao', ['pai', 'filho', 'negativo', 'nanosegundos', 'pose'])
def teste_callback_rejeita_referencia_invalida(adaptador, alteracao):
    disponibilizar_extrinseca(adaptador)
    mensagem = mensagem_referencia(0)
    if alteracao == 'pai':
        mensagem.header.frame_id = 'map'
    elif alteracao == 'filho':
        mensagem.child_frame_id = 'odom'
    elif alteracao == 'negativo':
        mensagem.header.stamp.sec = -1
    elif alteracao == 'nanosegundos':
        mensagem.header.stamp.nanosec = 1_000_000_000
    else:
        mensagem.pose.pose.position.x = float('nan')
    adaptador._receber_referencia(mensagem)
    adaptador._publicador.publish.assert_not_called()


def teste_buffer_so_admite_transformacoes_estaticas_locais_validas(adaptador):
    def transformacao(pai, filho, w=1.):
        return SimpleNamespace(header=SimpleNamespace(frame_id=pai), child_frame_id=filho,
                               transform=SimpleNamespace(translation=SimpleNamespace(x=0., y=0., z=.2),
                                                         rotation=SimpleNamespace(x=0., y=0., z=0., w=w)))
    valida = transformacao('lidar_mount_link', 'laser_simulado')
    adaptador._receber_tf_estatica(SimpleNamespace(transforms=[
        transformacao('map', 'odom'), transformacao('odom', 'base_footprint'),
        transformacao('', 'laser'), transformacao('base_footprint', 'invalido', w=0.), valida,
    ]))
    adaptador._buffer_estatico.set_transform_static.assert_called_once_with(valida, 'modelo_virtual')


def teste_protege_use_sim_time(adaptador):
    assert not adaptador._proteger_relogio([SimpleNamespace(name='use_sim_time', value=False)]).successful
    assert adaptador._proteger_relogio([SimpleNamespace(name='use_sim_time', value=True)]).successful
