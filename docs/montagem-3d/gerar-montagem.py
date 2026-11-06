"""Estudo 3D local: geometria de referência + reservas explicitamente marcadas.
Não executa scripts ou macros de terceiros. Não produz peças para fabricação.
"""
from pathlib import Path
import sys, json, zipfile, io, hashlib
sys.path.insert(0, '/usr/lib/freecad/lib')
import FreeCAD as App
import Part
import Mesh

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
CACHE=Path('/home/lamggm/.hermes/cache/scratch/slamderson-3d'); CACHE.mkdir(parents=True,exist_ok=True)
MODELS=ROOT/'docs/modelos-3d'
layout=json.loads((ROOT/'docs/disposicao-2d/implantacao.json').read_text())
manifest=json.loads((MODELS/'manifesto.json').read_text())
lookup={x['id']:x for x in manifest['modelos']}
doc=App.newDocument('Slamderson3D')
groups={}
for name,label in [('Mecanica','01 Chassi, rodas e motores — referência'),('Inferior','02 Piso inferior — quatro AA e controle'),('Superior','03 Piso superior — Pi e powerbank'),('Lidar','04 Ponte e corpo C1')]:
    g=doc.addObject('App::DocumentObjectGroup',name); g.Label=label; groups[name]=g
records=[]

def box(x,y,z,w,l,h): return Part.makeBox(w,l,h,App.Vector(x,y,z))
def cyl(x,y,z,r,h): return Part.makeCylinder(r,h,App.Vector(x,y,z))
def add(name,label,shape,color,group,kind='proposta',source=None,transparency=0):
    obj=doc.addObject('PartDesign::Feature',name); obj.Label=label; obj.Shape=shape
    obj.addProperty('App::PropertyString','Evidencia').Evidencia=kind
    obj.addProperty('App::PropertyColor','CorDoEstudo').CorDoEstudo=color
    obj.addProperty('App::PropertyInteger','TransparenciaEstudo').TransparenciaEstudo=transparency
    groups[group].addObject(obj)
    if source: obj.addProperty('App::PropertyString','Origem').Origem=source
    records.append({'objeto':obj.Name,'rotulo':label,'tipo':kind,'grupo':group,'origem':source})
    return obj

def load(model_id):
    m=lookup[model_id]; p=MODELS/m['caminho']
    assert hashlib.sha256(p.read_bytes()).hexdigest()==m['sha256']
    if p.suffix=='.zip':
        with zipfile.ZipFile(p) as z:
            name=next(n for n in z.namelist() if n.lower().endswith(('.step','.stp')))
            target=CACHE/(model_id+'.step')
            raw=z.read(name)
            if not target.exists() or hashlib.sha256(target.read_bytes()).digest()!=hashlib.sha256(raw).digest(): target.write_bytes(raw)
            p=target
    s=Part.Shape(); s.read(str(p)); assert not s.isNull()
    return s

def positioned(shape,x,y,z,rotation=None):
    s=shape.copy()
    if rotation: s.rotate(App.Vector(),rotation[0],rotation[1])
    b=s.BoundBox; s.translate(App.Vector(x-b.XMin,y-b.YMin,z-b.ZMin)); return s

# Geometria da montagem mecânica original, preservada, separada em componentes conexos.
source=MODELS/lookup['chassi_2wd_4738179_montagem']['caminho']
assert hashlib.sha256(source.read_bytes()).hexdigest()==lookup['chassi_2wd_4738179_montagem']['sha256']
with zipfile.ZipFile(source) as z:
    with zipfile.ZipFile(io.BytesIO(z.read('files/2wd_robot.zip'))) as inner:
        n=next(n for n in inner.namelist() if n.endswith('2wd_robot.stl'))
        raw=inner.read(n)
