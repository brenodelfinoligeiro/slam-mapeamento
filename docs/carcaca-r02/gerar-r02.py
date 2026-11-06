"""R02: corrige o powerbank e acrescenta carcaça de estudo, sem alterar a R01.
As peças são propostas paramétricas para teste dimensional, não encaixes certificados.
"""
from pathlib import Path
import sys,json,hashlib,struct
sys.path.insert(0,'/usr/lib/freecad/lib')
import FreeCAD as App
import Part
import Mesh
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
SOURCE=ROOT/'docs/montagem-3d/slamderson-estudo-3d.FCStd'
source_hash=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
D=App.openDocument(str(SOURCE))
assert len(D.Objects)==86
new_records=[]

def box(x,y,z,w,l,h): return Part.makeBox(w,l,h,App.Vector(x,y,z))
def cyl(x,y,z,r,h,axis=(0,0,1)): return Part.makeCylinder(r,h,App.Vector(x,y,z),App.Vector(*axis))
def rb(x,y,z,w,l,h,r):
    s=box(x,y,z,w,l,h)
    edges=[e for e in s.Edges if abs(e.BoundBox.ZLength-h)<1e-5 and e.BoundBox.XLength<1e-5 and e.BoundBox.YLength<1e-5]
    assert len(edges)==4
    return s.makeFillet(r,edges)
def setshape(o,s):
    o.Placement=App.Placement(); o.Shape=s
    return o
def move_min(o,x,y,z):
    s=o.Shape.copy(); b=s.BoundBox; s.translate(App.Vector(x-b.XMin,y-b.YMin,z-b.ZMin)); return setshape(o,s)
def shift(o,dx,dy,dz):
    s=o.Shape.copy(); s.translate(App.Vector(dx,dy,dz)); return setshape(o,s)
def add(name,label,shape,color,group,evidence='proposta geométrica, sem validação física'):
    o=D.addObject('PartDesign::Feature',name); o.Label=label; o.Shape=shape
    o.addProperty('App::PropertyColor','CorDoEstudo').CorDoEstudo=color
    o.addProperty('App::PropertyInteger','TransparenciaEstudo').TransparenciaEstudo=0
    o.addProperty('App::PropertyString','Evidencia').Evidencia=evidence
    D.getObject(group).addObject(o)
    new_records.append({'objeto':o.Name,'rotulo':label,'evidencia':evidence})
    return o
for name,label in [('CarcacaBase','05 Carcaça — saia inferior'),('Tampas','06 Carcaça — tampas superiores'),('Acessos','07 Portinholas e uniões propostas')]:
    D.addObject('App::DocumentObjectGroup',name).Label=label
pink=(.74,.22,.45); charcoal=(.12,.17,.21); light=(.73,.78,.8)

# POWERBANK REAL: cotas fornecidas, raio dos cantos apenas ilustrativo.
pb=rb(-75,135,50.8,150,70,30,4)
o=setshape(D.getObject('Reserva_Powerbank'),pb)
o.Label='07 Basike REAL — envelope 150 x 70 x 30 mm'
o.CorDoEstudo=(.08,.10,.12)
o.Evidencia='Envelope informado pelo autor; raio de canto, portas e cabos não medidos.'
o.addProperty('App::PropertyFloat','MassaIndicada_g').MassaIndicada_g=420
D.getObject('Superior').removeObject(o); D.getObject('Inferior').addObject(o)
# Tray e retirada para trás; sem parafusos/modelo exato de clip aprovados.
tray=box(-78,132,48.4,156,73,2.4)
tray=tray.fuse(box(-78,132,50.8,2,73,5)).fuse(box(76,132,50.8,2,73,5)).fuse(box(-78,132,50.8,156,2,5))
for x in (-40,40):
    for y in (147,198): tray=tray.cut(cyl(x,y,48,1.7,4))
add('BercoPB','Berço Basike — saque traseiro',tray,pink,'Inferior')
for name in [o.Name for o in D.Objects if o.Name.startswith('Apoio_PB')]: D.removeObject(name)
for i,o in enumerate([o for o in D.Objects if o.Name.startswith('CintaPowerbank')]):
    y=(153,191)[i]
    u=box(-76,y,51,152,6,30.8).cut(box(-75,y-1,50,150,8,31))
    setshape(o,u); D.getObject('Superior').removeObject(o); D.getObject('Inferior').addObject(o)
