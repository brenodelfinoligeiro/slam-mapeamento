"""Contrato puro do gate, sem ROS, hardware ou relógios reais."""
from pathlib import Path
import importlib
import pytest


def teste_retrocesso_visto_em_callback_de_sensor_nao_desaparece_entre_ticks():
    gate = ativo()
    gate.receber_sensor('scan', 10_100_000_000, True, 10_100_000_000, 1.1)
    gate.receber_sensor('scan', 10_100_000_000, True, 9_900_000_000, 1.2)
    preparar(gate, 10_200_000_000, 1.3)
    assert not gate.avaliar(10_200_000_000, 1.3)['autorizado']
    assert gate.parar_pendente


@pytest.mark.parametrize('delta,admitido', [(50_000_000, True), (50_000_001, False),
                                          (-300_000_000, True), (-300_000_001, False)])
def teste_limites_inteiros_de_futuro_e_prazo_do_comando(delta, admitido):
    gate = ativo()
    preparar(gate, 10_450_000_000, 1.45)
    assert gate.receber_comando(.2, 0., 10_450_000_000 + delta,
                                10_450_000_000, 1.45) is admitido
    assert gate.parar_pendente is (not admitido)


def teste_clock_perdido_apos_armamento_sem_objetivo_exige_nova_selecao():
    gate = criar()
    preparar(gate)
    armar(gate)
    gate.avaliar(0, 1.1)
    assert not gate.armado and gate.parar_pendente


def teste_inicializacao_incompleta_sem_objetivo_nao_dispara_parada():
    gate = criar()
    armar(gate)
    assert not gate.avaliar(10_100_000_000, 1.1)['pronto']
    assert not gate.parar_pendente
    objetivo(gate)
    assert gate.parar_pendente


def teste_modo_nao_pode_mudar_sem_nova_geracao():
    gate = ativo()
    gate.receber_estado({'modo': 'manual', 'geracao': 1, 'ativo': False,
                         'motivo': 'selecao_explicita'}, 10_200_000_000, 1.2)
    assert not gate.armado
    gate.receber_estado({'modo': 'autonomo', 'geracao': 1, 'ativo': False,
                         'motivo': 'selecao_explicita'}, 10_210_000_000, 1.21)
    assert not gate.armado


def teste_diagnostico_preserva_causa_da_falha_apos_resposta_arbitro_parado():
    gate = ativo()
    gate.rejeitar_comando()
    gate.receber_estado({'modo': 'parado', 'geracao': 2, 'ativo': False,
                         'motivo': 'parada_solicitada'}, 10_200_000_000, 1.2)
    estado = gate.avaliar(10_200_000_000, 1.2)
    assert estado['ultima_falha'] == 'comando_invalido'
    assert not estado['armado'] and not estado['aceita_objetivo']


@pytest.mark.parametrize('lista', [[('futuro', 20_000_000_000, 2)],
                                  [('a', 10_100_000_000, 2), ('b', 10_110_000_000, 2)],
                                  [('a', 10_100_000_000, 99)],
                                  [('a', 0, 2)]])
def teste_primeiro_status_invalido_ou_ambiguo_nao_cria_autoridade(lista):
    gate = criar()
    preparar(gate)
    armar(gate)
    gate.receber_objetivos(lista, 10_200_000_000, 1.2)
    assert gate.objetivo is None and gate.cancelar_pendente


def teste_sensor_retrogrado_nao_renova_lease():
    gate = ativo()
    gate.receber_sensor('scan', 9_999_999_999, True, 10_100_000_000, 1.1)
    assert gate.parar_pendente and gate.objetivo is None


def teste_clock_retrocede_durante_nova_selecao_nao_rearma():
    gate = ativo()
    gate.avaliar(10_100_000_000, 1.1)
    armar(gate, 2, 9_000_000_000, 1.2)
    assert not gate.armado and gate.parar_pendente


def teste_repeticao_de_comando_ja_expirado_so_descarta_sem_abortar_planejamento():
    gate = ativo()
    assert gate.receber_comando(.2, 0., 10_200_000_000, 10_200_000_000, 1.2)
    preparar(gate, 10_200_000_000, 1.4)
    assert not gate.avaliar(10_200_000_000, 1.51)['comando_valido']
    assert not gate.receber_comando(.2, 0., 10_200_000_000, 10_200_000_000, 1.52)
    assert not gate.parar_pendente


@pytest.mark.parametrize('objetivos', [[('futuro', 20_000_000_000, 2)],
                                       [('a', 10_200_000_000, 2), ('b', 10_210_000_000, 2)],
                                       [('nulo', 0, 2)]])