stl=CACHE/'montagem-original.stl'
if not stl.exists() or hashlib.sha256(stl.read_bytes()).digest()!=hashlib.sha256(raw).digest(): stl.write_bytes(raw)
mechanical=Mesh.Mesh(str(stl)); pieces=mechanical.getSeparateComponents()
assert len(pieces)==36 and mechanical.CountFacets==684152
shift=App.Vector(1.86686325073242,120.28302764892578,-0.01814041137695)
for i,m in enumerate(pieces):
    if i in (0,1): label='Pneu de referência'; col=(.12,.15,.18)
    elif i in (2,3): label='Cubo de roda de referência'; col=(.89,.68,.15)
    elif i==4: label='Chapa do chassi B'; col=(.59,.68,.72)
    elif i in (5,6,7): label='Rodízio de referência'; col=(.45,.49,.53)
    elif i in (8,9): label='Motor — tampa de referência'; col=(.22,.24,.27)
    elif i in (10,11,16,17): label='Motorredutor TT de referência'; col=(.93,.71,.12)
    else: label='Fixação/eixo da montagem de referência'; col=(.58,.61,.65)
    obj=doc.addObject('Mesh::Feature',f'Mecanica_{i:02d}'); obj.Label=f'{i:02d} {label}'
    obj.Mesh=m; obj.Placement.Base=shift
    obj.addProperty('App::PropertyColor','CorDoEstudo').CorDoEstudo=col
    obj.addProperty('App::PropertyInteger','TransparenciaEstudo').TransparenciaEstudo=35 if i==4 else 0
    obj.addProperty('App::PropertyString','Evidencia').Evidencia='Malha de referência do pacote 4738179; não medição física.'
    groups['Mecanica'].addObject(obj)
    records.append({'objeto':obj.Name,'rotulo':obj.Label,'tipo':'malha_referencia','grupo':'Mecanica','facetas':m.CountFacets})

# Porta-pilhas genérico, quatro AA ilustrativas; nenhuma marca/revisão escolhida.
outer=box(-37.5,10,50.4,75,70,22)
inner=box(-35.5,12,52.4,71,66,23)
holder=outer.cut(inner)
add('Reserva_Holder4AA','01 RESERVA — holder 4 AA',holder,(.34,.27,.15),'Inferior','reserva: holder não escolhido')
for i,y in enumerate((19,35,51,67)):
    s=Part.makeCylinder(7.1,50.5,App.Vector(-25.25,y,60),App.Vector(1,0,0))
    add(f'AA_{i+1}',f'01 AA {i+1} — ilustrativa',s,(.82,.59,.19),'Inferior','representação ilustrativa de AA, não ficha dimensional')
    x=25.25 if i%2==0 else -26.35
    cap=Part.makeCylinder(2.6,1.1,App.Vector(x,y,60),App.Vector(1,0,0))
    add(f'PoloAA_{i+1}',f'Polo AA {i+1} — ilustrativo',cap,(.8,.82,.84),'Inferior')

# Reserva do ESP elevada 6 mm em relação ao 2D: libera os suportes reais do motor.
esp=add('Reserva_ESP','02 RESERVA — placa ESP a definir',box(-45,101,56.4,28,55,15),(.14,.43,.68),'Inferior','reserva: placa final não escolhida',transparency=45)
imu=add('MPU6050','03 MPU-6050 — CAD candidato',positioned(load('mpu6050'),5,153,50.4),(.1,.55,.55),'Inferior','CAD de referência, furação/orientação a conferir',lookup['mpu6050']['caminho'])
driver=add('L298N','04 L298N — CAD de referência',positioned(load('l298n_step'),3,94,56.4),(.65,.2,.17),'Inferior','CAD de referência; elevado 6 mm para liberar suportes do motor',lookup['l298n_step']['caminho'])