# L298N abre espaço de 2 mm entre seu envelope e o powerbank.
move_min(D.getObject('L298N'),3,90,56.4)
for o in [o for o in D.Objects if o.Name.startswith('Apoio_L298N')]:
    shift(o,0,-4,0)
    b=o.Shape.BoundBox
    if b.YMin>120:
        setshape(o,cyl((b.XMin+b.XMax)/2,(b.YMin+b.YMax)/2,52.4,2.5,4))
# ESP leve sobe; IMU permanece rigidamente na base, junto à região central.
esp=move_min(D.getObject('Reserva_ESP'),-14,143,94)
D.getObject('Inferior').removeObject(esp); D.getObject('Superior').addObject(esp)
for name in [o.Name for o in D.Objects if o.Name.startswith('Apoio_ESP')]: D.removeObject(name)
for x in (-10,10):
    for y in (147,194): add('ApoioESP','Apoio ESP — posição de estudo',cyl(x,y,90,2.5,4),pink,'Superior')
move_min(D.getObject('MPU6050'),-14,110,50.4)
# Apoios do holder para não representar a caixa simplesmente suspensa.
for x in (-30,30):
    for y in (16,74): add('ApoioAA','Apoio do holder AA proposto',cyl(x,y,48.4,2.5,2),pink,'Inferior')
# Rear columns saem da região ocupada pelo powerbank.
for o in [o for o in D.Objects if o.Name.startswith('ColunaPrincipal')]:
    b=o.Shape.BoundBox; x=(b.XMin+b.XMax)/2; y=(b.YMin+b.YMax)/2
    if y<100: s=cyl(x,20,48.4,3.8,38.6).cut(cyl(x,20,47.4,1.6,40.6))
    else:
        x=58 if x>0 else -58
        s=cyl(x,130,52.4,3.8,34.6).cut(cyl(x,130,51.4,1.6,36.6))
    setshape(o,s)
for x in (-63,39): add('Travessa','Travessa traseira proposta',box(x,124,48.4,24,12,4),pink,'Inferior')
floor=box(-65,8,87,130,197,3).cut(box(0,90,86,50,56,5))
for x in (-61,61):
    for y in (24,194): floor=floor.cut(cyl(x,y,86,1.7,5))
for x in (-59.5,56.5): floor=floor.fuse(box(x,135,84,3,56,3))
# Recortes liberam as orelhas traseiras da carcaça/portinhola.
for x in (-66,62): floor=floor.cut(box(x,198,86,4,8,5))
for x in (-61,49): floor=floor.cut(box(x,203,86,12,4,5))
setshape(D.getObject('PisoSuperior'),floor)
for o in [o for o in D.Objects if o.Name.startswith('Apoio_Pi')]: shift(o,0,0,3)
shift(D.getObject('RaspberryPi5'),0,0,3)
for o in [o for o in D.Objects if o.Name.startswith('ApoioPonte')]:
    b=o.Shape.BoundBox; x=(b.XMin+b.XMax)/2
    setshape(o,cyl(x,80,90,3.8,50).cut(cyl(x,80,89,1.6,52)))
bridge=D.getObject('PonteLidar').Shape.copy(); bridge.translate(App.Vector(0,0,5))
bridge=bridge.cut(box(-66,98,139,41,12,5))
setshape(D.getObject('PonteLidar'),bridge)
for o in [o for o in D.Objects if o.Name.startswith('EspacadorC')]: shift(o,0,0,5)
shift(D.getObject('LidarC1'),0,0,5)

# CARCAÇA VENTILADA: 3 mm propostos; aberta embaixo, não é vedada/IP.
base=rb(-85,-2,49.4,170,212,40.6,12).cut(rb(-82,1,48,164,206,44,9))
wheel=D.getObject('Mecanica_00').Mesh.BoundBox
yw=(wheel.YMin+wheel.YMax)/2; zw=(wheel.ZMin+wheel.ZMax)/2
base=base.cut(cyl(-100,yw,zw,40,200,(1,0,0)))
# Acesso frontal AA, traseiro PB e janela lateral de serviço (não recorte exato das portas).
base=base.cut(box(-41,-3,49,82,5,26)).cut(box(-77,206,50.6,154,5,33.2))
base=base.cut(box(81,136,51,5,69,32))
for x in (-86,81):
    for y in (128,136,144,152,160,168): base=base.cut(box(x,y,59,5,3,17))
