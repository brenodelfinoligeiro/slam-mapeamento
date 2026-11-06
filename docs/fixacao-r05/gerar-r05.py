"""Revisão R05: derivado somente da R04 preservada. FreeCAD headless."""
from pathlib import Path
import sys, json, math, hashlib, struct, csv
from collections import Counter
sys.path.insert(0, '/usr/lib/freecad/lib')
import FreeCAD as A
import Part
import Mesh
ROOT=Path(__file__).resolve().parents[2]; OUT=Path(__file__).resolve().parent
SRC=ROOT/'docs/impressao-r04/slamderson-impressao-r04.FCStd'
SOURCE_FILES=[SRC,SRC.parent/'gerar-r04.py',SRC.parent/'kit-r04.json']
source_hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCE_FILES}
K4=json.loads((SRC.parent/'kit-r04.json').read_text())
D=A.openDocument(str(SRC)); V=A.Vector
(OUT/'stl').mkdir(exist_ok=True)
parts=[]; inserts=[]; joints=[]
def box(x,y,z,w,l,h): return Part.makeBox(w,l,h,V(x,y,z))
def cyl(x,y,z,r,h,axis=(0,0,1)): return Part.makeCylinder(r,h,V(x,y,z),V(*axis))
def rb(x,y,z,w,l,h,r):
 s=box(x,y,z,w,l,h); es=[e for e in s.Edges if abs(e.BoundBox.ZLength-h)<1e-6 and e.BoundBox.XLength<1e-6 and e.BoundBox.YLength<1e-6]; return s.makeFillet(r,es)
def hole(s,c,axis,length=20,r=1.7): return s.cut(cyl(*c,r,length,axis))
def counter(s,c,axis):
 s=hole(s,tuple(V(*c)-V(*axis)*.1),axis,10)
 return s.cut(Part.makeCone(3.2,1.7,1.5,V(*c),V(*axis)))
def bore(s,owner,c,axis):
 ident='INS%03d'%(len(inserts)+1)
 inserts.append({'id':ident,'objeto':owner,'entrada_mm':list(c),'eixo_para_dentro':list(axis),'comprimento_inserto_mm':5.68,'diametro_envelope_mm':4.7,'diametro_piloto_proposto_mm':4.3,'profundidade_proposta_mm':6.,'instalacao':'termica fora da montagem; antes das placas e bateria; piloto a confirmar no cupom'})
 return hole(s,tuple(V(*c)-V(*axis)*.001),axis,6.001,2.15)
def put(n,s,group='Superior',color=(.50,.22,.36)):
 o=D.getObject(n)
 if o is None: o=D.addObject('PartDesign::Feature',n); D.getObject(group).addObject(o)
 for typ,prop in [('App::PropertyColor','CorDoEstudo'),('App::PropertyString','Evidencia')]:
  if not hasattr(o,prop): o.addProperty(typ,prop)
 o.Placement=A.Placement(); o.Shape=s; o.CorDoEstudo=color; o.Evidencia='R05 proposta para cupom/montagem a seco. Não certifica fabricação nem interfaces físicas.'
 return o
def part(code,label,ss,nn,group='Superior',rot=None,gate='Cupom e medidas físicas pendentes',support='nao'):
 for s,n in zip(ss,nn):
  s=s.removeSplitter(); assert s.isValid() and len(s.Solids)==1,(code,n,len(s.Solids))
  o=put(n,s,group,(.72,.77,.79) if group=='Tampas' else (.12,.17,.21) if group in ('CarcacaBase','Acessos','Lidar') else (.5,.22,.36)); o.Label=code+' '+label
  if not hasattr(o,'CodigoPeca'): o.addProperty('App::PropertyString','CodigoPeca')
  o.CodigoPeca=code
 parts.append({'codigo':code,'nome':label,'quantidade':len(nn),'objetos':nn,'rotacao_impressao':rot,'condicao':gate,'suportes':support})