def teste_status_ambiguo_ou_carimbo_invalido_nunca_admite(objetivos):
    gate = ativo()
    gate.receber_objetivos(objetivos, 10_250_000_000, 1.25)
    assert gate.objetivo is None and gate.cancelar_pendente
    assert not gate.avaliar(10_250_000_000, 1.25)['autorizado']


def teste_objetivo_na_pendencia_cancelamento_exige_outro_apos_confirmacao():
    gate = criar()
    preparar(gate)
    gate.receber_estado({'modo': 'autonomo', 'geracao': 1, 'ativo': False,
                         'motivo': 'selecao_explicita'}, 10 * SEGUNDO, 1.)
    token = gate.sequencia_cancelamento
    objetivo(gate)
    gate.confirmar_cancelamento(token, 10_110_000_000, 1.11)
    assert gate.cancelar_pendente
    gate.confirmar_cancelamento(gate.sequencia_cancelamento, 10_120_000_000, 1.12)
    objetivo(gate, ros=10_130_000_000, parede=1.13)
    assert not gate.avaliar(10_130_000_000, 1.13)['autorizado']


def teste_replay_de_geracao_anterior_nao_rearma_apos_falha():
    gate = ativo()
    gate.rejeitar_comando()
    gate.confirmar_parada(gate.sequencia_parada)
    gate.confirmar_cancelamento(gate.sequencia_cancelamento, 10_200_000_000, 1.2)
    armar(gate, 0, 10_210_000_000, 1.21)
    assert not gate.armado


@pytest.mark.parametrize('parametro,valor', [('prazo_sensores', 0.), ('prazo_tf', -1.),
                                           ('prazo_comando', float('nan')),
                                           ('tolerancia_futuro', -1.),
                                           ('tolerancia_tf_futuro', float('inf'))])
def teste_parametros_invalidos_rejeitados(parametro, valor):
    classe = type(criar())
    with pytest.raises(ValueError):
        classe(**{parametro: valor})


def teste_prazos_configuraveis_e_diagnostico_explica_bloqueio():
    gate = type(criar())(prazo_sensores=.1, prazo_tf=.1, prazo_comando=.1,
                         tolerancia_futuro=.01, tolerancia_tf_futuro=.02)
    preparar(gate)
    armar(gate)
    objetivo(gate, carimbo=10_050_000_000, ros=10_050_000_000, parede=1.05)
    estado = gate.avaliar(10_110_000_000, 1.11)
    assert not estado['pronto'] and estado['bloqueado']
    assert estado['requer_nova_selecao']
    assert estado['cancelamento_pendente'] and estado['parada_pendente']
    assert estado['prerequisitos']['mapa']


@pytest.mark.parametrize('entrada', [(.2, 0., 10_600_000_000), (.2, 0., 9_000_000_000),
                                    (float('nan'), 0., 10_200_000_000),
                                    (.2, float('inf'), 10_200_000_000), (.2, 0., 0)])
def teste_comando_ativo_invalido_trava(entrada):
    gate = ativo()
    assert not gate.receber_comando(*entrada, 10_200_000_000, 1.2)
    # Comando anterior ao objetivo é apenas descartado; não pertence à época ativa.
    if entrada[2] > 0 and entrada[2] <= 10_100_000_000:
        assert not gate.parar_pendente
    else:
        assert gate.parar_pendente and gate.cancelar_pendente


def teste_mesmo_carimbo_com_comando_diferente_revoga_permissao():
    gate = ativo()
    assert gate.receber_comando(.2, 0., 10_200_000_000, 10_200_000_000, 1.2)
    assert not gate.receber_comando(.4, 0., 10_200_000_000, 10_200_000_000, 1.21)
    assert gate.parar_pendente


def teste_invalidacao_estrutural_ativa_e_imediata():
    gate = ativo()
    gate.rejeitar_comando()
    assert gate.parar_pendente and gate.objetivo is None


@pytest.mark.parametrize('nome', ['scan', 'odom', 'tf'])
def teste_sensor_invalido_ativo_trava_sem_esperar_tick(nome):
    gate = ativo()
    gate.receber_sensor(nome, 10_200_000_000, False, 10_200_000_000, 1.2)
    assert gate.parar_pendente and gate.objetivo is None


def teste_tf_futuro_aceita_025_mas_rejeita_alem_e_mapa_estatico_nao_expira():
    gate = ativo()
    gate.receber_sensor('tf', 10_350_000_000, True, 10_100_000_000, 1.1)
    assert gate.avaliar(10_100_000_000, 1.1)['autorizado']
    gate.receber_sensor('tf', 10_350_000_001, True, 10_100_000_000, 1.1)
    assert not gate.avaliar(10_100_000_000, 1.1)['autorizado']
    assert gate.parar_pendente