# Orelhas que apoiam o piso; seu furo é proposta, não furação real do chassi.
for x in (-83,56):
    for y in (18,192): base=base.fuse(box(x,y,84,27,12,3))
for x in (-61,61):
    for y in (24,194): base=base.cut(cyl(x,y,83,1.7,5))
# Uniões das tampas, todas fora dos volumes dos módulos.
for x in (-74,62):
    for y,length in ((0,8),(198,10)):
        base=base.fuse(box(x,y,82,12,length,8))
for x in (-68,68):
    for y in (4,202): base=base.cut(cyl(x,y,81,1.4,10))
for x in (-35,25): base=base.fuse(box(x,0,75,10,6,7))
for x in (-60,50): base=base.fuse(box(x,203,84,10,7,6))
for x in (-30,30): base=base.cut(cyl(x,-8,78.4,1.5,17,(0,1,0)))
for x in (-55,55): base=base.cut(cyl(x,202,87.5,1.5,13,(0,1,0)))
for y in (142,199):
    base=base.fuse(box(78,y-5,83.5,7,10,6.5))
    base=base.cut(cyl(77,y,86.5,1.5,12,(1,0,0)))
base=base.removeSplitter()
add('Saia','Carcaça 01 — saia ventilada',base,charcoal,'CarcacaBase')
# Capuz em duas metades que se retiram lateralmente por rasgos ao redor dos apoios do C1.
cap=rb(-85,-2,90.6,170,212,46.4,12).cut(rb(-82,1,89,164,206,45,9))
cap=cap.cut(box(-63,75,133,126,10,6)).cut(box(-45,98,133,45.4,12,6))
for x in range(-46,47,7): cap=cap.cut(box(x,17,133,3,45,6))
for x in (-86,81):
    for y in (20,28,36,44,52): cap=cap.cut(box(x,y,119,5,3,9))
# Carenagem cobre a placa; apenas uma pequena passagem de cabo na junta frontal.
cap=cap.cut(box(-6,-3,95,12,5,8))
cap=cap.cut(box(-6,206,97,12,5,8))
for x in (-74,62):
    for y,length in ((0,8),(198,10)): cap=cap.fuse(box(x,y,90.6,12,length,5.4))
for x in (-68,68):
    for y in (4,202): cap=cap.cut(cyl(x,y,89,1.7,9))
left=cap.common(box(-200,-100,0,199.7,500,500)).removeSplitter()
right=cap.common(box(.3,-100,0,200,500,500)).removeSplitter()
add('TampaEsquerda','Carcaça 02 — tampa esquerda, retirada lateral',left,light,'Tampas')
add('TampaDireita','Carcaça 03 — tampa direita, retirada lateral',right,light,'Tampas')
front=box(-47,-4.4,48.4,94,2.4,34)
for x in (-30,30): front=front.cut(cyl(x,-7,78.4,1.7,8,(0,1,0)))
rear=box(-80,210,48.4,160,2.4,41.4)
for x in (-55,55): rear=rear.cut(cyl(x,208,87.5,1.7,7,(0,1,0)))
add('PortinholaAA','Carcaça 04 — acesso AA pela frente',front,charcoal,'Acessos')
add('PortinholaPB','Carcaça 05 — acesso PB por trás',rear,charcoal,'Acessos')
side=box(85,132,49,2.4,75,40)
for y in (142,199): side=side.cut(cyl(84,y,86.5,1.7,6,(1,0,0)))
add('TampaServicoPB','Carcaça 06 — tampa lateral de serviço PB',side,charcoal,'Acessos')
for y in (142,199): add('UniaoServicoPB','União da tampa lateral PB',cyl(87.4,y,86.5,2.8,2,(1,0,0)),(.12,.46,.48),'Acessos')
# Cabeças ilustrativas: não são uma especificação de parafuso ou insert.
for x in (-68,68):
    for y in (4,202): add('UniaoTampas','União proposta — fixador a definir',cyl(x,y,96,2.8,2),(.12,.46,.48),'Acessos')