def screw(group,desc,c,axis,L,owner,entry,flat=False):
 # c = plano sob cabeça, ou face externa da cabeça escareada. Arruela ocupa os primeiros 0.5 mm.
 a=V(*axis); p=V(*c); e=V(*entry); dist=(e-p).dot(a); engage=L-dist
 assert (e-p-a*dist).Length<1e-6 and 3<=engage<=5.3,(group,c,entry,engage)
 ins=[i for i in inserts if i['objeto']==owner and (V(*i['entrada_mm'])-e).Length<1e-6 and V(*i['eixo_para_dentro']).dot(a)>.99]
 assert len(ins)==1,(group,owner,entry)
 if flat: s=cyl(*(p+a*1.5),1.5,L-1.5,axis).fuse(Part.makeCone(3,1.5,1.5,p,a))
 else: s=cyl(*c,1.5,L,axis).fuse(cyl(*(p-a*3),2.75,3,axis))
 n='Parafuso_R05_%03d'%(len(joints)+1); put(n,s,'FerragensR05',(.12,.46,.48)).Label=group+' '+desc
 wn=None
 if not flat:
  wn='Arruela_R05_%03d'%(len(joints)+1)
  put(wn,cyl(*c,3.5,.5,axis).cut(cyl(*(p-a*.01),1.7,.52,axis)),'FerragensR05',(.68,.70,.72))
 joints.append({'grupo':group,'descricao':desc,'metrica':'M3','comprimento_mm':L,'cabeca':'escareada 90 graus' if flat else 'cilindrica Allen','posicao_cabeca_mm':list(c),'eixo_para_dentro':list(axis),'inserto':ins[0]['id'],'objeto_inserto':owner,'engate_mm':round(engage,6),'folga_ponta_ao_fim_inserto_mm':round(5.68-engage,6),'folga_ponta_fundo_mm':round(6-engage,6),'objeto_parafuso':n,'objeto_arruela':wn})
# Remover todas as peças próprias antigas e ferragens; referências externas permanecem.
for o in list(D.Objects):
 if hasattr(o,'CodigoPeca') or o.Name.startswith(('Parafuso_','Porca_','Arruela','CintaPowerbank')): D.removeObject(o.Name)
if D.getObject('FerragensR04'): D.removeObject('FerragensR04')
D.addObject('App::DocumentObjectGroup','FerragensR05')
# Referências, deltas em relação à R04, sem modificar os arquivos de origem.
for n,dv in [('Reserva_Powerbank',(0,1,0)),('L298N',(0,-3,4)),('MPU6050',(-12,-3,8))]:
 o=D.getObject(n); s=o.Shape.copy(); s.translate(V(*dv)); put(n,s,'Inferior',tuple(o.CorDoEstudo[:3]))
frame=[(-48,33),(48,33),(-58,126),(58,126)]
pi_xy=[(-40.3,17.13035),(17.7,17.13035),(-40.3,66.13035),(17.7,66.13035)]
# Saia: nova geometria, nenhum bolso sextavado herdado.
base=rb(-85,-2,49.4,170,212,40.6,12).cut(rb(-82,1,48,164,206,44,9))
bw=D.getObject('Mecanica_00').Mesh.BoundBox; yw=(bw.YMin+bw.YMax)/2; zw=(bw.ZMin+bw.ZMax)/2
base=base.cut(cyl(-100,yw,zw,40,200,(1,0,0)))
base=base.cut(box(-41,-3,49,82,5,26)).cut(box(-77,206,50.6,154,5,33.2)).cut(box(81,136,51,5,69,32))
for x in (-86,81):
 for y in (128,136,144,152,160,168): base=base.cut(box(x,y,59,5,3,17))
for x in (-83,56):
 for y,l in ((18,12),(185,10)): base=base.fuse(box(x,y,82,27,l,5))
for x in (-61,61):
 for y in (24,190): base=counter(base,(x,y,82),(0,0,1))
for x in (-30,30):
 base=base.fuse(box(x-5,-2,73.4,10,12,10))
 base=bore(base,'SaiaFrente',(x,-2,78.4),(0,1,0))
for x in (-55,55):
 base=base.fuse(box(x-5,198,81.5,10,12,10.5))
 base=bore(base,'SaiaTras',(x,210,86),(0,-1,0))
for y in (142,199):
 base=base.fuse(box(76,y-5,82,9,10,10)); base=bore(base,'SaiaTras',(85,y,86.5),(-1,0,0))
for x in (-66,66):
 for y in (-3,206): base=hole(base,(x,y,86.5),(0,1,0),6)
def split(s,z,frontowners):
 f=s.common(box(-200,-100,0,400,211.7,300)); r=s.common(box(-200,112.3,0,400,300,300))
 for sg,owner in zip((-1,1),frontowners):
  if sg>0: root=box(73,102,z-6,10.5,9.7,12); tab=box(73,111.5,z-6,8.6,12.5,12)
  else: root=box(-83.5,102,z-6,10.5,9.7,12); tab=box(-81.6,111.5,z-6,8.6,12.5,12)
  f=bore(f.fuse(root).fuse(tab),owner,(sg*81.6,118,z),(-sg,0,0))
  r=hole(r,(sg*86,118,z),(-sg,0,0),5)
 return f.removeSplitter(),r.removeSplitter()
