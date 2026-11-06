"""Correção estática configurada de IMU, sem estimativa de orientação."""

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class LeituraImu:
    tempo_ns: int
    frame_id: str
    giroscopio: tuple[float, float, float]
    acelerometro: tuple[float, float, float]
    covariancia_giroscopio: tuple[float, ...]
    covariancia_acelerometro: tuple[float, ...]
    covariancia_orientacao: tuple[float, ...] = (-1.0,) + (0.0,) * 8


def _finito(nome, valor):
    if type(valor) not in (int, float):
        raise ValueError(f"{nome} deve ser numérico e finito")
    try:
        convertido = float(valor)
    except OverflowError as erro:
        raise ValueError(f"{nome} excede o intervalo numérico") from erro
    if not math.isfinite(convertido):
        raise ValueError(f"{nome} deve ser finito")
    return convertido


class ProcessamentoImu:
    def __init__(self, bias_giroscopio_z=0.01, variancia_giroscopio=0.000016,
                 variancia_acelerometro=0.01, tolerancia_atraso=0.3,
                 tolerancia_futuro=0.05):
        self.bias_giroscopio_z = _finito("bias_giroscopio_z", bias_giroscopio_z)
        variancia_giroscopio = _finito("variancia_giroscopio", variancia_giroscopio)
        variancia_acelerometro = _finito("variancia_acelerometro", variancia_acelerometro)
        if variancia_giroscopio <= 0 or variancia_acelerometro <= 0:
            raise ValueError("Variâncias devem ser positivas")
        variancia_giroscopio = max(1e-12, variancia_giroscopio)
        variancia_acelerometro = max(1e-12, variancia_acelerometro)
        tolerancia_atraso = _finito("tolerancia_atraso", tolerancia_atraso)
        if not 0 <= tolerancia_atraso <= 2**31 - 1:
            raise ValueError("Tolerância fora do intervalo ROS")
        self.tolerancia_ns = round(tolerancia_atraso * 1e9)
        tolerancia_futuro = _finito("tolerancia_futuro", tolerancia_futuro)
        if not 0 <= tolerancia_futuro <= 2**31 - 1:
            raise ValueError("Tolerância futura fora do intervalo ROS")
        self.tolerancia_futuro_ns = round(tolerancia_futuro * 1e9)
        self._ultimo_tempo = None
        self._ultimo_agora = None
        self.covariancia_giroscopio = (variancia_giroscopio, 0.0, 0.0, 0.0,
                                      variancia_giroscopio, 0.0, 0.0, 0.0,
                                      variancia_giroscopio)
        self.covariancia_acelerometro = (variancia_acelerometro, 0.0, 0.0, 0.0,
                                        variancia_acelerometro, 0.0, 0.0, 0.0,
                                        variancia_acelerometro)

    def processar(self, tempo_ns, agora_ns, giroscopio, acelerometro,
                  frame_id="imu_mount_link"):
        if (type(tempo_ns) is not int or type(agora_ns) is not int
                or not 0 < tempo_ns < 2**31 * 10**9
                or not 0 < agora_ns < 2**31 * 10**9):
            raise ValueError("Tempo ROS não iniciado ou inválido")
        if self._ultimo_agora is not None and agora_ns < self._ultimo_agora:
            self._ultimo_tempo = None
        self._ultimo_agora = agora_ns
        if frame_id != "imu_mount_link":
            raise ValueError("Frame deve ser imu_mount_link; não há transformação implícita")
        for vetor in (giroscopio, acelerometro):
            if not isinstance(vetor, (tuple, list)) or len(vetor) != 3:
                raise ValueError("IMU exige três componentes finitas em cada vetor")
            for componente in vetor:
                _finito("componente IMU", componente)
        # /clock e a aquisição podem chegar invertidos por DDS.
        if not -self.tolerancia_futuro_ns <= agora_ns - tempo_ns <= self.tolerancia_ns:
            raise ValueError("Aquisição vencida ou futura")
        if self._ultimo_tempo is not None and tempo_ns <= self._ultimo_tempo:
            raise ValueError("Aquisição fora de ordem")
        gx, gy, gz = giroscopio
        corrigido = gz - self.bias_giroscopio_z
        if not math.isfinite(corrigido):
            raise ValueError("Correção do giroscópio não finita")
        self._ultimo_tempo = tempo_ns
        return LeituraImu(tempo_ns, frame_id,
                          (gx, gy, corrigido),
                          tuple(acelerometro), self.covariancia_giroscopio,
                          self.covariancia_acelerometro)