for x in (-30,30): add('UniaoAA','União portinhola AA',cyl(x,-6.4,78.4,2.8,2,(0,1,0)),(.12,.46,.48),'Acessos')
for x in (-55,55): add('UniaoPB','União portinhola PB',cyl(x,212.4,87.5,2.8,2,(0,1,0)),(.12,.46,.48),'Acessos')

D.getObject('Escopo').Aviso='R02: Basike real 150x70x30 mm, massa indicada 420 g. Carcaça ventilada de estudo; não é vedada, não aprova furação, fixadores, resistência, temperatura ou desempenho elétrico.'
D.recompute()
invalid=[o.Name for o in D.Objects if hasattr(o,'Shape') and (o.Shape.isNull() or not o.Shape.isValid())]
assert not invalid,invalid
file=OUT/'slamderson-coberto-r02.FCStd'; D.saveAs(str(file))
principal=['Saia','TampaEsquerda','TampaDireita','PortinholaAA','PortinholaPB','TampaServicoPB']
# Exportar apenas peças próprias da carcaça para avaliação dimensional.
C=App.newDocument('CarcacaR02'); own=[]; stls=[]
for name in principal:
    s=D.getObject(name).Shape.copy(); assert len(s.Solids)==1,(name,len(s.Solids))
    o=C.addObject('PartDesign::Feature',name); o.Label=D.getObject(name).Label; o.Shape=s; own.append(o)
    v,faces=s.tessellate(.2)
    path=OUT/(name+'_ESTUDO.stl')
    with path.open('wb') as f:
        f.write(('Slamderson R02 - ESTUDO, conferir encaixes; unidades interpretadas em mm').encode()[:80].ljust(80,b' ')); f.write(struct.pack('<I',len(faces)))
        for a,b,c in faces:
            n=(v[b]-v[a]).cross(v[c]-v[a]); n.normalize()
            f.write(struct.pack('<12fH',*n,*v[a],*v[b],*v[c],0))
    mesh=Mesh.Mesh(str(path)); assert mesh.isSolid(),name
    stls.append({'arquivo':path.name,'triangulos':len(faces),'malha_fechada':True,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
C.recompute(); C.saveAs(str(OUT/'carcaca-estudo-r02.FCStd'))
Part.makeCompound([o.Shape for o in own]).exportStep(str(OUT/'carcaca-estudo-r02.step'))
audit={'revisao':'R02','arquivo_origem':str(SOURCE.relative_to(ROOT)),'sha256_origem':source_hash,'objetos_montagem':len(D.Objects),'powerbank_mm':[150,70,30],'massa_indicada_PB_g':420,'PB_z_novo':50.8,'queda_altura_centro_PB_mm':(91+25/2)-(50.8+30/2),'cotas_carcaca_mm':{'largura':170,'comprimento':212,'parede_proposta':3,'saia_z':[49.4,90],'tampas_z':[90.6,137],'folga_seam_mm':.6},'pisos_z':[87,90],'base_C1_z':145,'folga_carcaca_para_base_C1_mm':145-137,'peças_principais':principal,'stls':stls,'alteracoes':['PB desceu para berço traseiro; ESP subiu; IMU ficou na base central; L298N 4 mm à frente.','Colunas traseiras foram deslocadas para braços laterais, fora do volume do PB.','Piso superior elevado 3 mm; ponte/C1 elevados 5 mm.','Duas tampas saem lateralmente, com rasgos para apoios do C1 e passagem de cabo.','Portinholas frontal AA e traseira PB; acesso lateral genérico e ventilação.'],'limites':['Geometria conceitual; conferir holder, ESP, cabos, portas, massas, raio real do PB e furação do chassi.','Sem cálculo estrutural, térmico, IP ou aprovação para fabricação.','A troca de posição reduz altura do PB, mas não comprova estabilidade ou centro de massa do conjunto.'],'novos_objetos':new_records}
(OUT/'parametros-r02.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==source_hash
print(json.dumps({'objetos':len(D.Objects),'carcaca_pecas':len(principal),'STLs_fechados':len(stls),'origem_preservada':True},ensure_ascii=False))
App.closeDocument(C.Name); App.closeDocument(D.Name)
