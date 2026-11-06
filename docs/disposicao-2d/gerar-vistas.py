"""Gera um estudo ortogonal 2D de envelopes; não é desenho de fabricação.
Executar com Python do sistema e /usr/lib/freecad/lib no sys.path.
O contorno é extraído da superfície superior do STL local, sem executar macros.
"""
from pathlib import Path
from collections import Counter
import sys, json, struct, hashlib, html, math
sys.path.insert(0, '/usr/lib/freecad/lib')
import FreeCAD as App
import Part

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / 'docs/modelos-3d/arquivos/chassi-2wd-B/chassi_e_suportes_derivado_mm.stl'
S = 2.5
COL = {'estrutura':'#8b98a6','impresso':'#c14d88','pilhas':'#d79a22','motor':'#c49b3e',
       'esp':'#347fb3','imu':'#168c91','driver':'#c44f49','pi':'#27875a',
       'powerbank':'#566c87','lidar':'#7852b6','rodas':'#263849','encoder':'#64768d'}
parts = [
 {'id':'01','nome':'Porta-pilhas 4 AA','tipo':'pilhas','box':[-37.5,10,50.4,75,70,22],'evidencia':'Reserva proposta; holder não escolhido.'},
 {'id':'02','nome':'ESP — reserva','tipo':'esp','box':[-45,101,50.4,28,55,15],'evidencia':'Envelope proposto; placa ESP final pendente.'},
 {'id':'03','nome':'MPU-6050','tipo':'imu','box':[5,153,50.4,16,21,11.54],'evidencia':'Envelope CAD candidato; orientação/furação não medidas.'},
 {'id':'04','nome':'L298N','tipo':'driver','box':[3,94,50.4,43,43,28],'evidencia':'Envelope do CAD de referência; módulo físico a conferir.'},
 {'id':'05','nome':'Encoders e discos','tipo':'encoder','box':[-35,70,25,14.3,35.45,13.8],'evidencia':'Representação funcional simplificada; alinhar garfo/disco nos eixos reais.'},
 {'id':'06','nome':'Raspberry Pi 5','tipo':'pi','box':[-44.25,12,91,88.5,57.63035,18.976],'evidencia':'Envelope CAD oficial; cabos e cooler real não incluídos.'},
 {'id':'07','nome':'Powerbank — reserva','tipo':'powerbank','box':[-60,140,91,120,65,25],'evidencia':'Volume hipotético; modelo e medidas desconhecidos.'},
 {'id':'08','nome':'LiDAR C1 — corpo','tipo':'lidar','box':[-27.8,76.2,140,55.6,55.6,41.3],'evidencia':'Corpo simplificado; dimensões comerciais citadas no catálogo, não envelope global do STEP.'},
]

def contour():
    data=SOURCE.read_bytes(); edges=Counter()
    for i in range(struct.unpack_from('<I',data,80)[0]):
        row=struct.unpack_from('<12fH',data,84+50*i)
        if all(abs(row[j+2]-48.418)<0.003 for j in (3,6,9)):
            vs=[tuple(round(v,4) for v in row[j:j+2]) for j in (3,6,9)]
            for a,b in zip(vs,vs[1:]+vs[:1]):
                if a!=b: edges[tuple(sorted((a,b)))]+=1
    remaining={e for e,c in edges.items() if c==1}; loops=[]
    while remaining:
        a,b=remaining.pop(); ring=[a,b]
        while ring[-1]!=ring[0]:
            matches=[e for e in remaining if ring[-1] in e]
            if not matches: raise ValueError('Contorno aberto no STL de referência')
            e=matches[0]; remaining.remove(e); ring.append(e[1] if e[0]==ring[-1] else e[0])
        loops.append(ring)
    area=lambda v:abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(v,v[1:]))/2)
    loops.sort(key=area,reverse=True)
    xs=[v[0] for v in loops[0]]; ys=[v[1] for v in loops[0]]
    cx=(min(xs)+max(xs))/2; ymin=min(ys)
    return [[(x-cx,y-ymin) for x,y in ring] for ring in loops]

loops=contour()
doc=App.newDocument('Disposicao2D')
doc.addObject('App::FeaturePython','Notas').addProperty('App::PropertyString','Limite').Limite='Estudo de envelopes, sem validação física ou dimensões para fabricação. Ver SVG e LEIA-ME.'
svg=[]; native_count=0; active='Prancha'; bounds=[]

def text(x,y,value,size=22,color='#25374b',weight='400',anchor='start'):
    svg.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}" text-anchor="{anchor}">{html.escape(value)}</text>')

