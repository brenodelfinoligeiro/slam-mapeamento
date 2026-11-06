"""Comparação geométrica independente do raycaster e do SLAM, só para ensaio."""
import math
from statistics import median

def transformar(x,y,origem):
    ox,oy,angulo=origem;c=math.cos(angulo);s=math.sin(angulo)
    return ox+c*x-s*y,oy+s*x+c*y

def distancia_segmento(ponto,segmento):
    x,y=ponto;x1,y1,x2,y2=segmento;dx=x2-x1;dy=y2-y1
    comprimento2=dx*dx+dy*dy
    if comprimento2<=0:raise ValueError('Segmento sem comprimento')
    t=max(0.,min(1.,((x-x1)*dx+(y-y1)*dy)/comprimento2))
    return math.hypot(x-(x1+t*dx),y-(y1+t*dy))

def analisar(grade,segmentos,tolerancia=.15):
    largura=grade['largura'];altura=grade['altura'];res=grade['resolucao'];origem=grade['origem'];dados=grade['dados']
    if (type(largura) is not int or type(altura) is not int or largura<=0 or altura<=0 or largura*altura>2000000 or
        not math.isfinite(res) or res<=0 or len(dados)!=largura*altura or len(origem)!=3 or
        not all(math.isfinite(v) for v in origem) or not math.isfinite(tolerancia) or tolerancia<=0):
        raise ValueError('Grade ou tolerância inválida')
    if any(type(v) is not int or not -1<=v<=100 for v in dados):raise ValueError('Ocupação inválida')
    if not segmentos or any(len(s)!=4 or not all(math.isfinite(v) for v in s) or (s[0]==s[2] and s[1]==s[3]) for s in segmentos):
        raise ValueError('Segmentos inválidos')
    ocupados=[transformar((i%largura+.5)*res,(i//largura+.5)*res,origem) for i,v in enumerate(dados) if v>=65]
    if not ocupados:raise ValueError('Mapa sem obstáculos observados')
    distancias=[min(distancia_segmento(p,s) for s in segmentos) for p in ocupados]
    amostras=[]
    for x1,y1,x2,y2 in segmentos:
        n=max(1,math.ceil(math.hypot(x2-x1,y2-y1)/max(res,.05)))
        if n>20000:raise ValueError('Cenário excede orçamento de amostragem')
        amostras.extend((x1+(x2-x1)*i/n,y1+(y2-y1)*i/n) for i in range(n+1))
    cobrimentos=[min(math.hypot(x-px,y-py) for px,py in ocupados) for x,y in amostras]
    return {'largura':largura,'altura':altura,'resolucao_m':res,'celulas_ocupadas':len(ocupados),
        'celulas_livres':sum(0<=v<=25 for v in dados),'celulas_desconhecidas':sum(v==-1 for v in dados),
        'distancia_mediana_ocupados_parede_m':median(distancias),
        'fracao_ocupados_proximos_parede':sum(v<=tolerancia for v in distancias)/len(distancias),
        'fracao_parede_proxima_ocupado':sum(v<=tolerancia for v in cobrimentos)/len(cobrimentos),
        'tolerancia_m':tolerancia,'limite':'Paredes ocultas podem permanecer desconhecidas; não é validação física.'}
