"""Kit R04 para ensaio dimensional na Ender-3 V3 SE. Não certifica montagem física."""
from pathlib import Path
import sys,json,math,hashlib,struct,csv
from collections import Counter
sys.path.insert(0,'/usr/lib/freecad/lib')
import FreeCAD as A
import Part
import Mesh
ROOT=Path(__file__).resolve().parents[2]; OUT=Path(__file__).resolve().parent
(OUT/'stl').mkdir(exist_ok=True)
SRC=ROOT/'docs/carcaca-r03/slamderson-coberto-r03.FCStd'
sha=hashlib.sha256(SRC.read_bytes()).hexdigest(); D=A.openDocument(str(SRC))
assert len(D.Objects)==110
V=A.Vector
parts=[]; joints=[]; instances={}; original={n:D.getObject(n).Shape.copy() for n in ['RaspberryPi5','L298N','MPU6050','LidarC1','Reserva_Powerbank']}
def box(x,y,z,w,l,h): return Part.makeBox(w,l,h,V(x,y,z))
def cyl(x,y,z,r,h,axis=(0,0,1)): return Part.makeCylinder(r,h,V(x,y,z),V(*axis))
def rb(x,y,z,w,l,h,r):
 s=box(x,y,z,w,l,h); es=[e for e in s.Edges if abs(e.BoundBox.ZLength-h)<1e-6 and e.BoundBox.XLength<1e-6 and e.BoundBox.YLength<1e-6]; return s.makeFillet(r,es)
def hexagon(c,axis,af,depth):
 a=V(*axis); u=V(1,0,0) if abs(a.z)>.9 or abs(a.y)>.9 else V(0,1,0); v=V(0,1,0) if abs(a.z)>.9 else V(0,0,1); r=af/math.sqrt(3)
 points=[V(*c)+u*(r*math.cos(i*math.pi/3))+v*(r*math.sin(i*math.pi/3)) for i in range(6)]; return Part.Face(Part.Wire(Part.makePolygon(points+[points[0]]).Edges)).extrude(a*depth)
def hole(s,c,axis,length=20,r=1.7): return s.cut(cyl(*c,r,length,axis))
def trap(s,c,axis): return s.cut(hexagon(c,axis,5.8,2.8))
def counter(s,x,y,z,r=1.7):
 s=hole(s,(x,y,z+1),(0,0,-1),10,r)
 return s.cut(Part.makeCone(3.2,r,1.5,V(x,y,z),V(0,0,-1)))
def put(name,shape,group='Superior',color=(.50,.22,.36)):
 o=D.getObject(name)
 if o is None:
  o=D.addObject('PartDesign::Feature',name); D.getObject(group).addObject(o)
  o.addProperty('App::PropertyColor','CorDoEstudo'); o.addProperty('App::PropertyInteger','TransparenciaEstudo'); o.addProperty('App::PropertyString','Evidencia')
 o.Placement=A.Placement(); o.Shape=shape; o.CorDoEstudo=color; o.TransparenciaEstudo=0; o.Evidencia='R04: geometria para ensaio; medidas externas/furação física exigem conferência.'
 return o

def part(code,label,shapes,names,group='Superior',rot=None,gate='',support='nao'):
 assert len(shapes)==len(names)
 obs=[]
 for i,(s,n) in enumerate(zip(shapes,names)):
  s=s.removeSplitter(); assert s.isValid() and len(s.Solids)==1,(code,n,len(s.Solids))
  o=put(n,s,group,(.72,.77,.79) if group=='Tampas' else (.12,.17,.21) if group in ('CarcacaBase','Acessos','Lidar') else (.50,.22,.36)); o.Label=code+' '+label+(' '+str(i+1) if len(names)>1 else '')
  if not hasattr(o,'CodigoPeca'): o.addProperty('App::PropertyString','CodigoPeca')
  o.CodigoPeca=code; obs.append(o)
 instances[code]=[o.Name for o in obs]
 parts.append({'codigo':code,'nome':label,'quantidade':len(obs),'objetos':instances[code],'rotacao_impressao':rot,'condicao':gate or 'cupom e montagem a seco antes do uso','suportes':support})
 return obs