f,r=split(base,82,['SaiaFrente','SaiaFrente'])
part('P01','Saia dianteira',[f],['SaiaFrente'],'CarcacaBase',((1,0,0),180),support='local sob orelhas/linguetas; nao preencher arcos')
part('P02','Saia traseira',[r],['SaiaTras'],'CarcacaBase',((1,0,0),180),support='local sob orelhas/linguetas')
cap=rb(-85,-2,90.6,170,212,46.4,12).cut(rb(-82,1,89,164,206,45,9))
# Rasgo aberto em cada meia tampa, OD10 dos posts com folga.
cap=cap.cut(box(-31.5,78,133,63,12,6)).cut(box(-6,108,133,12,8,6))
for x in range(-46,47,7): cap=cap.cut(box(x,17,133,3,45,6))
for x in (-86,81):
 for y in (20,28,36,44,52): cap=cap.cut(box(x,y,119,5,3,9))
cap=cap.cut(box(-6,-3,95,12,5,8)).cut(box(-6,206,97,12,5,8))
for y in (142,199): cap=cap.cut(box(75.8,y-5.2,90.5,10,10.4,1.9))
for x in (-60.2,49.8): cap=cap.cut(box(x,197.8,90.5,10.4,13,1.9))
for x in (-66,66):
 for y in (-3,206): cap=hole(cap,(x,y,96.5),(0,1,0),6)
for x in (-53,53):
 for y in (104,120): cap=hole(cap,(x,y,128),(0,0,1),12)
cf,cr=split(cap,110,['P03_Teto','P04_Teto'])
for code,label,s,sg in [('P03','Teto dianteiro esquerdo',cf,-1),('P04','Teto dianteiro direito',cf,1),('P05','Teto traseiro esquerdo',cr,-1),('P06','Teto traseiro direito',cr,1)]:
 clip=box(-200,-100,0,199.7,500,300) if sg<0 else box(.3,-100,0,200,500,300)
 part(code,label,[s.common(clip)],[code+'_Teto'],'Tampas',((1,0,0),180),support='local linguetas; face externa na mesa')
f=box(-47,-4.4,48.4,94,2.4,34).fuse(box(-25,-2,52,50,11.6,17))
for x in (-30,30): f=hole(f,(x,-7,78.4),(0,1,0),8)
part('P07','Portinhola AA com batente plano holder',[f],['PortinholaAA'],'Acessos',((1,0,0),90))
r=box(-80,210,48.4,160,2.4,41.4).fuse(box(-50,206.4,55,100,3.6,22))
for x in (-55,55): r=hole(r,(x,208,86),(0,1,0),8)
for x in (-66,66): r=r.cut(box(x-4,209,82.8,8,5,8))
part('P08','Portinhola PB com batente plano',[r],['PortinholaPB'],'Acessos',((1,0,0),90),support='local no batente')
s=box(85,132,49,2.4,75,40)
for y in (142,199): s=hole(s,(84,y,86.5),(1,0,0),6)
part('P09','Painel lateral PB',[s],['TampaServicoPB'],'Acessos',((0,1,0),-90))
bridges=[]
for x,n in [(-53,'UniaoTetoE'),(53,'UniaoTetoD')]:
 s=box(x-7,98,124.8,14,28,9)
 for y in (104,120): s=bore(s,n,(x,y,133.8),(0,0,-1))
 bridges.append(s)
part('P10','Ponte teto insertos',bridges,['UniaoTetoE','UniaoTetoD'],rot=((1,0,0),180))
clips=[]; names=[]
for x in (-66,66):
 for back in (False,True):
  n='Clipe'+('T' if back else 'F')+('E' if x<0 else 'D'); names.append(n)
  s=box(x-6,198 if back else 1,82,12,9,20)
  for z in (86.5,96.5): s=bore(s,n,(x,207 if back else 1,z),(0,-1,0) if back else (0,1,0))
  clips.append(s)
part('P11','Clipe retencao tampas',clips,names,'Acessos',((1,0,0),90))
# Piso e apoios Pi integrados: pinos polimericos 2.2 mm, nao parafusos no PCB.
floor=box(-65,8,87,130,197,3).cut(box(0,90,86,50,56,5))
for x in (-59.5,56.5): floor=floor.fuse(box(x,135,90,3,55,2))
for x in (-66,59):
 floor=floor.cut(box(x,197,86,7,9,18)).cut(box(x,7.5,86,7,3.5,18))