# Garfos CAD ao lado interno dos motores; discos ilustrativos, sem calibração de alinhamento.
encoder=load('sensor_extraido')
axle_y=(-77.05526733398438-8.192363739013672)/2+shift.y
axle_z=(.47281599044799805+69.39561462402344)/2+shift.z
for side,x in [('E',-23.8),('D',9.5)]:
    rot=90 if side=='E' else -90
    add('Encoder_'+side,'05 Encoder '+side+' — posição a alinhar',positioned(encoder,x,axle_y-17.725,25,(App.Vector(0,0,1),rot)),(.1,.25,.46),'Inferior','CAD do sensor confirmado visualmente; posição/garfo a conferir',lookup['sensor_extraido']['caminho'])
    plane=-24.5 if side=='E' else 23.5
    disk=Part.makeCylinder(10,1,App.Vector(plane,axle_y,axle_z),App.Vector(1,0,0))
    disk=disk.cut(Part.makeCylinder(2,3,App.Vector(plane-1,axle_y,axle_z),App.Vector(1,0,0)))
    # Fendas meramente ilustrativas; não assumir resolução de encoder.
    for j in range(12):
        cut=box(plane-1,axle_y+5,axle_z-1.1,3,6,2.2)
        cut.rotate(App.Vector(plane,axle_y,axle_z),App.Vector(1,0,0),j*30)
        disk=disk.cut(cut)
    add('Disco_'+side,'05 Disco '+side+' — ILUSTRATIVO, fendas não medidas',disk,(.08,.09,.1),'Inferior','geometria ilustrativa; número de fendas sem valor de resolução real')

pink=(.74,.22,.45)
# Colunas propostas: dimensões para estudo, não peças aprovadas para impressão.
for x in (-43,43):
    for y in (20,199):
        s=cyl(x,y,48.4,3.8,35.6).cut(cyl(x,y,47.4,1.6,37.6))
        add('ColunaPrincipal',f'09 Coluna principal x={x} y={y}',s,pink,'Superior')
floor=box(-65,8,84,130,197,3).cut(box(0,90,83,50,56,5))
add('PisoSuperior','10 Piso removível — janela sobre L298N',floor,pink,'Superior',transparency=25)
# Pequenos apoios ilustrativos dos módulos/volumes não representam furação real.
for prefix,coords,z,h in [('ESP',[(-41,106),(-21,151)],48.4,8),('L298N',[(7,98),(42,133)],48.4,8),('Pi',[(-35,20),(35,20),(-35,62),(35,62)],87,4),('PB',[(-48,148),(48,148),(-48,198),(48,198)],87,4)]:
    for x,y in coords:
        add('Apoio_'+prefix,'Apoio proposto '+prefix,cyl(x,y,z,2.5,h),pink,'Inferior' if prefix in ('ESP','L298N') else 'Superior')

# Pi oficial: geometria completa, sem redimensionamento e com translação apenas.
pi=add('RaspberryPi5','06 Raspberry Pi 5 — CAD oficial',positioned(load('raspberry_pi_5'),-44.25,12,91),(.16,.45,.26),'Superior','CAD oficial; revisão física, cooler e cabos a conferir',lookup['raspberry_pi_5']['caminho'])
powerbank=box(-60,140,91,120,65,25)
try: powerbank=powerbank.makeFillet(4,powerbank.Edges)
except Part.OCCError: pass
add('Reserva_Powerbank','07 RESERVA — powerbank 120x65x25',powerbank,(.2,.28,.39),'Superior','reserva: powerbank exato desconhecido')
for y in (153,191):
    strap=box(-61,y,116.2,122,6,.8)
    add('CintaPowerbank','Cinta removível — representação',strap,(.09,.11,.14),'Superior')

for x in (-58,58):
    post=cyl(x,80,87,3.8,48).cut(cyl(x,80,86,1.6,50))
    add('ApoioPonte','11 Apoio elevado do C1',post,pink,'Lidar')
bridge=box(-65,71,135,130,66,3)
# Vazios aliviam a visualização e o peso proposto, sem validar resistência.
for x in (-51,37): bridge=bridge.cut(box(x,95,134,14,31,5))
add('PonteLidar','12 Ponte C1 — proposta',bridge,pink,'Lidar')
for x in (-21.5,21.5):
    for y in (82.5,125.5): add('EspacadorC1','Apoio C1 proposto',cyl(x,y,138,2.4,2),pink,'Lidar')