# Retirar apenas geometrias ilustrativas substituídas; referências mecânicas preservadas.
remove=[]
for o in D.Objects:
 if o.Name in ['Saia','TampaEsquerda','TampaDireita','PortinholaAA','PortinholaPB','TampaServicoPB','BercoPB'] or o.Name.startswith(('ColunaPrincipal','Travessa','ApoioPonte','EspacadorC','Apoio_Pi','Apoio_L298N','ApoioESP','ApoioAA','Uniao')): remove.append(o.Name)
for n in remove: D.removeObject(n)

# Saia: paredes 3 mm, porcas M3 alojadas; sem as antigas orelhas inacessíveis da tampa.
base=rb(-85,-2,49.4,170,212,40.6,12).cut(rb(-82,1,48,164,206,44,9))
bw=D.getObject('Mecanica_00').Mesh.BoundBox; yw=(bw.YMin+bw.YMax)/2; zw=(bw.ZMin+bw.ZMax)/2
base=base.cut(cyl(-100,yw,zw,40,200,(1,0,0)))
base=base.cut(box(-41,-3,49,82,5,26)).cut(box(-77,206,50.6,154,5,33.2)).cut(box(81,136,51,5,69,32))
for x in (-86,81):
 for y in (128,136,144,152,160,168): base=base.cut(box(x,y,59,5,3,17))
# Piso preso por 4 M3x10; orelhas com 5 mm, porca no lado inferior.
for x in (-83,56):
 for y,length in ((18,12),(191,7)): base=base.fuse(box(x,y,82,27,length,5))
for x in (-61,61):
 for y in (24,194): base=trap(hole(base,(x,y,81),(0,0,1),11),(x,y,82),(0,0,1))
# AA: porcas acessíveis pelo interior, cabeça do parafuso fora.
for x in (-35,25): base=base.fuse(box(x,0,75,10,6,7))
for x in (-30,30): base=trap(hole(base,(x,-8,78.4),(0,1,0),20),(x,6,78.4),(0,-1,0))
# PB atrás: centro z86, 1.2 mm nominal acima do envelope do PB para os apoios.
for x in (-60,50): base=base.fuse(box(x,203,82,10,7,8))
for x in (-55,55): base=trap(hole(base,(x,201,86),(0,1,0),14),(x,203,86),(0,1,0))
for y in (142,199):
 base=base.fuse(box(78,y-5,82.5,7,10,7.5)); base=trap(hole(base,(74,y,86.5),(1,0,0),20),(78,y,86.5),(1,0,0))
# Parafusos exteriores dos 4 clipes de retenção da tampa, inferiores z86.
for x in (-66,66):
 for y in (-3,206): base=hole(base,(x,y,86),(0,1,0),6)

def split_with_laps(s,z):
 front=s.common(box(-200,-100,0,400,211.7,300)); rear=s.common(box(-200,112.3,0,400,300,300))
 for sign in (-1,1):
  if sign>0: root=box(78,102,z-6,5.5,9.7,12); tab=box(78,111.5,z-6,3.6,12.5,12); c=(78,118,z); ax=(1,0,0); drill=(77,118,z)
  else: root=box(-83.5,102,z-6,5.5,9.7,12); tab=box(-81.6,111.5,z-6,3.6,12.5,12); c=(-78,118,z); ax=(-1,0,0); drill=(-77,118,z)
  front=trap(hole(front.fuse(root).fuse(tab),drill,ax,12),c,ax)
  rear=hole(rear,drill,ax,12)
 return front.removeSplitter(),rear.removeSplitter()
front,rear=split_with_laps(base,82)
part('P01','Saia dianteira',[front],['SaiaFrente'],'CarcacaBase',((1,0,0),180),support='local sob orelhas e linguetas; nao preencher arcos')
part('P02','Saia traseira',[rear],['SaiaTras'],'CarcacaBase',((1,0,0),180),support='local sob orelhas e linguetas')
# Teto em 4 quartos. Parafusos de retenção HORIZONTAIS, acessíveis por frente/trás.
cap=rb(-85,-2,90.6,170,212,46.4,12).cut(rb(-82,1,89,164,206,45,9))
cap=cap.cut(box(-31,77.5,133,62,10,6)).cut(box(-6,108,133,12,8,6))
for x in range(-46,47,7): cap=cap.cut(box(x,17,133,3,45,6))
for x in (-86,81):
 for y in (20,28,36,44,52): cap=cap.cut(box(x,y,119,5,3,9))
