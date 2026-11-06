#!/usr/bin/env python3
"""Renderiza SVGs próprios a partir dos dados reais do ensaio digital; sem CAD."""
import json
from html import escape
from pathlib import Path

BASE = Path(__file__).resolve().parent
DADOS = json.loads((BASE / 'dados-ensaio.json').read_text())
FUNDO = '#0b1220'
TEXTO = '#e8eef7'
SUAVE = '#a8bad0'
AZUL = '#42dbf4'
AMARELO = '#ffc76b'
VERDE = '#72e3aa'


def svg(largura, altura):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{largura}" height="{altura}" viewBox="0 0 {largura} {altura}">',
            '<style>text { font-family: DejaVu Sans, sans-serif; }</style>',
            f'<rect width="100%" height="100%" fill="{FUNDO}"/>']


def texto(partes, x, y, valor, tamanho=20, cor=TEXTO, ancora='start'):
    partes.append(f'<text x="{x}" y="{y}" font-size="{tamanho}" fill="{cor}" text-anchor="{ancora}">{escape(str(valor))}</text>')


def linha(partes, x1, y1, x2, y2, cor, espessura=2, extra=''):
    partes.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{cor}" stroke-width="{espessura}" {extra}/>')


def decimal(valor, casas=2):
    return f'{valor:.{casas}f}'.replace('.', ',')


def salvar(nome, partes):
    (BASE / nome).write_text('\n'.join(partes + ['</svg>']) + '\n')


def trajeto():
    partes = svg(1200, 1100)
    partes.append('<title>Robô móvel: trajeto medido no ensaio virtual Nav2</title>')
    texto(partes, 70, 62, 'Nav2 | trajetória observada', 34)
    texto(partes, 70, 102, 'ROS 2 Jazzy · NavFn + Regulated Pure Pursuit · 3 objetivos SUCCEEDED', 22, SUAVE)
    texto(partes, 70, 138, 'Ground truth para avaliação — não é pose fornecida ao Nav2.', 20, SUAVE)
    # Uma unidade de x tem exatamente a mesma escala de uma unidade de y.
    def xy(x, y):
        return 150 + (x + 2.5) * 145, 915 - (y + 2.0) * 145
    for x in range(-2, 4):
        px, _ = xy(x, 0)
        linha(partes, px, 190, px, 915, '#243044', 1)
        texto(partes, px, 950, x, 18, SUAVE, 'middle')
    for y in range(-2, 4):
        _, py = xy(0, y)
        linha(partes, 150, py, 1020, py, '#243044', 1)
        texto(partes, 125, py + 6, y, 18, SUAVE, 'end')
    for x1, y1, x2, y2 in DADOS['paredes_cenario']:
        a, b = xy(x1, y1), xy(x2, y2)
        linha(partes, *a, *b, '#dbe5ef', 6, 'stroke-linecap="round"')
    pontos = ' '.join(f'{xy(x, y)[0]:.2f},{xy(x, y)[1]:.2f}' for x, y in DADOS['trajeto_xy_m'])
    partes.append(f'<polyline points="{pontos}" fill="none" stroke="{AZUL}" stroke-width="3" opacity="0.9"/>')
    for indice, objetivo in enumerate(DADOS['objetivos'], 1):
        x, y = xy(*objetivo['alvo'][:2])
        partes.append(f'<circle cx="{x}" cy="{y}" r="15" fill="{FUNDO}" stroke="{AMARELO}" stroke-width="3"/>')
        texto(partes, x, y + 6, indice, 17, AMARELO, 'middle')
        # Centro verdadeiro ao concluir a ação: sem ícone ou geometria CAD.
        rx, ry = xy(*objetivo['pose_oraculo'][:2])
        partes.append(f'<circle cx="{rx}" cy="{ry}" r="4" fill="{VERDE}"/>')
    texto(partes, 1050, 946, 'x [m]', 20, SUAVE)
    texto(partes, 72, 173, 'y [m]', 20, SUAVE)
    linha(partes, 80, 993, 120, 993, AZUL, 4)
    texto(partes, 134, 1000, 'Trajeto integral: inclui teleop e testes de falha', 19)
    texto(partes, 80, 1035, 'Paredes do cenário de raios, não o /map aprendido. Números: metas; pontos verdes: chegada real.', 18, SUAVE)
    texto(partes, 80, 1070, 'Fonte: runtime-v09-final · 7.604 amostras · sensores/planta sintéticos · sem validação física.', 18, SUAVE)
    salvar('trajeto-nav2.svg', partes)