for x in (-61,49): floor=floor.cut(box(x,197,86,12,9,18))
for x,y in frame: floor=hole(floor,(x,y,86),(0,0,1),8)
for x in (-25.5,25.5): floor=hole(floor,(x,84,86),(0,0,1),8)
for x,y in pi_xy: floor=floor.fuse(cyl(x,y,90,3,6)).fuse(cyl(x,y,96,1.1,.8))
for x in (-40.3,17.7):
 for y in (7.5,75.5):
  # Conector inferior garante fusao mesmo para boss que ultrapassa o limite Y8.
  floor=floor.fuse(cyl(x,y,87,5,10.8)); floor=bore(floor,'PisoSuperior',(x,y,97.8),(0,0,-1))
for x in (-61,61):
 for y in (24,190):
  floor=floor.fuse(cyl(x,y,87,5,8)); floor=bore(floor,'PisoSuperior',(x,y,87),(0,0,1))
for x in (-22,22): floor=hole(floor,(x,170,86),(0,0,1),8)
part('P12','Piso com apoio Pi e insertos',[floor],['PisoSuperior'])
# Gaveta PB rigida: apoio plano, labios superiores e janela USB provisoria.
tray=box(-80,132,48.4,160,74,2.4)
for x in (-80,76): tray=tray.fuse(box(x,132,50.8,4,74,30.6))
for x in (-80,73): tray=tray.fuse(box(x,132,81.4,7,74,2.4))
tray=tray.fuse(box(-80,132,50.8,160,3.4,25.2))
tray=tray.cut(box(75.9,145,58,5,50,18))
for x in (-58,58): tray=counter(tray,(x,135.4,70),(0,-1,0))
tray=tray.common(rb(-81.6,1.4,48,163.2,205.2,40,8.6))
for y in (142,199): tray=tray.cut(box(75.8,y-5.4,81.9,6,10.8,3))
for x in (-81,72.8): tray=tray.cut(box(x,184.6,81.4,8.2,10.8,3))
part('P13','Gaveta rigida Basike',[tray],['BercoPB'],'Inferior',support='local nos labios; sem suporte em janela USB',gate='420g sem prova estatica; medir portas e cantos reais')
# Holder removivel com duas reguas rigidas P29; bosses fora do envelope comercial.
aa=box(-40.5,7,48.4,81,76,2).fuse(box(-40.5,7,50.4,2.7,76,5)).fuse(box(37.8,7,50.4,2.7,76,5)).fuse(box(-40.5,80.3,50.4,81,2.7,5))
aa_coords=[(x,y) for x in (-44,44) for y in (6,74)]
for x,y in aa_coords:
 aa=aa.fuse(box(-46 if x<0 else 37.8,y-4.5,48.4,8.2,9,2)).fuse(cyl(x,y,48.4,4.5,26.8))
 aa=bore(aa,'BercoAA',(x,y,48.4),(0,0,1)); aa=bore(aa,'BercoAA',(x,y,75.2),(0,0,-1))
for x in (6,43): aa=aa.cut(cyl(x,87,48,5.4,15))
part('P14','Berco holder com bosses externos',[aa],['BercoAA'],'Inferior',gate='Holder nao medido; P29 separado permite introduzir de cima')
# Colunas estruturais, insertos opostos, sem parafusos longos.
for code,coords,z,h in [('P15',frame[:2],48.4,38.6),('P16',frame[2:],52.4,34.6)]:
 ss=[]; nn=[]
 for idx,(x,y) in enumerate(coords):
  n=code+'_'+str(idx); nn.append(n); s=cyl(x,y,z,5,h)
  if code=='P16': s=s.fuse(box(x-5,126,64,10,6,12)); s=bore(s,n,(x,132,70),(0,-1,0))
  s=bore(s,n,(x,y,z),(0,0,1)); s=bore(s,n,(x,y,87),(0,0,-1)); ss.append(s)
 part(code,'Coluna principal '+('dianteira' if code=='P15' else 'traseira'),ss,nn)
trav=[]
for x in (-63,48):
 center=-58 if x<0 else 58; trav.append(hole(box(x,120,48.4,15,12,4),(center,126,47),(0,0,1),8))
trav[1]=trav[1].cut(cyl(51.5,117.5,48,5.2,6))
trav[0]=trav[0].cut(cyl(-51.5,134.5,48,5.2,6))
part('P17','Travessa traseira',trav,['TravessaE','TravessaD'],'Inferior')
cols=[]
for x,n in [(-25.5,'ColunaC1E'),(25.5,'ColunaC1D')]:
 s=cyl(x,84,90,5,50); s=bore(s,n,(x,84,90),(0,0,1)); s=bore(s,n,(x,84,140),(0,0,-1)); cols.append(s)