cap=cap.cut(box(-6,-3,95,12,5,8)).cut(box(-6,206,97,12,5,8))
for x in (-66,66):
 for y in (-3,206): cap=hole(cap,(x,y,96),(0,1,0),6)
for x in (-53,53):
 for y in (104,120): cap=hole(cap,(x,y,128),(0,0,1),12)
cf,cr=split_with_laps(cap,110)
for code,label,s,sg in [('P03','Teto dianteiro esquerdo',cf,-1),('P04','Teto dianteiro direito',cf,1),('P05','Teto traseiro esquerdo',cr,-1),('P06','Teto traseiro direito',cr,1)]:
 clip=box(-200,-100,0,199.7,500,300) if sg<0 else box(.3,-100,0,200,500,300)
 part(code,label,[s.common(clip)],[code+'_Teto'],'Tampas',((1,0,0),180),support='local nas linguetas laterais; face externa do teto na mesa')
# Portinholas planas, cada cabeça acessível do lado de fora.
f=box(-47,-4.4,48.4,94,2.4,34)
for x in (-30,30): f=hole(f,(x,-7,78.4),(0,1,0),8)
part('P07','Portinhola AA',[f],['PortinholaAA'],'Acessos',((1,0,0),90))
r=box(-80,210,48.4,160,2.4,41.4)
for x in (-55,55): r=hole(r,(x,208,86),(0,1,0),8)
for x in (-66,66): r=r.cut(box(x-4,209,82.3,8,5,9))
part('P08','Portinhola PB',[r],['PortinholaPB'],'Acessos',((1,0,0),90))
s=box(85,132,49,2.4,75,40)
for y in (142,199): s=hole(s,(84,y,86.5),(1,0,0),6)
part('P09','Painel lateral PB',[s],['TampaServicoPB'],'Acessos',((0,1,0),-90))
# Pontes internas do teto, porca anti-giro aberta para dentro.
bridges=[]
for x in (-53,53):
 s=box(x-7,98,129.8,14,28,4)
 for y in (104,120): s=trap(hole(s,(x,y,129),(0,0,1),10),(x,y,129.8),(0,0,1))
 bridges.append(s)
part('P10','Uniao interna teto',bridges,['UniaoTetoE','UniaoTetoD'],rot=((1,0,0),180))
# Clipes de retenção, todos iguais; 2 porcas M3 por clipe, não ficam escondidos sob o teto.
clips=[]
for x in (-66,66):
 for back in (False,True):
  s=box(x-6,200 if back else 1,82,12,7,20)
  for z in (86,96):
   s=hole(s,(x,198 if back else -3,z),(0,1,0),15)
   s=trap(s,(x,200 if back else 8,z),(0,1,0) if back else (0,-1,0))
  clips.append(s)
part('P11','Clipe retencao tampas',clips,['ClipeFE','ClipeTE','ClipeFD','ClipeTD'],'Acessos',((1,0,0),90))
# Piso plano por baixo, nervuras por cima: elimina ponte enorme sob o piso.
floor=box(-65,8,87,130,197,3).cut(box(0,90,86,50,56,5))
for x in (-61,61):
 for y in (24,194): floor=hole(floor,(x,y,86),(0,0,1),6)