def geom(rings,color,fill='none',dash=False,width: float=2,opacity: float=1,label=''):
    global native_count
    wires=[]; paths=[]
    for ring in rings:
        if len(ring)<2: continue
        vectors=[App.Vector(x/S,-y/S,0) for x,y in ring]
        wires.append(Part.makePolygon(vectors))
        paths.append('M '+' L '.join(f'{x:.3f},{y:.3f}' for x,y in ring))
    obj=doc.addObject('PartDesign::Feature',f'G{native_count:04d}'); native_count+=1
    obj.Label=active+' / '+label
    obj.Shape=Part.makeCompound(wires)
    obj.addProperty('App::PropertyString','CorSVG').CorSVG=color
    obj.addProperty('App::PropertyString','Camada').Camada=active
    dashattr=' stroke-dasharray="9 6"' if dash else ''
    svg.append(f'<path d="{" ".join(paths)}" fill="{fill}" fill-rule="evenodd" stroke="{color}" stroke-width="{width}" opacity="{opacity}"{dashattr}/>')
    bb=obj.Shape.BoundBox
    bounds.append((obj.Name,bb.XMin,bb.XMax,bb.YMin,bb.YMax))

def rect(x,y,w,h,color,fill='none',dash=False,width=2,opacity=1,label=''):
    geom([[(x,y),(x+w,y),(x+w,y+h),(x,y+h),(x,y)]],color,fill,dash,width,opacity,label)

def circle(cx,cy,r,color,fill='none',dash=False,width=2,opacity=1,label=''):
    # Polígono discretizado de visualização; não substitui cilindro medido.
    ring=[(cx+r*math.cos(t*math.pi/48),cy+r*math.sin(t*math.pi/48)) for t in range(97)]
    geom([ring],color,fill,dash,width,opacity,label)

def line(points,color='#8b98a6',dash=False,width=2,label=''):
    geom([points],color,'none',dash,width,1,label)

def badge(x,y,n,color):
    circle(x,y,16,color,'white',width=2,label='Identificador '+n)
    text(x,y+6,n,17,color,'700','middle')

def panel(x,y,w,h,title,subtitle):
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="#fff" stroke="#d8e0e8" stroke-width="2"/>')
    text(x+22,y+36,title,27,weight='700'); text(x+22,y+65,subtitle,18,'#617084')

def plan_base(cx,top,ghost=False):
    mapped=[[(cx+x*S,top+y*S) for x,y in ring] for ring in loops]
    geom(mapped,COL['estrutura'],'#f3f5f7',ghost,1.2,0.3 if ghost else 1,'Contorno CAD da chapa e aberturas')
    for x in (-66.7,66.7):
        rect(cx+(x-12)*S,top+(87.3-34.5)*S,24*S,69*S,COL['rodas'],'#e5e9ed',label='Roda de referência')
    circle(cx,top+210*S,12*S,COL['estrutura'],'#e5e9ed',dash=True,label='Rodízio, posição proposta')
    line([(cx,top-12),(cx,top+224*S)],'#b1bdc9',True,1)

def footprint(p,cx,top,dashed=False):
    x,y,z,w,l,h=p['box']; c=COL[p['tipo']]
    rect(cx+x*S,top+y*S,w*S,l*S,c,c+'18',dashed,label=p['id']+' '+p['nome'])
    badge(cx+(x+w/2)*S,top+(y+l/2)*S,p['id'],c)

def dim_h(x1,x2,y,value):
    line([(x1,y),(x2,y)],'#53657b',width=1)
    for x in (x1,x2): line([(x-5,y-6),(x+5,y+6)],'#53657b',width=1)
    text((x1+x2)/2,y-10,value,18,'#53657b',anchor='middle')

svg.append('<svg xmlns="http://www.w3.org/2000/svg" width="2200" height="1720" viewBox="0 0 2200 1720"><title>Slamderson — disposição 2D com quatro pilhas AA</title><desc>Estudo preliminar em quatro vistas. Contorno derivado do CAD local do chassi B; dimensões restantes são envelopes de referência ou reservas propostas. Sem validação física.</desc><g font-family="DejaVu Sans, sans-serif">')
svg.append('<rect width="2200" height="1720" fill="#edf2f7"/>')
text(40,60,'SLAMDERSON / DISPOSIÇÃO DOS COMPONENTES',37,weight='700')
text(40,100,'4 PILHAS AA + POWERBANK SEPARADO  •  ESTUDO DE ENVELOPES, NÃO DESENHO PARA FABRICAÇÃO',23,'#617084')
panel(40,140,620,760,'01 / PLANTA DO PISO INFERIOR','Piso superior retirado; componentes sob a chapa em tracejado.')
panel(700,140,620,760,'02 / PLANTA DO PISO SUPERIOR','LiDAR e ponte acima deste piso, indicados em tracejado.')
panel(1360,140,800,760,'COMPONENTES E SUPORTES','Cores e identificadores iguais em todas as vistas.')
panel(40,940,1270,600,'03 / VISTA LATERAL','Vista esquemática por transparência; frente à esquerda.')
panel(1360,940,800,600,'04 / VISTA FRONTAL','Olhando da extremidade arredondada para o rodízio.')