def teste_somente_selecao_nova_depois_de_parada_confirmada_rearma():
    gate = ativo()
    gate.rejeitar_comando()
    gate.receber_estado({'modo': 'autonomo', 'geracao': 2, 'ativo': False,
                         'motivo': 'selecao_explicita'}, 10_200_000_000, 1.2)
    assert not gate.armado
    gate.confirmar_parada(gate.sequencia_parada)
    gate.confirmar_cancelamento(gate.sequencia_cancelamento, 10_210_000_000, 1.21)
    # Repetir mesmo estado, ainda que sensores recuperem, não rearma.
    gate.receber_estado({'modo': 'autonomo', 'geracao': 2, 'ativo': False,
                         'motivo': 'selecao_explicita'}, 10_220_000_000, 1.22)
    assert not gate.armado
    armar(gate, 3, 10_230_000_000, 1.23)
    preparar(gate, 10_240_000_000, 1.24)
    objetivo(gate, 'novo2', 10_250_000_000, 10_250_000_000, 1.25)
    assert gate.avaliar(10_250_000_000, 1.25)['autorizado']


@pytest.mark.parametrize('estado', [{}, {'modo': 'autonomo', 'geracao': True},
                                  {'modo': 'invalido', 'geracao': 2},
                                  {'modo': 'autonomo', 'geracao': -1}])
def teste_estado_arbitro_invalido_trava(estado):
    gate = ativo()
    gate.receber_estado(estado, 10_200_000_000, 1.2)
    assert gate.objetivo is None and gate.parar_pendente


@pytest.mark.parametrize('sensor', ['scan', 'odom', 'tf'])
def teste_carimbo_sensor_duplicado_nao_renova_lease_com_clock_pausado(sensor):
    gate = ativo()
    gate.receber_sensor(sensor, 10 * SEGUNDO, True, 10_100_000_000, 1.4)
    for nome in ('scan', 'odom', 'tf'):
        if nome != sensor:
            gate.receber_sensor(nome, 10_100_000_000, True, 10_100_000_000, 1.4)
    estado = gate.avaliar(10_100_000_000, 1.51)
    assert not estado['autorizado']
    assert gate.parar_pendente
    assert estado['motivo'] == sensor + '_indisponivel'


def teste_comando_duplicado_nao_republica_ou_renova_lease_e_expiracao_nao_aborta():
    gate = ativo()
    assert gate.receber_comando(.2, 0., 10_200_000_000, 10_200_000_000, 1.2)
    assert not gate.receber_comando(.2, 0., 10_200_000_000, 10_200_000_000, 1.4)
    preparar(gate, 10_200_000_000, 1.4)
    estado = gate.avaliar(10_200_000_000, 1.51)
    assert not estado['comando_valido']
    assert not gate.parar_pendente and not gate.cancelar_pendente
    assert gate.objetivo is not None


def teste_planejamento_longo_sem_primeiro_comando_nao_dispara_parada():
    gate = ativo()
    for passo in range(1, 101):
        ros = 10_100_000_000 + passo * 100_000_000
        parede = 1.1 + passo * .1
        preparar(gate, ros, parede)
        estado = gate.avaliar(ros, parede)
        assert estado['autorizado'] and not estado['comando_valido']
        assert not gate.parar_pendente


@pytest.mark.parametrize('ros,parede', [(0, 1.2), (10_000_000_000, 1.2),
                                      (10_200_000_000, .9), (10_200_000_000, float('nan'))])
def teste_clock_invalido_ou_retrocesso_trava_mesmo_recuperando(ros, parede):
    gate = ativo()
    gate.avaliar(10_100_000_000, 1.1)
    estado = gate.avaliar(ros, parede)
    assert not estado['autorizado']
    assert gate.parar_pendente and gate.cancelar_pendente
    preparar(gate, 10_300_000_000, 1.3)
    assert not gate.avaliar(10_300_000_000, 1.3)['autorizado']


def ativo():
    gate = criar()
    preparar(gate)
    armar(gate)
    objetivo(gate)
    return gate


@pytest.mark.parametrize('sensor', ['scan', 'odom', 'tf'])
def teste_perda_sensor_ativo_trava_cancela_para_e_recuperacao_nao_rearma(sensor):
    gate = ativo()
    # Mantém os outros sensores novos, perde somente aquele sob ensaio.
    for nome in ('scan', 'odom', 'tf'):
        if nome != sensor:
            gate.receber_sensor(nome, 10_600_000_000, True, 10_600_000_000, 1.6)
    estado = gate.avaliar(10_600_000_000, 1.6)
    assert estado['autorizado'] is False
    assert gate.parar_pendente and gate.cancelar_pendente
    assert estado['motivo'] == sensor + '_indisponivel'
    preparar(gate, 10_610_000_000, 1.61)
    assert not gate.avaliar(10_610_000_000, 1.61)['autorizado']
    objetivo(gate, 'outro', 10_620_000_000, 10_620_000_000, 1.62)
    assert gate.objetivo is None