for x in (-59.5,56.5): floor=floor.fuse(box(x,135,90,3,55,2))
for x in (-66,60): floor=floor.cut(box(x,198,86,6,8,8))
for x in (-61,49): floor=floor.cut(box(x,200,86,12,7,8))
for x in (-66,63): floor=floor.cut(box(x,7.5,86,3,5,8))
frame=[(-48,33), (48,33),(-58,126),(58,126)]
for x,y in frame: floor=hole(floor,(x,y,86),(0,0,1),8)
for x in (-26.5,26.5): floor=hole(floor,(x,82.5,86),(0,0,1),8)
# Centros reais dos cilindros de fixação no CAD oficial da Pi, diâmetro 2.7 mm.
pi_xy=[(-40.3,17.13035),(17.7,17.13035),(-40.3,66.13035),(17.7,66.13035)]
for x,y in pi_xy: floor=hole(floor,(x,y,86),(0,0,1),8,1.4)
for x in (-22,22): floor=hole(floor,(x,170,86),(0,0,1),8)
# Passagem de velcro do berço ESP, sem inventar furação de placa desconhecida.
for x in (-20,15):
 for y in (146,186): floor=floor.cut(box(x,y,86,5,12,8))
part('P12','Piso superior',[floor],['PisoSuperior'],gate='conferir gabarito de chassis, placa real e cooler')
# Berço PB: parafusos escareados, não cabeças de parafuso debaixo dos 420 g.
tray=box(-78,132,48.4,156,73,2.4).fuse(box(-78,132,50.8,2,73,5)).fuse(box(76,132,50.8,2,73,5)).fuse(box(-78,132,50.8,156,2,5))
for x in (-40,40):
 for y in (147,198): tray=counter(tray,x,y,50.8)
# Dois canais inferiores para velcro 10 mm, espessura máxima de referência 1 mm.
for y in (148,186):
 tray=tray.cut(box(-77,y,48.3,154,12,1.3))
 for x in (-77,74): tray=tray.cut(box(x,y,48,3,12,9))
part('P13','Berco Basike',[tray],['BercoPB'],'Inferior',gate='gabarito chassis; conferir cintas e cantos/portas reais')
for o,y in zip([o for o in D.Objects if o.Name.startswith('CintaPowerbank')],(149,187)):
 u=box(-76,y,51,152,10,30.8).cut(box(-75,y-1,50,150,12,31))
 put(o.Name,u,'Inferior',(.09,.11,.14)); o.Label='Cinta velcro 10 mm — NAO imprimir, representação'
# Holder comercial permanece reserva: berço, não contatos/pilhas impressos.
aa=box(-40.5,7,48.4,81,76,2).fuse(box(-40.5,7,50.4,2.7,76,5)).fuse(box(37.8,7,50.4,2.7,76,5)).fuse(box(-40.5,80.3,50.4,81,2.7,5))
for x in (-30,30):
 for y in (16,74): aa=counter(aa,x,y,50.4)
part('P14','Berco holder quatro AA',[aa],['BercoAA'],'Inferior',gate='MEDIR holder real; reserva 75x70 mm, folga 0.3 mm por lado')
# Colunas principais com parafuso passante; posição no chassis ainda é gabarito.
for code,label,coords,z,h in [('P15','Coluna principal dianteira',frame[:2],48.4,38.6),('P16','Coluna principal traseira',frame[2:],52.4,34.6)]:
 ss=[hole(cyl(x,y,z,5,h),(x,y,z-1),(0,0,1),h+2) for x,y in coords]
 part(code,label,ss,[code+'_'+str(i) for i in range(2)],gate='gabarito chassis; M3x50 passante')
trav=[]
for x in (-63,48):
 center=-58 if x<0 else 58
 trav.append(hole(box(x,120,48.4,15,12,4),(center,126,47),(0,0,1),8))
part('P17','Travessa traseira',trav,['TravessaE','TravessaD'],'Inferior',gate='gabarito chassis; iguais com rotação de 180 graus')
# C1: parafuso passante da coluna separado dos quatro parafusos físicos do sensor.
cols=[hole(cyl(x,82.5,90,4,50),(x,82.5,89),(0,0,1),52) for x in (-26.5,26.5)]
part('P18','Coluna C1',cols,['ColunaC1E','ColunaC1D'],'Lidar',gate='base C1 e gabarito de furação')
plate=rb(-31,73,140,62,62,3,8).cut(box(-5,108,139,10,8,5))
for x in (-26.5,26.5): plate=counter(plate,x,82.5,143)
for x in (-21.5,21.5):
 for y in (82.5,125.5): plate=hole(plate,(x,y,139),(0,0,1),6)