part('P18','Coluna C1 insertos opostos',cols,['ColunaC1E','ColunaC1D'],'Lidar')
plate=rb(-31,73,140,62,62,3,8).cut(box(-5,108,139,10,8,5))
for x in (-25.5,25.5): plate=counter(plate,(x,84,143),(0,0,-1))
for x in (-21.5,21.5):
 for y in (82.5,125.5): plate=hole(plate,(x,y,139),(0,0,1),6)
part('P19','Base C1 estrutural separada da matriz ilustrativa',[plate],['PonteLidar'],'Lidar',gate='Fixacao REAL C1 desconhecida; quatro furos 43x43 apenas estudo, sem parafusos')
sp=[hole(cyl(x,y,143,2.8,2),(x,y,142),(0,0,1),5) for x in (-21.5,21.5) for y in (82.5,125.5)]
part('P20','Espacador C1 ilustrativo',sp,['EspacadorC1_'+str(i) for i in range(4)],'Lidar',gate='Matriz e rosca C1 desconhecidas; nao montar sensor antes de medir')
# L298N: terminais do CAD invadem cabecas M3. Manter PCB intacta e usar quadro P30.
lxy=[(6,87),(43,87),(6,124),(43,124)]
l_ext=[(-3,99),(51.5,117.5)]
s=box(6,85,60.8,45.5,2.2,1.6).fuse(box(6,122,60.8,45.5,4,1.6)).fuse(box(47.5,87,60.8,4,37,1.6)).fuse(box(-5,87,60.8,4,12,1.6)).fuse(box(-3,85,60.8,9,4,1.6))
for x,y in lxy:
 s=s.fuse(cyl(x,y,48.4,5,14)).fuse(cyl(x,y,62.4,1.1,.8))
 s=bore(s,'BercoL298',(x,y,48.4),(0,0,1))
for x,y in l_ext:
 s=s.fuse(cyl(x,y,48.4,5,16.1))
 s=bore(s,'BercoL298',(x,y,48.4),(0,0,1)); s=bore(s,'BercoL298',(x,y,64.5),(0,0,-1))
part('P22','Berco L298 com pinos e bosses externos',[s],['BercoL298'],'Inferior',support='local sob travessas a Z60.8; evitar suporte nos pilotos',gate='Pinos nos furos3.2 CAD; quadro P30 rigido evita terminais sobre os parafusos')
# MPU berco no chassi; dois pinos polimericos e presilhas externas.
s=box(-17.5,104,48.4,17.5,27,2.4)
for y in (109.5,125.5):
 s=s.fuse(cyl(-12.5,y,50.8,3,9.6)).fuse(cyl(-12.5,y,60.4,1.1,.8)).fuse(cyl(-5,y,48.4,5,14.1))
 s=bore(s,'BercoMPU',(-5,y,48.4),(0,0,1)); s=bore(s,'BercoMPU',(-5,y,62.5),(0,0,-1))
part('P23','Berco MPU isolado da gaveta',[s],['BercoMPU'],'Inferior')
# ESP sem furos inventados: berco e quadro rigido separados.
e=box(-17.3,140,90,34.6,61,2).fuse(box(-17.3,140,92,3,61,18)).fuse(box(14.3,140,92,3,61,18))
e=e.fuse(box(-17.3,140,92,34.6,2,18)).fuse(box(-17.3,199,92,34.6,2,18))
for x in (-22,22):
 e=e.fuse(box(x-5,165,90,10,10,3)).fuse(cyl(x,170,90,5,20))
 e=bore(e,'BercoESP',(x,170,90),(0,0,1)); e=bore(e,'BercoESP',(x,170,110),(0,0,-1))
part('P24','Berco ESP rigido',[e],['BercoESP'])
# P25 cupom separado, nunca componente da montagem.
Q=A.newDocument('CupomR05'); coupon=box(0,0,0,66,28,8)
notch=Part.Face(Part.Wire(Part.makePolygon([V(0,0,-1),V(5,0,-1),V(0,5,-1),V(0,0,-1)]).Edges)).extrude(V(0,0,10))
coupon=coupon.cut(notch)
for i,d in enumerate((4.2,4.3,4.4)): coupon=hole(coupon,(11+22*i,14,8),(0,0,-1),6,d/2)
qo=Q.addObject('PartDesign::Feature','Cupom'); qo.Shape=coupon
qo.addProperty('App::PropertyString','CodigoPeca'); qo.CodigoPeca='P25'
qo.addProperty('App::PropertyColor','CorDoEstudo'); qo.CorDoEstudo=(.5,.22,.36)
Q.recompute(); Q.saveAs(str(OUT/'cupom-insertos-r05.FCStd'))
# Quadro ESP: sobreposicao projetada 1 mm nas bordas e folga vertical1.4 mm.
# O PCB real nao foi medido: conferir bordas livres antes de fabricar o quadro.
t=box(-27,138,110.4,54,65,3).cut(box(-13,144,110,26,53,5))
for x in (-22,22): t=hole(t,(x,170,110),(0,0,1),5)
part('P26','Quadro retencao ESP',[t],['QuadroESP'])
# Presilhas Pi: uma geometria, traseiras giradas 180 graus.
ss=[]; nn=[]
for x in (-40.3,17.7):
 for back in (False,True):
  y=75.5 if back else 7.5; n='PresilhaPi_'+str(len(nn)); nn.append(n)
  s=box(x-4,y-4,97.8,8,8,3)
  s=s.fuse(box(x-2,64.2 if back else y,97.8,4,(y-64.2) if back else (18.8-y),3))
  s=hole(s,(x,y,97),(0,0,1),5); ss.append(s)
