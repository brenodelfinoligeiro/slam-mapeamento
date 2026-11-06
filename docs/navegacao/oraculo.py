"""Oráculo independente de contato no ensaio cinemático; não altera a planta."""
import math


def _ponto_segmento(p,a,b):
    dx,dy=b[0]-a[0],b[1]-a[1];den=dx*dx+dy*dy
    t=max(0.,min(1.,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/den)) if den else 0.
    return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)


def distancia_segmentos(a,b,c,d):
    def cruz(p,q,r):return (q[0]-p[0])*(r[1]-p[1])-(q[1]-p[1])*(r[0]-p[0])
    o=[cruz(a,b,c),cruz(a,b,d),cruz(c,d,a),cruz(c,d,b)]
    if o[0]*o[1]<0 and o[2]*o[3]<0:return 0.
    return min(_ponto_segmento(a,c,d),_ponto_segmento(b,c,d),_ponto_segmento(c,a,b),_ponto_segmento(d,a,b))


def analisar_percurso(pontos,segmentos,raio):
    if not pontos or not segmentos or not math.isfinite(raio) or raio<=0:raise ValueError('Geometria ausente/inválida')
    if any(len(p)!=2 or not all(math.isfinite(v) for v in p) for p in pontos):raise ValueError('Ponto inválido')
    if any(len(s)!=4 or not all(math.isfinite(v) for v in s) for s in segmentos):raise ValueError('Segmento inválido')
    trechos=list(zip(pontos,pontos[1:])) or [(pontos[0],pontos[0])]
    distancia=min(distancia_segmentos(a,b,(s[0],s[1]),(s[2],s[3])) for a,b in trechos for s in segmentos)
    # 5 mm adicionais limitam a aproximação de arco por cordas no ensaio amostrado.
    folga=distancia-raio-.005
    return {'amostras':len(pontos),'comprimento_m':sum(math.dist(a,b) for a,b in trechos),
            'folga_minima_m':folga,'sem_interseccao_com_envoltoria':folga>=0,'raio_verificado_m':raio,'margem_amostragem_m':.005}