active='Piso inferior'; cx=350; top=270
plan_base(cx,top)
text(cx,top-45,'FRENTE PROPOSTA ↑',18,'#53657b',anchor='middle')
for x in (-46.7,24.3):
    rect(cx+x*S,top+47*S,22.4*S,70.6*S,COL['motor'],COL['motor']+'18',True,label='Motor TT, envelope proposto')
for side in (-1,1):
    x=-35 if side<0 else 20.7
    rect(cx+x*S,top+70*S,14.3*S,35.45*S,COL['encoder'],'none',True,label='05 Encoder, suporte a alinhar')
    line([(cx+side*35*S,top+77*S),(cx+side*35*S,top+97*S)],COL['encoder'],True,4,'Disco, posição ilustrativa')
for p in parts[:4]: footprint(p,cx,top,p['id'] in ('01','02'))
# Quatro símbolos de pilhas, sem atribuir dimensões de fabricação ao holder.
for j in range(4):
    rect(cx-29*S,top+(15+j*15)*S,58*S,12*S,COL['pilhas'],'none',width=1,label='AA ilustrativa')
badge(cx,top+45*S,'01',COL['pilhas'])
text(cx,top+80*S+20,'RESERVA DO HOLDER',16,COL['pilhas'],anchor='middle')
badge(110,top+87.3*S,'05',COL['encoder'])
line([(126,top+87.3*S),(cx-35*S,top+87.3*S)],COL['encoder'],True,1)
for x in (-43,43):
    for y in (20,199): rect(cx+(x-3)*S,top+(y-3)*S,6*S,6*S,COL['impresso'],COL['impresso']+'40',label='09 Coluna proposta')
badge(205,top+20*S,'09',COL['impresso'])
line([(221,top+20*S),(cx-43*S,top+20*S)],COL['impresso'],width=1)
text(cx,860,'Chapa ≈149 × 210 mm no CAD; conferir na peça.',18,'#617084',anchor='middle')
dim_h(cx-74.489*S,cx+74.489*S,top-4, '≈149 mm • referência CAD')
text(70,886,'05 Garfos/discos próximos aos eixos, sob a chapa.',19,'#64768d')

active='Piso superior'; cx=1010; top=270
plan_base(cx,top,True)
# Piso com abertura de ventilação sobre a L298N.
outer=[(cx-65*S,top+8*S),(cx+65*S,top+8*S),(cx+65*S,top+205*S),(cx-65*S,top+205*S),(cx-65*S,top+8*S)]
window=[(cx,top+90*S),(cx+50*S,top+90*S),(cx+50*S,top+146*S),(cx,top+146*S),(cx,top+90*S)]
geom([outer,window],COL['impresso'],COL['impresso']+'08',label='10 Piso removível com janela de ventilação')
for p in parts[5:7]: footprint(p,cx,top,p['id']=='07')
for x in (-58,58): rect(cx+(x-3)*S,top+77*S,6*S,6*S,COL['impresso'],COL['impresso']+'30',label='11 Coluna da ponte LiDAR')
rect(cx-65*S,top+71*S,130*S,66*S,COL['impresso'],'none',True,label='12 Ponte LiDAR acima do piso')
circle(cx,top+104*S,27.8*S,COL['lidar'],COL['lidar']+'18',True,label='08 Corpo C1 acima do piso')
badge(cx,top+104*S,'08',COL['lidar'])
text(cx+27*S,top+140*S,'JANELA',15,COL['driver'],anchor='middle')
text(cx,top+182*S,'RESERVA',17,COL['powerbank'],anchor='middle')
for n,x,y,target in [('10',1250,320,(cx+65*S,top+20*S)),('11',815,470,(cx-58*S,top+80*S)),('12',1250,575,(cx+65*S,575))]:
    badge(x,y,n,COL['impresso']); line([(x-16 if x>cx else x+16,y),target],COL['impresso'],width=1)