part('P27','Presilha borda Pi',ss,nn,gate='Pad isolante opcional medido; nao apertar trilhas/componentes; apoio duro em 97.8')
ss=[]; nn=[]
for y in (109.5,125.5):
 n='PresilhaMPU_'+str(len(nn)); nn.append(n); s=box(-9,y-4,62.5,8,8,3).fuse(box(-14.5,y-2,62.5,9.5,4,3)); s=hole(s,(-5,y,62),(0,0,1),5); ss.append(s)
part('P28','Presilha borda MPU',ss,nn,'Inferior',gate='Pad isolante opcional medido; conferir header real e nova extrinseca IMU')
# P29 duas reguas removiveis: permite instalar holder por cima sem flexionar.
ss=[]; nn=[]
for sg in (-1,1):
 x=sg*44; n='ReguaAA_'+('E' if sg<0 else 'D'); nn.append(n)
 s=box(-40.5 if sg<0 else 36.8,1.5,75.2,3.7,83,3)
 for y in (6,74): s=s.fuse(box(-48.5 if sg<0 else 36.8,y-4.5,75.2,11.7,9,3)); s=hole(s,(x,y,75),(0,0,1),5)
 ss.append(s)
part('P29','Regua removivel holder AA',ss,nn,'Inferior',gate='Sobrepor somente borda do holder; nao toca celulas, conferir holder real')
s=box(.5,83,64.5,3,46,3).fuse(box(48,83,64.5,4.5,46,3)).fuse(box(.5,81,64.5,52,2.2,3))
s=s.fuse(box(-7,95,64.5,10,8,3)).fuse(box(47.5,113.5,64.5,8,8,3))
for y in (87,124):
 s=s.fuse(box(1,y-2,64.5,4.5,4,3)).fuse(box(42.5,y-2,64.5,9.5,4,3))
for x,y in l_ext: s=hole(s,(x,y,64),(0,0,1),5)
part('P30','Quadro retencao bordas L298N',[s],['QuadroL298'],'Inferior',gate='Nao passa metal pelos furos PCB; verificar bordas reais; pad isolante eventual a medir')
# Ferragens e relacao univoca parafuso/inserto.
for x in (-66,66):
 for back in (False,True):
  n='Clipe'+('T' if back else 'F')+('E' if x<0 else 'D'); ax=(0,-1,0) if back else (0,1,0)
  for z in (86.5,96.5): screw('A','Clipe '+('tampa' if z>90 else 'saia'),(x,210.5 if back else -2.5,z),ax,8,n,(x,207 if back else 1,z))
for z,g in [(82,'B'),(110,'C')]:
 for sg in (-1,1): screw(g,'Lingueta lateral',(sg*85.5,118,z),(-sg,0,0),8,'SaiaFrente' if g=='B' else 'P03_Teto' if sg<0 else 'P04_Teto',(sg*81.6,118,z))
for x,n in [(-53,'UniaoTetoE'),(53,'UniaoTetoD')]:
 for y in (104,120): screw('D','Ponte teto',(x,y,137.5),(0,0,-1),8,n,(x,y,133.8))
for x in (-30,30): screw('E','Portinhola AA',(x,-4.9,78.4),(0,1,0),8,'SaiaFrente',(x,-2,78.4))
for x in (-55,55): screw('F','Portinhola PB',(x,212.9,86),(0,-1,0),8,'SaiaTras',(x,210,86))
for y in (142,199): screw('G','Painel lateral PB',(87.9,y,86.5),(-1,0,0),8,'SaiaTras',(85,y,86.5))
for x in (-61,61):
 for y in (24,190): screw('H','Piso pela orelha saia',(x,y,82),(0,0,1),10,'PisoSuperior',(x,y,87),True)