part('P19','Base compacta C1',[plate],['PonteLidar'],'Lidar',gate='CONFIRMAR matriz proposta 43x43 mm; bitola/rosca do C1 real não identificada')
sp=[hole(cyl(x,y,143,2.8,2),(x,y,142),(0,0,1),5) for x in (-21.5,21.5) for y in (82.5,125.5)]
part('P20','Espacador C1',sp,['EspacadorC1_'+str(i) for i in range(4)],'Lidar',gate='não usar M3 no sensor sem conferir a rosca real')
# Pi: altura real do PCB no CAD 95.48; +0.52 permite espaçador de 6 mm.
pi=D.getObject('RaspberryPi5'); sh=pi.Shape.copy(); sh.translate(V(0,0,.52)); put(pi.Name,sh,color=tuple(pi.CorDoEstudo[:3]))
sp=[hole(cyl(x,y,90,3,6),(x,y,89),(0,0,1),9,1.4) for x,y in pi_xy]
part('P21','Espacador Pi seis mm',sp,['ApoioPi_'+str(i) for i in range(4)],gate='M2.5, não M3; conferir placa e cooler')
# L298N e MPU: apoiar o PCB, não a ponta mais baixa do envelope de componentes.
for n in ['L298N','MPU6050']:
 old=D.getObject(n); sh=old.Shape.copy(); sh.translate(V(0,-3 if n=='L298N' else 0,.6)); put(n,sh,'Inferior',tuple(old.CorDoEstudo[:3]))
lxy=[(6,90),(43,90),(6,127),(43,127)]
sp=[hole(cyl(x,y,48.4,3,10),(x,y,47.4),(0,0,1),13) for x,y in lxy]
part('P22','Espacador L298N dez mm',sp,['ApoioL298_'+str(i) for i in range(4)],'Inferior',gate='CAD de referência 37x37 mm; confirmar módulo/chassis reais')
mxy=[(-.5,112.5),(-.5,128.5)]
sp=[hole(cyl(x,y,48.4,3,4),(x,y,47.4),(0,0,1),7,1.4) for x,y in mxy]
part('P23','Espacador MPU quatro mm',sp,['ApoioMPU_'+str(i) for i in range(2)],'Inferior',gate='CAD de referência, conferir módulo real')
# ESP sem modelo final: berço com espuma e velcro, sem inventar furos de placa.
e=box(-17.3,140,90,34.6,61,2).fuse(box(-17.3,140,92,3,61,3)).fuse(box(14.3,140,92,3,61,3))
for x in (-26,14): e=e.fuse(box(x,164,90,12,12,3))
for x in (-22,22): e=hole(e,(x,170,89),(0,0,1),7)
for x in (-17.4,14.2):
 for y in (146,186): e=e.cut(box(x,y,89,3.2,12,7))
part('P24','Berco ESP por velcro',[e],['BercoESP'],gate='MEDIR placa ESP; usar espuma isolante 2 mm e velcro, sem furos fictícios')
# Cupom de calibração separado, não componente da montagem.
Q=A.newDocument('CupomR04'); coupon=box(0,0,0,70,38,5)
notch=Part.Face(Part.Wire(Part.makePolygon([V(0,0,-1),V(5,0,-1),V(0,5,-1),V(0,0,-1)]).Edges)).extrude(V(0,0,7))
coupon=coupon.cut(notch)
for i,r in enumerate((1.6,1.7,1.8)):
 coupon=hole(coupon,(12+23*i,11,-1),(0,0,1),8,r)
 coupon=hole(coupon,(12+23*i,28,-1),(0,0,1),8)
 coupon=coupon.cut(hexagon((12+23*i,28,5),(0,0,-1),(5.7,5.8,5.9)[i],2.8))
qo=Q.addObject('PartDesign::Feature','Cupom'); qo.Shape=coupon; Q.recompute(); Q.saveAs(str(OUT/'cupom-encaixe.FCStd'))