c1_full=load('lidar_c1')
selected=[]; selected_indices=[]
for i,s in enumerate(c1_full.Solids):
    b=s.BoundBox
    if b.XMin>=-28 and b.XMax<=28 and b.YMin>=-28 and b.YMax<=28:
        selected.append(s); selected_indices.append(i)
assert len(selected)==15
c1=Part.makeCompound(selected); c1=positioned(c1,-c1.BoundBox.XLength/2,104-c1.BoundBox.YLength/2,140)
add('LidarC1','08 LiDAR C1 — corpo extraído do CAD',c1,(.15,.17,.2),'Lidar','derivação: corpo sem cabo/acessórios externos',lookup['lidar_c1']['caminho'])

note=doc.addObject('App::FeaturePython','Escopo')
note.addProperty('App::PropertyString','Aviso').Aviso='Estudo mecânico. Reservas de holder/ESP/powerbank. Suportes, discos e furação não são aprovados para fabricação. Quatro AA não comprovam alimentação de motores 12 V.'
note.addProperty('App::PropertyString','AlteracaoDo2D').AlteracaoDo2D='ESP e L298N elevados 6 mm para liberar suportes dos motores do CAD original; rodas/eixos preservados no CAD de origem.'
doc.recompute()
# Validar os BREP, manter malhas como malhas (não fingir volume sólido).
invalid=[]; solid_count=0
for o in doc.Objects:
    if hasattr(o,'Shape'):
        if o.Shape.isNull() or not o.Shape.isValid(): invalid.append(o.Name)
        solid_count+=len(o.Shape.Solids)
assert not invalid,invalid
path=OUT/'slamderson-estudo-3d.FCStd'
doc.saveAs(str(path)); expected=len(doc.Objects); App.closeDocument(doc.Name)
reopened=App.openDocument(str(path)); assert len(reopened.Objects)==expected
for r in records:
    o=reopened.getObject(r['objeto'])
    if hasattr(o,'Shape'): assert not o.Shape.isNull() and o.Shape.isValid()
    else: assert o.Mesh.CountFacets==r['facetas']
audit={'natureza':'estudo_3D_de_referencias_e_reservas_nao_fabricacao','origem_layout_2d':'docs/disposicao-2d/implantacao.json','AA':4,'FreeCAD':'.'.join(App.Version()[:3]),'objetos':expected,'solidos_BREP':solid_count,'malhas_referencia':len(pieces),'facetas_mecanica':mechanical.CountFacets,'objetos_invalidos':invalid,'reaberto_no_kernel':True,'objetos_componentes':records,'C1_indices_selecionados':selected_indices,'C1_acessorios_omitidos':[i for i in range(22) if i not in selected_indices],'diferencas_do_2d':['ESP e L298N elevados em 6 mm, base do envelope em z=56,4 mm.','Rodas/eixos/rodízio mantêm geometria e posições relativas do CAD mecânico original, não os círculos simplificados do 2D.','Corpo C1 real ocupa cerca de 55,86 x 55,86 x 41,45 mm; não foi redimensionado para o círculo nominal 2D.'],'limites':['Malhas de terceiros não são sólidos BREP validados.','Não há ensaio físico, cálculo de estabilidade ou verificação completa de colisões.','Encoders/discos, fixações, cabos, cooler e retenção das pilhas exigem conferência.','Suportes e placeholders não estão aprovados para fabricação.'],'fontes':{k:{'caminho':lookup[k]['caminho'],'sha256':lookup[k]['sha256']} for k in ['chassi_2wd_4738179_montagem','raspberry_pi_5','l298n_step','mpu6050','sensor_extraido','lidar_c1']}}
(OUT/'validacao-3d.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:audit[k] for k in ['objetos','solidos_BREP','malhas_referencia','facetas_mecanica','objetos_invalidos']},ensure_ascii=False))