text(cx,top-45,'FRENTE PROPOSTA ↑',18,'#53657b',anchor='middle')
text(cx,860,'Piso proposto: 130 × 197 mm; apoios a conferir.',18,'#617084',anchor='middle')
text(730,886,'Janela sobre a L298N • piso removível para trocar as AA.',18,'#617084')

# Legenda com áreas reservadas e evidência explícita.
legend=[('01','pilhas','4 AA / reserva 75 × 70 × 22 mm','Holder a escolher; posição baixa e acesso por cima.'),
('02','esp','ESP / reserva 28 × 55 × 15 mm','A placa final ainda não foi escolhida.'),
('03','imu','MPU-6050 / 16 × 21 × 11,5 mm','Fixação rígida ao piso inferior; calibrar orientação.'),
('04','driver','L298N / 43 × 43 × 28 mm','Dissipador livre, janela no piso superior.'),
('05','encoder','Dois encoders + discos + motores TT','Montagem funcional simplificada; alinhamento pendente.'),
('06','pi','Pi 5 / 88,5 × 57,6 × 19 mm','Reservar ventilação, cooler e saída dos cabos.'),
('07','powerbank','Powerbank / reserva 120 × 65 × 25 mm','Modelo desconhecido; prender com cinta removível.'),
('08','lidar','LiDAR C1 / corpo Ø55,6 × 41,3 mm','Acima dos demais volumes; cabos abaixo da óptica.'),
('09–12','impresso','Suportes propostos para impressão 3D','Colunas, piso removível e ponte do C1; sem furação final.')]
for i,(n,c,title,sub) in enumerate(legend):
    y=250+i*68
    svg.append(f'<rect x="1384" y="{y-23}" width="8" height="43" fill="{COL[c]}"/>')
    text(1410,y,n+'  '+title,22,COL[c],'700'); text(1410,y+25,sub,19,'#617084')
text(1384,853,'09 colunas • 10 piso • 11 apoios • 12 ponte do LiDAR',19,COL['impresso'])
text(1384,882,'Tracejado: oculto/elevado OU reserva; conferir identificação.',18,'#617084')

# Elevações usam as MESMAS caixas 3D propostas, projetadas ortogonalmente.
def elevation(front=False):
    global active
    active='Frontal' if front else 'Lateral'
    origin=1770 if front else 220; ground=1490
    project=lambda u,z:(origin+u*S,ground-z*S)
    def box(u,z,w,h,c,fill='none',dash=False,label=''):
        if front: u=-u-w  # Observador na frente: espelha a planta com frente para cima.
        a,b=project(u,z+h); rect(a,b,w*S,h*S,c,fill,dash,label=label)
    line([project(-100 if front else -18,0),project(100 if front else 242,0)],'#8b98a6',width=2,label='Solo proposto / z =0')
    if front:
        for x in (-66.7,66.7): box(x-12,0,24,69,COL['rodas'],COL['rodas']+'15',label='Rodas')
        circle(*project(0,12),12*S,COL['estrutura'],'none',True,label='Rodízio ao fundo')
        box(-74.489,45.4,148.978,3,COL['estrutura'],'#e0e5eb',label='Chapa')
    else:
        circle(*project(87.3,34.5),34.5*S,COL['rodas'],COL['rodas']+'12',label='Roda')
        circle(*project(210,12),12*S,COL['estrutura'],'#e0e5eb',label='Rodízio')
        box(185,12,26,33.4,COL['estrutura'],'none',True,label='Suporte do rodízio a ajustar')
        box(0,45.4,209.9732,3,COL['estrutura'],'#e0e5eb',label='Chapa')
    for p in parts:
        if p['id']=='08': continue
        x,y,z,w,l,h=p['box']; u,size=(x,w) if front else (y,l)
        box(u,z,size,h,COL[p['tipo']],COL[p['tipo']]+'10',p['id'] in ('01','02','05','07'),p['id']+' '+p['nome'])
    for u in ((-43,43) if front else (20,199)):
        box(u-3,48.4,6,35.6,COL['impresso'],COL['impresso']+'15',label='09 Colunas principais')
    box(-65 if front else 8,84,130 if front else 197,3,COL['impresso'],COL['impresso']+'20',label='10 Piso superior')
    for u in ((-58,58) if front else (80,)):
        box(u-3,87,6,48,COL['impresso'],COL['impresso']+'20',label='11 Colunas do C1')
    box(-65 if front else 71,135,130 if front else 66,3,COL['impresso'],COL['impresso']+'20',label='12 Ponte do C1')
    box(-27.8 if front else 76.2,140,55.6,41.3,COL['lidar'],COL['lidar']+'15',label='08 Corpo do C1')
    box(-15 if front else 89,138,30,2,COL['impresso'],'none',label='Espaçadores C1')
    box(-44.25 if front else 12,109.976,88.5 if front else 57.63035,18,COL['pi'],'none',True,label='Reserva de cooler, não é peça selecionada')
    if front:
        text(1770,1518,'Simetria dos apoios; furação e estabilidade não verificadas.',18,'#617084',anchor='middle')
        text(1770,1019,'08  C1 acima de todas as outras peças',19,COL['lidar'],anchor='middle')
    else:
        text(320,1154,'Reserva de cooler',18,COL['pi'],anchor='middle')
        for z,caption in [(48.4,'Chapa / z ≈48 mm'),(87,'Piso proposto / z =87 mm'),(140,'Base C1 proposta / z =140 mm'),(181.3,'Topo proposto / z ≈181 mm')]:
            xx,yy=project(235,z); line([project(216,z),(xx,yy)],'#8b98a6',True,1); text(xx+12,yy+6,caption,19,'#53657b')
        text(230,1518,'Frente proposta ←',18,'#53657b')
        text(1010,1518,'Rodízio →',18,'#53657b')