# Ferragens: geometrias de envelope, roscas não modeladas. Não exportar como STL.
if D.getObject('FerragensR04') is None: D.addObject('App::DocumentObjectGroup','FerragensR04')
def joint(code,desc,c,axis,length,metric=3,flat=False,nut=None,trap_part=None,targets=None,gate=''):
 c=V(*c); a=V(*axis); r=metric/2
 if flat:
  shaft=Part.makeCylinder(r,length-1.5,c+a*1.5,a); head=Part.makeCone(3,1.5,1.5,c,a); solid=shaft.fuse(head)
 else:
  solid=Part.makeCylinder(r,length,c,a).fuse(Part.makeCylinder(2.75 if metric==3 else 2.25,3 if metric==3 else 2.5,c-a*(3 if metric==3 else 2.5),a))
 obj=put('Parafuso_'+code+'_'+str(len(joints)),solid,'FerragensR04',(.12,.46,.48)); obj.Label=code+' '+desc
 if not flat:
  washer=Part.makeCylinder(3.5 if metric==3 else 3,.5,c,a).cut(Part.makeCylinder(r+.2,.7,c-a*.1,a)); put('Arruela_'+str(len(joints)),washer,'FerragensR04',(.68,.70,.72))
 if nut is not None:
  p,ax=nut; th=2.4 if metric==3 else 2.; af=5.5 if metric==3 else 5.
  ns=hexagon(p,ax,af,th).cut(cyl(*p,r,th,ax)); put('Porca_'+str(len(joints)),ns,'FerragensR04',(.62,.64,.66))
  if trap_part is None and code!='O':
   # Arruela sob porca livre: acima dela nos parafusos descendentes, abaixo nos ascendentes.
   start=V(*p)+V(*ax)*th if a.z<0 else V(*p)
   direction=V(0,0,1) if a.z<0 else V(0,0,-1)
   ws=Part.makeCylinder(3.5 if metric==3 else 3,.5,start,direction).cut(Part.makeCylinder(r+.2,.7,start-direction*.1,direction))
   put('ArruelaPorca_'+str(len(joints)),ws,'FerragensR04',(.68,.70,.72))
 joints.append({'grupo':code,'descricao':desc,'metrica':'M'+str(metric),'comprimento_mm':length,'cabeca':'escareada 90 graus' if flat else 'cilindrica Allen','posicao_cabeca_mm':list(c),'eixo_para_dentro':list(a),'porca_alojada_em':trap_part,'alvos':targets or [],'condicao':gate,'objeto_parafuso':obj.Name,'porca':nut,'arruela_cabeca':not flat,'arruela_porca':trap_part is None and nut is not None and code!='O'})
# Clipe: 4 inferiores para instalar, 4 superiores para remover as tampas.
for x in (-66,66):
 for back in (False,True):
  for z in (86,96):
   joint('A','Clipe de retencao, '+('tampa' if z==96 else 'saia'),(x,210.5 if back else -2.5,z),(0,-1,0) if back else (0,1,0),12,nut=((x,200.4 if back else 5.2,z),(0,1,0)),trap_part='P11',targets=['P11',('P05/P06' if back else 'P03/P04') if z==96 else ('P02' if back else 'P01')])
for z,role in [(82,'Uniao saia'),(110,'Uniao lateral teto')]:
 for sg in (-1,1): joint('B' if z==82 else 'C',role,(sg*85.5,118,z),(-sg,0,0),10,nut=((sg*78.4,118,z),(sg,0,0)),trap_part='P01' if z==82 else 'P03/P04',targets=['P01','P02'] if z==82 else ['P03/P04','P05/P06'])
for x in (-53,53):
 for y in (104,120): joint('D','Ponte interna teto',(x,y,137.5),(0,0,-1),10,nut=((x,y,130.2),(0,0,1)),trap_part='P10',targets=['P10','P03/P04/P05/P06'])
