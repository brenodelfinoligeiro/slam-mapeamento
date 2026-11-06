"""Admissão por carimbo da fonte e conversão planar, independentes do ROS."""

import math

from .geometria import vetor_finito
from .varredura import ParametrosLidar


class LimitadorAquisicao:
    def __init__(self, frequencia):
        parametros = ParametrosLidar(frequencia=frequencia)
        self._periodo_ns = round(1e9 / parametros.frequencia)
        self._ultima_referencia = None
        self._ultima_aquisicao = None

    def admitir(self, tempo_ns, pronto):
        if type(tempo_ns) is not int or tempo_ns < 0:
            raise ValueError('Carimbo deve ser inteiro não negativo em nanossegundos')
        if self._ultima_referencia is not None:
            if tempo_ns == self._ultima_referencia:
                return False
            if tempo_ns < self._ultima_referencia:
                self._ultima_aquisicao = None
        self._ultima_referencia = tempo_ns
        if not pronto:
            return False
        if self._ultima_aquisicao is not None and tempo_ns - self._ultima_aquisicao < self._periodo_ns:
            return False
        self._ultima_aquisicao = tempo_ns
        return True


def extrair_pose_planar(posicao, quaternion):
    posicao = vetor_finito(posicao, 3)
    quaternion = vetor_finito(quaternion, 4)
    norma = math.hypot(*quaternion)
    if not math.isfinite(norma) or norma < 1e-15:
        raise ValueError('Quaternion sem orientação válida')
    x, y, z, w = (valor / norma for valor in quaternion)
    if abs(x) > 1e-6 or abs(y) > 1e-6:
        raise ValueError('O sensor geométrico 2D exige orientação planar')
    angulo = math.atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))
    return posicao[0], posicao[1], angulo


def preencher_mensagem_scan(mensagem, marca, dados, parametros):
    mensagem.header.stamp = marca
    mensagem.header.frame_id = parametros.referencial_laser
    mensagem.angle_min = dados.angulo_minimo
    mensagem.angle_max = dados.angulo_maximo
    mensagem.angle_increment = dados.angulo_incremento
    mensagem.time_increment = dados.tempo_incremento
    mensagem.scan_time = dados.tempo_varredura
    mensagem.range_min = float(parametros.alcance_minimo)
    mensagem.range_max = float(parametros.alcance_maximo)
    mensagem.ranges = list(dados.distancias)
    mensagem.intensities = []