for idx,(x,y) in enumerate(frame):
 n=('P15_' if idx<2 else 'P16_')+str(idx%2); z=48.4 if idx<2 else 52.4
 screw('I','Coluna no chassi',(x,y,44.9),(0,0,1),8 if idx<2 else 12,n,(x,y,z))
 screw('I2','Piso na coluna',(x,y,90.5),(0,0,-1),8,n,(x,y,87))
for x,n in [(-25.5,'ColunaC1E'),(25.5,'ColunaC1D')]:
 screw('J','Coluna C1 no piso',(x,84,86.5),(0,0,1),8,n,(x,84,90))
 screw('J2','Base C1 na coluna',(x,84,142.8),(0,0,-1),8,n,(x,84,140),True)
for x in (-40.3,17.7):
 for y in (7.5,75.5): screw('K','Presilha Pi',(x,y,101.3),(0,0,-1),8,'PisoSuperior',(x,y,97.8))
for i,x in enumerate((-58,58)): screw('L','Gaveta PB na coluna',(x,135.2,70),(0,-1,0),8,'P16_'+str(i),(x,132,70),True)
for x,y in aa_coords:
 screw('M','Berco AA no chassi',(x,y,44.9),(0,0,1),8,'BercoAA',(x,y,48.4))
 screw('M2','Regua AA no berco',(x,y,78.7),(0,0,-1),8,'BercoAA',(x,y,75.2))
for x,y in lxy+l_ext: screw('N','Berco L298N no chassi',(x,y,44.9),(0,0,1),8,'BercoL298',(x,y,48.4))
for x,y in l_ext: screw('N2','Quadro L298N no boss externo',(x,y,68),(0,0,-1),8,'BercoL298',(x,y,64.5))
for y in (109.5,125.5):
 screw('O','Berco MPU no chassi',(-5,y,44.9),(0,0,1),8,'BercoMPU',(-5,y,48.4))
 screw('O2','Presilha MPU',(-5,y,66),(0,0,-1),8,'BercoMPU',(-5,y,62.5))
for x in (-22,22):
 screw('P','Berco ESP no piso',(x,170,86.5),(0,0,1),8,'BercoESP',(x,170,90))
 screw('P2','Quadro ESP',(x,170,113.9),(0,0,-1),8,'BercoESP',(x,170,110))
assert len(joints)==len(inserts)
for i in inserts:
 p=V(*i['entrada_mm']); a=V(*i['eixo_para_dentro']); sh=cyl(*p,2.35,5.68,i['eixo_para_dentro']).cut(cyl(*(p-a*.01),1.5,5.7,i['eixo_para_dentro']))
 put('Inserto_'+i['id'],sh,'FerragensR05',(.82,.63,.2))