for x in (-30,30): joint('E','Portinhola AA',(x,-4.9,78.4),(0,1,0),12,nut=((x,3.2,78.4),(0,1,0)),trap_part='P01',targets=['P01','P07'])
for x in (-55,55): joint('F','Portinhola PB',(x,212.9,86),(0,-1,0),12,nut=((x,203.4,86),(0,1,0)),trap_part='P02',targets=['P02','P08'])
for y in (142,199): joint('G','Painel lateral PB',(87.9,y,86.5),(-1,0,0),12,nut=((78.4,y,86.5),(1,0,0)),trap_part='P02',targets=['P02','P09'])
for x in (-61,61):
 for y in (24,194): joint('H','Piso na saia',(x,y,90.5),(0,0,-1),10,nut=((x,y,82.4),(0,0,1)),trap_part='P01/P02',targets=['P12','P01/P02'])
for x,y in frame: joint('I','Colunas principais no chassis',(x,y,44.9),(0,0,1),50,nut=((x,y,90.5),(0,0,1)),targets=['chassis','P12','P15/P16/P17'],gate='Conferir material/espessura 3 mm e furação do chassis físico')
for x in (-26.5,26.5): joint('J','Coluna C1 no piso e base',(x,82.5,142.8),(0,0,-1),60,flat=True,nut=((x,82.5,84.1),(0,0,1)),targets=['P12','P18','P19'])
for x,y in pi_xy: joint('K','Pi no piso',(x,y,97.776),(0,0,-1),16,metric=2.5,nut=((x,y,84.5),(0,0,1)),targets=['RaspberryPi5','P21','P12'],gate='Arruelas isolantes; conferir cooler e espessura real do PCB')
for code,xy,top,desc,pc in [('L',[(x,y) for x in (-40,40) for y in (147,198)],50.6,'Berco PB no chassis','P13'),('M',[(x,y) for x in (-30,30) for y in (16,74)],50.2,'Berco AA no chassis','P14')]:
 for x,y in xy: joint(code,desc,(x,y,top),(0,0,-1),10,flat=True,nut=((x,y,42.5),(0,0,1)),targets=['chassis',pc],gate='Conferir gabarito do chassis e cabeça abaixo do plano do berço')