elevation(); elevation(True)
text(40,1590,'SÓ A QUANTIDADE DE AA FOI FECHADA: QUATRO. POSIÇÕES E SUPORTES SÃO UMA PROPOSTA.',24,'#25374b','700')
text(40,1625,'4 AA alcalinas ≈6 V nominais (NiMH ≈4,8 V). Motores informados como 12 V: desempenho com L298N ainda não validado.',22,'#a24531')
text(40,1660,'Chapa: contorno extraído do CAD B local. Demais volumes: referências ou reservas indicadas. Sem cabos, tolerâncias ou encaixes certificados.',20,'#617084')
text(40,1694,'Cotas em mm. Mesma proporção nas quatro vistas, sem escala de impressão. Não usar para furar, usinar ou imprimir suportes definitivos.',20,'#617084')
svg.append('</g></svg>')
doc.recompute()
native=OUT/'disposicao-componentes-2d.FCStd'; doc.saveAs(str(native)); count=len(doc.Objects)
App.closeDocument(doc.Name)
opened=App.openDocument(str(native))
assert len(opened.Objects)==count
for name,x1,x2,y1,y2 in bounds:
    shape=opened.getObject(name).Shape
    assert not shape.isNull() and shape.isValid(),name
    b=shape.BoundBox
    assert all(abs(a-c)<1e-5 for a,c in zip((x1,x2,y1,y2),(b.XMin,b.XMax,b.YMin,b.YMax))),name
(OUT/'disposicao-componentes-2d.svg').write_text('\n'.join(svg),encoding='utf-8')
# Todos os números de implantação são propostas, não uma medição do robô.
audit={'versao':1,'natureza':'estudo_ortogonal_de_envelopes_nao_fabricacao','componentes':parts,
       'quantidade_AA_confirmada':4,'tensoes_nominais_exemplos':{'alcalinas_V':4*1.5,'NiMH_V':4*1.2},
       'origem_contorno':{'arquivo':str(SOURCE.relative_to(ROOT)),'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'z_da_superficie_STL':48.418,'aneis':len(loops),'unidade':'mm interpretados conforme cena Blender de origem'},
       'cotas_propostas_mm':{'chapa_z_inferior':45.4,'chapa_z_superior':48.4,'piso_z_inferior':84,'piso_z_superior':87,'ponte_z_inferior':135,'ponte_z_superior':138,'base_C1_z':140,'topo_C1_z':181.3},
       'validacao_FreeCAD':{'versao':'.'.join(App.Version()[:3]),'reaberto':True,'geometrias_2D_validas':native_count,'objetos':count,'limite':'Validação geométrica de desenho 2D; não análise de colisão de sólidos ou de estabilidade.'},
       'pendencias':['Medir holder 4 AA, powerbank e placa ESP.','Confirmar motores, corrente e desempenho com 4 AA/L298N.','Conferir alinhamento discos/garfos, cabos, refrigeração e suporte do rodízio.','Dimensionar fixações, tolerâncias, espessuras e estabilidade física.']}
(OUT/'implantacao.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'saida':str(OUT),'geometrias_validas':native_count,'objetos_reabertos':count,'contorno_aneis':len(loops)},ensure_ascii=False))