D.getObject('Escopo').Aviso='R05 ensaio dimensional; C1/chassi/holder/ESP nao medidos; cupom e montagem a seco obrigatorios. Sem prova FDM/estrutural.'
D.recompute(); D.saveAs(str(OUT/'slamderson-fixacao-r05.FCStd'))
# Exportacao em orientacao individual, nao montagem nem uma mesa unica.
P=A.newDocument('PecasR05'); rows=[]
for r in parts+[{'codigo':'P25','nome':'Cupom insertos 4.2 4.3 4.4','quantidade':1,'objetos':[],'rotacao_impressao':None,'condicao':'Ensaiar termicamente e resistencia antes das demais pecas; fundo 2mm','suportes':'nao'}]:
 s=(D.getObject(r['objetos'][0]).Shape if r['objetos'] else coupon).copy()
 if r['rotacao_impressao']: axis,angle=r['rotacao_impressao']; s.rotate(V(0,0,0),V(*axis),angle)
 b=s.BoundBox; s.translate(V(-b.XMin,-b.YMin,-b.ZMin)); b=s.BoundBox
 assert b.XLength+16<=220 and b.YLength+16<=220 and b.ZLength<=250,(r['codigo'],b)
 o=P.addObject('PartDesign::Feature',r['codigo']); o.Shape=s; o.Label=r['codigo']+' '+r['nome']; o.addProperty('App::PropertyString','CodigoPeca'); o.CodigoPeca=r['codigo']; o.addProperty('App::PropertyColor','CorDoEstudo'); o.CorDoEstudo=(.5,.22,.36)
 idx=len(P.Objects)-1; o.Placement.Base=V((idx%5)*235,(idx//5)*235,0)
 verts,faces=s.tessellate(.10); path=OUT/'stl'/(r['codigo']+'.stl')
 with path.open('wb') as f:
  f.write(('Slamderson R05 mm '+r['codigo']).encode().ljust(80,b' ')); f.write(struct.pack('<I',len(faces)))
  for a,b1,c in faces:
   n=(verts[b1]-verts[a]).cross(verts[c]-verts[a]); assert n.Length>1e-12; n.normalize(); f.write(struct.pack('<12fH',*n,*verts[a],*verts[b1],*verts[c],0))
 mesh=Mesh.Mesh(str(path)); assert mesh.isSolid(),r['codigo']
 r.update({'arquivo':'stl/'+path.name,'dimensoes_impressao_mm':[b.XLength,b.YLength,b.ZLength],'triangulos':len(faces),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'volume_mm3':s.Volume}); rows.append(r)
P.recompute(); P.saveAs(str(OUT/'pecas-impressao-r05.FCStd'))
bom=Counter((j['metrica'],j['comprimento_mm'],j['cabeca']) for j in joints)
audit={'revisao':'R05','estado':'PROTOTIPO_DIMENSIONAL_NAO_LIBERADO_FABRICACAO','origem':str(SRC.relative_to(ROOT)),'sha256_origem':source_hashes[str(SRC.relative_to(ROOT))],'fontes_preservadas_sha256':source_hashes,'impressora':'Ender-3 V3 SE','volume_referencia_mm':[220,220,250],'bico_assumido_mm':.4,'camada_assumida_mm':.2,'brim_referencia_mm':5,'margem_adicional_por_borda_mm':3,'pecas':rows,'quantidade_tipos_STL':len(rows),'quantidade_total_a_imprimir':sum(r['quantidade'] for r in rows),'quantidade_tipos_montagem':len(parts),'quantidade_pecas_montagem':sum(r['quantidade'] for r in parts),'parafusos':joints,'insertos':inserts,'bom_parafusos':[{'metrica':a,'comprimento_mm':b,'cabeca':c,'quantidade':q} for (a,b,c),q in sorted(bom.items())],'arruelas_M3_0_5mm':sum(j['objeto_arruela'] is not None for j in joints),'porcas':0,'velcro':0,'cintas':0,'inserto_autor_mm':{'rosca':'M3','comprimento':5.68,'diametro_liso':4.,'diametro_dentes':4.7},'piloto_proposto_mm':4.3,'profundidade_proposta_mm':6.,'cupom_pilotos_mm':[4.2,4.3,4.4],'pi_furos_CAD_xy_mm':pi_xy,'deltas_referencias_relativos_R04_mm':{'MPU6050':[-12,-3,8],'L298N':[0,-3,4],'Reserva_Powerbank':[0,1,0]},'extrinseca_IMU':'Alterada -12X, -3Y e +8Z no referencial CAD: medir/calibrar transformacao ROS, nao aplicada em software','furos_C1_pendentes':{'quantidade_ilustrativa':4,'matriz_proposta_mm':[43,43],'bitola':'DESCONHECIDA: sem parafusos modelados no sensor; estrutura P18/P19 usa M3 separado'}, 'limitacoes':[
 'Sem impressao FDM, resistencia, carga estatica420g, termica ou montagem fisica.',
 'Chassi espessura3mm e furacao de referencia: exigir gabarito fisico antes de furar.',
 'ESP e holder nao medidos; captura condicional.',
 'C1: rosca, matriz e profundidade desconhecidas; nao montar pelos furos ilustrativos.',
 'Piloto4.3 e profundidade6 propostos, nao recomendacao de fabricante. Ensaiar cupom4.2/4.3/4.4.',
 'Presilhas Pi/MPU/L298: verificar pads/bordas/componentes e eventual isolante medido.',
 'Janela USB, cooler e cabos nao medidos. Rotacoes STL por tipo.']}
(OUT/'kit-r05.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
with (OUT/'lista-pecas.csv').open('w',newline='') as f:
 w=csv.writer(f); w.writerow(['codigo','nome','quantidade','X_mm','Y_mm','Z_mm','suportes','condicao'])
 for r in rows: w.writerow([r['codigo'],r['nome'],r['quantidade'],*[round(v,3) for v in r['dimensoes_impressao_mm']],r['suportes'],r['condicao']])
for p in SOURCE_FILES: assert hashlib.sha256(p.read_bytes()).hexdigest()==source_hashes[str(p.relative_to(ROOT))]
print(json.dumps({'status':'GERADO_PENDENTE_VALIDACAO','tipos_STL':len(rows),'pecas_montagem':audit['quantidade_pecas_montagem'],'parafusos':len(joints),'insertos':len(inserts),'bom':audit['bom_parafusos']},ensure_ascii=False))
for d in [P,Q,D]: A.closeDocument(d.Name)