for x,y in lxy: joint('N','L298N no chassis',(x,y,60.5),(0,0,-1),20,nut=((x,y,42.5),(0,0,1)),targets=['chassis','P22','L298N'],gate='Modelo de módulo e chassis precisam conferir')
for x,y in mxy: joint('O','MPU no chassis',(x,y,54.5),(0,0,-1),12,metric=2.5,nut=((x,y,43.4),(0,0,1)),targets=['chassis','P23','MPU6050'],gate='Uma arruela isolante sobre PCB; conferir módulo')
for x in (-22,22): joint('P','Berco ESP no piso',(x,170,93.5),(0,0,-1),10,nut=((x,170,84.1),(0,0,1)),targets=['P24','P12'])
D.getObject('Escopo').Aviso='R04 para Ender-3 V3 SE. Parafusos definidos entre peças próprias; chassi, holder, ESP, C1 físicos ainda exigem gabarito. Não liberar fabricação final sem cupom e montagem a seco.'
D.recompute(); D.saveAs(str(OUT/'slamderson-impressao-r04.FCStd'))
# STL orientados individualmente em mm, face de impressão em z=0, não layout de montagem.
P=A.newDocument('PecasR04'); rows=[]
for record in parts+[{'codigo':'P25','nome':'Cupom M3 e porcas','quantidade':1,'objetos':[],'rotacao_impressao':None,'condicao':'IMPRIMIR PRIMEIRO: furos 3.2/3.4/3.6 e porcas AF5.7/5.8/5.9','suportes':'nao'}]:
 s=(D.getObject(record['objetos'][0]).Shape if record['objetos'] else coupon).copy()
 if record['rotacao_impressao']:
  axis,angle=record['rotacao_impressao']; s.rotate(V(0,0,0),V(*axis),angle)
 b=s.BoundBox; s.translate(V(-b.XMin,-b.YMin,-b.ZMin)); b=s.BoundBox
 assert b.XLength+16<=220 and b.YLength+16<=220 and b.ZLength<=250,(record['codigo'],b)
 o=P.addObject('PartDesign::Feature',record['codigo']); o.Shape=s.copy(); o.Label=record['codigo']+' '+record['nome']
 idx=len(P.Objects)-1; o.Placement.Base=V((idx%5)*235,(idx//5)*235,0)
 verts,faces=s.tessellate(.15); path=OUT/'stl'/(record['codigo']+'.stl')
 with path.open('wb') as f:
  f.write(('SLAMDerson R04 mm '+record['codigo']).encode().ljust(80,b' ')); f.write(struct.pack('<I',len(faces)))
  for a,b1,c in faces:
   n=(verts[b1]-verts[a]).cross(verts[c]-verts[a]); assert n.Length>1e-12; n.normalize(); f.write(struct.pack('<12fH',*n,*verts[a],*verts[b1],*verts[c],0))
 mesh=Mesh.Mesh(str(path)); assert mesh.isSolid(),record['codigo']
 record.update({'arquivo':'stl/'+path.name,'dimensoes_impressao_mm':[b.XLength,b.YLength,b.ZLength],'triangulos':len(faces),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'volume_mm3':s.Volume}); rows.append(record)
P.recompute(); P.saveAs(str(OUT/'pecas-impressao-r04.FCStd'))
Part.makeCompound([o.Shape for o in P.Objects]).exportStep(str(OUT/'pecas-impressao-r04.step'))
# Geometria de orientação sem brigar com sobreposição intencional dos objetos na origem.
bom=Counter((j['metrica'],j['comprimento_mm'],j['cabeca']) for j in joints)
audit={'revisao':'R04','origem':str(SRC.relative_to(ROOT)),'sha256_origem':sha,'impressora':'Ender-3 V3 SE','volume_referencia_mm':[220,220,250],'bico_assumido_mm':.4,'camada_assumida_mm':.2,'brim_referencia_mm':5,'margem_adicional_por_borda_mm':3,'gap_junta_corpo_mm':.6,'folga_lateral_lingueta_mm':.4,'furo_passante_M3_mm':3.4,'bolso_porca_M3_AF_mm':5.8,'bolso_porca_M3_profundidade_mm':2.8,'pecas':rows,'quantidade_tipos_STL':len(rows),'quantidade_total_a_imprimir':sum(r['quantidade'] for r in rows),'parafusos':joints,'bom_parafusos':[{'metrica':a,'comprimento_mm':b,'cabeca':c,'quantidade':q} for (a,b,c),q in sorted(bom.items())],'furos_C1_pendentes':{'quantidade':4,'matriz_proposta_mm':[43,43],'bitola':'PENDENTE medir rosca e profundidade, não presumir M3'},'pi_furos_CAD_xy_mm':pi_xy,'mudancas_PCB_mm':{'Pi_delta_z':.52,'L298N_delta_z':.6,'MPU_delta_z':.6},'externos_nao_imprimir':['chassis original','rodas, motores, rodizio','holder/pilhas AA','placas/sensor','cintas velcro e espuma','porcas, parafusos, arruelas'],'limitacoes':['Nenhuma impressão ou montagem física executada.','Furação e espessura do chassi real não medidas. Gabarito obrigatório antes de furar.','Holder e ESP não escolhidos: berços condicionais.','Fixação do sensor C1 não pode usar rosca presumida.','Sem análise estrutural, estabilidade ou térmica em carga.']}
(OUT/'kit-r04.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
with (OUT/'lista-pecas.csv').open('w',newline='') as f:
 w=csv.writer(f); w.writerow(['codigo','nome','quantidade','X_mm','Y_mm','Z_mm','suportes','condicao']);
 for r in rows: w.writerow([r['codigo'],r['nome'],r['quantidade'],*[round(v,3) for v in r['dimensoes_impressao_mm']],r['suportes'],r['condicao']])
assert hashlib.sha256(SRC.read_bytes()).hexdigest()==sha
print(json.dumps({'tipos_STL':len(rows),'pecas_com_cupom':sum(r['quantidade'] for r in rows),'parafusos_modelados':len(joints),'bom':audit['bom_parafusos']},ensure_ascii=False))
for d in [P,Q,D]: A.closeDocument(d.Name)
