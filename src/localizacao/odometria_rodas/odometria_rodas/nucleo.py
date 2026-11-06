"""Odometria planar por contadores idealizados; não comprova sentido físico."""

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class EstadoOdometria:
    tempo_ns: int
    x: float = 0.0
    y: float = 0.0
    angulo: float = 0.0
    velocidade: float = 0.0
    rotacao: float = 0.0
    posicoes: tuple[float, float] = (0.0, 0.0)
    velocidades: tuple[float, float] = (0.0, 0.0)


def _positivo(nome, valor):
    if type(valor) not in (int, float):
        raise ValueError(f"{nome} deve ser numérico e positivo")
    try:
        convertido = float(valor)
    except OverflowError as erro:
        raise ValueError(f"{nome} excede o intervalo numérico") from erro
    if not math.isfinite(convertido) or convertido <= 0.0:
        raise ValueError(f"{nome} deve ser finito e positivo")
    return convertido


def _covariancia(diagonal):
    return tuple(diagonal[i // 7] if i % 7 == 0 else 0.0 for i in range(36))


class OdometriaRodas:
    def __init__(self, raio_roda, distancia_rodas,
                 variancia_velocidade=0.0025, variancia_rotacao=0.04):
        self.raio_roda = _positivo("raio_roda", raio_roda)
        self.distancia_rodas = _positivo("distancia_rodas", distancia_rodas)
        linear = _positivo("variancia_velocidade", variancia_velocidade)
        angular = _positivo("variancia_rotacao", variancia_rotacao)
        # Pose não calibrada e eixos não observados: incerteza conservadora,
        # não uma estimativa de covariância propagada nem pose verdadeira.
        self.covariancia_pose = _covariancia((1e6,) * 6)
        # vy=0 é restrição cinemática do diferencial idealizado, não sensor lateral.
        self.covariancia_velocidade = _covariancia((linear, linear, 1e6, 1e6, 1e6, angular))
        self._anterior = None
        self._sessao = None
        self._pulsos = None
        self._estado = EstadoOdometria(0)

    def processar(self, tempo_ns, sessao, contagem_esquerda, contagem_direita,
                  pulsos_por_volta):
        for nome, valor, minimo, maximo in (
            ("tempo_ns", tempo_ns, 1, (2**31) * 10**9 - 1),
            ("sessao", sessao, 0, 2**64 - 1),
            ("contagem_esquerda", contagem_esquerda, -(2**63), 2**63 - 1),
            ("contagem_direita", contagem_direita, -(2**63), 2**63 - 1),
            ("pulsos_por_volta", pulsos_por_volta, 1, 2**32 - 1),
        ):
            if type(valor) is not int or not minimo <= valor <= maximo:
                raise ValueError(f"{nome} fora do intervalo permitido")
        anterior = self._anterior
        atual = (tempo_ns, contagem_esquerda, contagem_direita)
        if anterior is None or sessao != self._sessao:
            self._anterior = atual
            self._sessao = sessao
            self._pulsos = pulsos_por_volta
            self._estado = EstadoOdometria(tempo_ns)
            return self._estado
        if tempo_ns <= anterior[0] or pulsos_por_volta != self._pulsos:
            # Descarta o intervalo ambíguo; preserva pose e ângulos acumulados.
            self._anterior = atual
            self._pulsos = pulsos_por_volta
            return None
        dt = (tempo_ns - anterior[0]) / 1e9
        escala = 2.0 * math.pi / pulsos_por_volta
        de = (contagem_esquerda - anterior[1]) * escala
        dd = (contagem_direita - anterior[2]) * escala
        distancia = (de + dd) * self.raio_roda / 2.0
        antigo = self._estado
        giro = (dd - de) * self.raio_roda / self.distancia_rodas
        metade = giro / 2.0
        sinc = math.sin(metade) / metade if metade != 0.0 else 1.0
        arco = distancia * sinc
        direcao = antigo.angulo + metade
        estado = EstadoOdometria(
            tempo_ns, antigo.x + arco * math.cos(direcao),
            antigo.y + arco * math.sin(direcao),
            math.atan2(math.sin(antigo.angulo + giro), math.cos(antigo.angulo + giro)),
            distancia / dt, giro / dt,
            (antigo.posicoes[0] + de, antigo.posicoes[1] + dd),
            (de / dt, dd / dt))
        valores = (estado.x, estado.y, estado.angulo, estado.velocidade, estado.rotacao,
                   *estado.posicoes, *estado.velocidades)
        if not all(math.isfinite(v) for v in valores):
            raise ValueError("Incremento excede o intervalo numérico finito")
        self._anterior = atual
        self._estado = estado
        return estado
