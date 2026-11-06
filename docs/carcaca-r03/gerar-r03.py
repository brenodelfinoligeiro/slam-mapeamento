"""R03: suporte C1 compacto; preserva a R02 e os CADs dos componentes."""
from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,'/usr/lib/freecad/lib')
import FreeCAD as App
import Part
import Mesh
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
SOURCE=ROOT/'docs/carcaca-r02/slamderson-coberto-r02.FCStd'
source_hash=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
D=App.openDocument(str(SOURCE))
assert len(D.Objects)==110

def box(x,y,z,w,l,h): return Part.makeBox(w,l,h,App.Vector(x,y,z))
def cyl(x,y,z,r,h): return Part.makeCylinder(r,h,App.Vector(x,y,z))
def rb(x,y,z,w,l,h,r):
    s=box(x,y,z,w,l,h)
    edges=[e for e in s.Edges if abs(e.BoundBox.ZLength-h)<1e-5 and e.BoundBox.XLength<1e-5 and e.BoundBox.YLength<1e-5]
    assert len(edges)==4
    return s.makeFillet(r,edges)
def setshape(o,s):
    o.Placement=App.Placement(); o.Shape=s
    return o

# Geometria C1 e altura preservadas; apenas a plataforma e seus dois apoios mudam.
original_C1=D.getObject('LidarC1').Shape.hashCode()
compact=(.12,.17,.21)
for o,x in zip(sorted([o for o in D.Objects if o.Name.startswith('ApoioPonte')],key=lambda o:o.Shape.BoundBox.XMin),(-21.5,21.5)):
    setshape(o,cyl(x,82.5,90,3.8,50).cut(cyl(x,82.5,89,1.6,52)))
    o.Label='Apoio interno compacto C1 — proposta'; o.CorDoEstudo=compact
plate=rb(-31,73,140,62,62,3,8)
# Furação de estudo na mesma matriz dos espaçadores da R02; conferir no C1 real.
for x in (-21.5,21.5):
    for y in (82.5,125.5): plate=plate.cut(cyl(x,y,139,1.6,5))
plate=plate.cut(box(-5,108,139,10,8,5)).removeSplitter()
o=setshape(D.getObject('PonteLidar'),plate)
o.Label='Base compacta C1 — 62 x 62 x 3 mm, proposta'; o.CorDoEstudo=compact
o.Evidencia='Suporte reduzido a pedido do autor; furos e rigidez ainda não validados fisicamente.'
for o in [o for o in D.Objects if o.Name.startswith('EspacadorC')]:
    b=o.Shape.BoundBox; x=(b.XMin+b.XMax)/2; y=(b.YMin+b.YMax)/2
    setshape(o,o.Shape.cut(cyl(x,y,142,1.6,4))); o.CorDoEstudo=compact

# Reconstruir só as duas tampas: remover o rasgo de 126 mm da ponte antiga.
# Rasgo de 54 x 11 mm para os dois postes internos; totalmente sob a nova base.
cap=rb(-85,-2,90.6,170,212,46.4,12).cut(rb(-82,1,89,164,206,45,9))
cap=cap.cut(box(-27,77,133,54,11,6)).cut(box(-6,108,133,12,8,6))
for x in range(-46,47,7): cap=cap.cut(box(x,17,133,3,45,6))
for x in (-86,81):
    for y in (20,28,36,44,52): cap=cap.cut(box(x,y,119,5,3,9))
cap=cap.cut(box(-6,-3,95,12,5,8)).cut(box(-6,206,97,12,5,8))
for x in (-74,62):
    for y,length in ((0,8),(198,10)): cap=cap.fuse(box(x,y,90.6,12,length,5.4))
for x in (-68,68):
    for y in (4,202): cap=cap.cut(cyl(x,y,89,1.7,9))
setshape(D.getObject('TampaEsquerda'),cap.common(box(-200,-100,0,199.7,500,500)).removeSplitter())
setshape(D.getObject('TampaDireita'),cap.common(box(.3,-100,0,200,500,500)).removeSplitter())
D.getObject('Escopo').Aviso='R03: suporte compacto C1 62x62x3 mm, colunas internas; Basike e carcaça da R02 preservados. Furação, cabos, rigidez, vibração e temperatura pendentes de ensaio.'
assert D.getObject('LidarC1').Shape.hashCode()==original_C1
D.recompute()
assert all(o.Shape.isValid() for o in D.Objects if hasattr(o,'Shape'))
D.saveAs(str(OUT/'slamderson-coberto-r03.FCStd'))
# Documento leve das peças do suporte, ainda para avaliação e não fabricação final.
C=App.newDocument('SuporteCompactoR03')
names=['PonteLidar']+[o.Name for o in D.Objects if o.Name.startswith(('ApoioPonte','EspacadorC'))]
for name in names:
    o=C.addObject('PartDesign::Feature',name); o.Label=D.getObject(name).Label; o.Shape=D.getObject(name).Shape.copy()
C.recompute(); C.saveAs(str(OUT/'suporte-c1-estudo-r03.FCStd'))
Part.makeCompound([o.Shape for o in C.Objects]).exportStep(str(OUT/'suporte-c1-estudo-r03.step'))
audit={'revisao':'R03','arquivo_origem':str(SOURCE.relative_to(ROOT)),'sha256_origem':source_hash,'objetos_montagem':len(D.Objects),'largura_anterior_mm':130,'base_compacta_mm':[62,62,3],'reducao_largura_percentual':100*(130-62)/130,'colunas_xy_mm':[[-21.5,82.5],[21.5,82.5]],'suporte_z_mm':[90,145],'base_C1_z_mm':145,'cota_teto_mm':137,'rasgo_tampa_postes_mm':[54,11],'cor_suporte':'carvao, para integrar ao sensor','componentes_preservados':['LidarC1','RaspberryPi5','Reserva_Powerbank','Reserva_ESP','L298N','MPU6050','Reserva_Holder4AA'],'limites':['Furos na matriz proposta da R02, sem comprovar furação do sensor físico.','Sem prova estrutural, de vibração, passagem real de cabo ou térmica.','A retirada das tampas é testada por amostras; não representa ensaio de montagem.']}
(OUT/'parametros-r03.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==source_hash
print(json.dumps(audit,ensure_ascii=False))
App.closeDocument(C.Name); App.closeDocument(D.Name)