def metricas():
    partes = svg(1400, 1000)
    partes.append('<title>Resultados medidos dos objetivos e das perdas de dados no ensaio digital</title>')
    texto(partes, 70, 62, 'Resultados medidos | ensaio digital', 34)
    texto(partes, 70, 102, '3/3 objetivos SUCCEEDED · contato não detectado pelo oráculo geométrico', 23, VERDE)
    texto(partes, 70, 153, 'Erro real de posição [cm] · Nav2 aceita 10 cm na pose estimada', 23)
    for indice, objetivo in enumerate(DADOS['objetivos']):
        y = 204 + indice * 77
        erro = objetivo['erro_real_m'] * 100
        texto(partes, 70, y + 7, f'Meta {indice + 1}', 22)
        partes.append(f'<rect x="210" y="{y-18}" width="750" height="28" rx="6" fill="#243044"/>')
        partes.append(f'<rect x="210" y="{y-18}" width="{erro/12*750:.2f}" height="28" rx="6" fill="{AZUL}"/>')
        texto(partes, 985, y + 6, decimal(erro) + ' cm', 23, AZUL)
        texto(partes, 1160, y + 6, decimal(objetivo['duracao_parede_s'], 1) + ' s', 22, SUAVE)
    texto(partes, 210, 408, 'Barras: escala de 0 a 12 cm. À direita: duração de parede da ação.', 19, SUAVE)
    linha(partes, 70, 442, 1330, 442, '#324359')
    texto(partes, 70, 492, 'Perda de dados | latência monotônica até comando zerado [ms]', 23)
    nomes = {'scan': 'Scan', 'tf_global': 'TF global', 'odometria': 'Odometria', 'clock': 'Clock*'}
    for indice, falha in enumerate(DADOS['perdas_de_dados']):
        y = 545 + indice * 70
        ms = falha['latencia_parada_s'] * 1000
        texto(partes, 70, y + 7, nomes[falha['dado']], 22)
        partes.append(f'<rect x="250" y="{y-18}" width="650" height="28" rx="6" fill="#243044"/>')
        partes.append(f'<rect x="250" y="{y-18}" width="{ms/700*650:.2f}" height="28" rx="6" fill="{AMARELO}"/>')
        texto(partes, 925, y + 6, decimal(ms, 0) + ' ms', 23, AMARELO)
        texto(partes, 1090, y + 6, decimal(falha['deslocamento_ate_parar_m'] * 100, 1) + ' cm Δpose', 20, SUAVE)
    texto(partes, 250, 821, '0 a 700 ms · uma observação por falha · Δpose: deslocamento virtual no teste.', 19, SUAVE)
    texto(partes, 70, 872, '* Clock pausado congela também a planta: 0 cm não comprova frenagem física.', 20, SUAVE)
    total = DADOS['casos_workspace'] + DADOS['casos_oraculo']
    texto(partes, 70, 922, f'{total} casos: {DADOS["casos_workspace"]} dos pacotes + {DADOS["casos_oraculo"]} do oráculo/helpers; sem falhas/ignorados.', 22, VERDE)
    texto(partes, 70, 970, 'Fonte: validacao-navegacao.json / runtime-v09-final · AMD64/Jazzy · sem hardware ou segurança certificada.', 18, SUAVE)
    salvar('metricas-nav2.svg', partes)


if __name__ == '__main__':
    assert len(DADOS['trajeto_xy_m']) == DADOS['oraculo_contato']['amostras']
    assert all(objetivo['status'] == 4 and objetivo['error_code'] == 0 for objetivo in DADOS['objetivos'])
    trajeto()
    metricas()
    print('SVGs gerados com dados do ensaio digital, sem malhas CAD.')