def criar():
    caminho = Path(__file__).parents[1] / 'navegacao_autonoma' / 'protecao.py'
    assert caminho.is_file(), 'Núcleo de proteção ainda não implementado'
    return importlib.import_module('navegacao_autonoma.protecao').ProtecaoAutonomia()


def teste_inicia_bloqueado_sem_disparar_parada_por_inicializacao():
    gate = criar()
    estado = gate.avaliar(0, 1.0)
    assert estado['pronto'] is False
    assert estado['autorizado'] is False
    assert estado['objetivo'] is None
    assert gate.parar_pendente is False
    assert gate.cancelar_pendente is False


SEGUNDO = 1_000_000_000


def preparar(gate, ros=10 * SEGUNDO, parede=1.0):
    gate.receber_mapa(True)
    for sensor in ('scan', 'odom', 'tf'):
        gate.receber_sensor(sensor, ros, True, ros, parede)


def armar(gate, geracao=1, ros=10 * SEGUNDO, parede=1.0):
    gate.receber_estado({'modo': 'autonomo', 'ativo': False,
                         'motivo': 'selecao_explicita', 'geracao': geracao}, ros, parede)
    gate.confirmar_cancelamento(gate.sequencia_cancelamento, ros, parede)


def objetivo(gate, identidade='novo', carimbo=10_100_000_000,
             ros=10_100_000_000, parede=1.1):
    gate.receber_objetivos([(identidade, carimbo, 2)], ros, parede)


def teste_prontidao_independe_de_objetivo_e_comando_novo_exige_armamento():
    gate = criar()
    preparar(gate)
    assert gate.avaliar(10 * SEGUNDO, 1.0)['pronto'] is True
    assert not gate.receber_comando(.2, .1, 10 * SEGUNDO, 10 * SEGUNDO, 1.0)
    armar(gate)
    objetivo(gate)
    assert gate.avaliar(10_100_000_000, 1.1)['autorizado']
    assert gate.receber_comando(.2, .1, 10_200_000_001, 10_200_000_001, 1.2)
    assert gate.avaliar(10_200_000_001, 1.2)['comando_valido']


@pytest.mark.parametrize('modo', ['manual', 'parado', 'autonomo'])
def teste_nova_epoca_cancela_neutraliza_e_objetivo_antigo_nao_ressuscita(modo):
    gate = ativo()
    gate.receber_comando(.2, .1, 10_200_000_000, 10_200_000_000, 1.2)
    gate.receber_estado({'modo': modo, 'ativo': False, 'motivo': 'selecao_explicita',
                         'geracao': 2}, 10_250_000_000, 1.25)
    assert gate.cancelar_pendente
    assert gate.comando is None and gate.objetivo is None
    gate.confirmar_cancelamento(gate.sequencia_cancelamento, 10_260_000_000, 1.26)
    objetivo(gate, ros=10_270_000_000, parede=1.27)
    assert gate.objetivo is None
    # Mesmo UUID com carimbo adulterado também não pode reaparecer.
    objetivo(gate, carimbo=10_280_000_000, ros=10_280_000_000, parede=1.28)
    assert gate.objetivo is None
    if modo != 'autonomo':
        assert gate.cancelar_pendente


def teste_objetivo_recebido_manual_e_cancelado_inclusive_durante_rpc():
    gate = criar()
    gate.receber_estado({'modo': 'manual', 'ativo': False, 'motivo': 'inicializacao',
                         'geracao': 0}, 10 * SEGUNDO, 1.)
    token = gate.sequencia_cancelamento
    objetivo(gate)
    assert gate.objetivo is None and gate.cancelar_pendente
    gate.confirmar_cancelamento(token, 10_110_000_000, 1.11)
    assert gate.cancelar_pendente, 'resposta antiga não confirma objetivo que chegou depois'


@pytest.mark.parametrize('status', [3, 4, 5, 6, None])
def teste_objetivo_terminal_ou_ausente_neutraliza_sem_rejuvenescer(status):
    gate = ativo()
    gate.receber_comando(.2, 0., 10_200_000_000, 10_200_000_000, 1.2)
    lista = [] if status is None else [('novo', 10_100_000_000, status)]
    gate.receber_objetivos(lista, 10_250_000_000, 1.25)
    assert gate.objetivo is None and gate.comando is None
    assert gate.cancelar_pendente
    gate.confirmar_cancelamento(gate.sequencia_cancelamento, 10_260_000_000, 1.26)
    objetivo(gate, ros=10_270_000_000, parede=1.27)
    assert gate.objetivo is None
