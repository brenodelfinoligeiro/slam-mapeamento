"""Contrato da R03: suporte compacto, folgas e abertura; não é ensaio físico."""
from pathlib import Path
import sys,json
sys.path.insert(0,'/usr/lib/freecad/lib')
import FreeCAD as App
import Part
ROOT=Path(__file__).resolve().parent
file=ROOT/'slamderson-coberto-r03.FCStd'
assert file.is_file(),'Gerar R03; a ponte larga da R02 não satisfaz esta revisão.'
D=App.openDocument(str(file))
def volume_common(a,b):
    # Caixas sem interseção interior provam volume nulo, inclusive faces de contato.
    aa=a.BoundBox; bb=b.BoundBox
    for lo,hi in [('XMin','XMax'),('YMin','YMax'),('ZMin','ZMax')]:
        if min(getattr(aa,hi),getattr(bb,hi))-max(getattr(aa,lo),getattr(bb,lo))<=1e-7:
            return 0.0
    return a.common(b).Volume
plate=D.getObject('PonteLidar').Shape
b=plate.BoundBox
assert all(abs(a-c)<1e-5 for a,c in zip((b.XLength,b.YLength,b.ZLength),(62,62,3)))
assert abs(b.ZMin-140)<1e-5
posts=[o for o in D.Objects if o.Name.startswith('ApoioPonte')]
assert len(posts)==2
for o,x in zip(sorted(posts,key=lambda o:o.Shape.BoundBox.XMin),(-21.5,21.5)):
    b=o.Shape.BoundBox
    assert abs((b.XMin+b.XMax)/2-x)<1e-5 and abs((b.YMin+b.YMax)/2-82.5)<1e-5
    assert abs(b.ZMin-90)<1e-5 and abs(b.ZMax-140)<1e-5
    # O pé deve ter contato de área positiva com a face superior do piso.
    probe=o.Shape.copy(); probe.translate(App.Vector(0,0,-.1))
    assert volume_common(probe,D.getObject('PisoSuperior').Shape)>1
shapes=[o for o in D.Objects if hasattr(o,'Shape')]
assert all(o.Shape.isValid() and not o.Shape.isNull() for o in shapes)
parts=['Saia','TampaEsquerda','TampaDireita','PortinholaAA','PortinholaPB','TampaServicoPB']
for n in parts+['PonteLidar']+[o.Name for o in posts]:
    assert len(D.getObject(n).Shape.Solids)==1,n
checks=[]
for name in parts:
    for cname in ['Reserva_Powerbank','RaspberryPi5','Reserva_ESP','L298N','MPU6050','Reserva_Holder4AA','LidarC1','BercoPB','CintaPowerbank','CintaPowerbank001']:
        b=D.getObject(cname).Shape.BoundBox
        env=Part.makeBox(b.XLength,b.YLength,b.ZLength,App.Vector(b.XMin,b.YMin,b.ZMin))
        v=volume_common(D.getObject(name).Shape,env)
        assert v<1e-5,(name,cname,v)
        checks.append([name,cname,v])
    assert volume_common(D.getObject(name).Shape,D.getObject('PisoSuperior').Shape)<1e-5
support=['PonteLidar']+[o.Name for o in posts]+[o.Name for o in D.Objects if o.Name.startswith('EspacadorC')]
for s in support:
    for other in parts+['RaspberryPi5','Reserva_ESP','LidarC1']:
        assert volume_common(D.getObject(s).Shape,D.getObject(other).Shape)<1e-5,(s,other)
for name,sign in [('TampaEsquerda',-1),('TampaDireita',1)]:
    for dx in (0,5,15,40,80,110):
        q=D.getObject(name).Shape.copy(); q.translate(App.Vector(sign*dx,0,0))
        for n in support:
            assert volume_common(q,D.getObject(n).Shape)<1e-5,(name,dx,n)
for wheel in ('Mecanica_00','Mecanica_01'):
    b=D.getObject(wheel).Mesh.BoundBox
    keep=Part.makeCylinder(39.5,200,App.Vector(-100,(b.YMin+b.YMax)/2,(b.ZMin+b.ZMax)/2),App.Vector(1,0,0))
    for n in parts: assert volume_common(D.getObject(n).Shape,keep)<1e-5,(wheel,n)
for component,door,sign in [('Reserva_Powerbank','PortinholaPB',1),('Reserva_Holder4AA','PortinholaAA',-1)]:
    for dy in (0,10,30,70,90):
        q=D.getObject(component).Shape.copy(); q.translate(App.Vector(0,sign*dy,0))
        for n in parts:
            if n!=door: assert volume_common(q,D.getObject(n).Shape)<1e-5,(component,dy,n)
pb=D.getObject('Reserva_Powerbank').Shape.BoundBox
assert all(abs(a-c)<1e-5 for a,c in zip((pb.XLength,pb.YLength,pb.ZLength,pb.ZMin),(150,70,30,50.8)))
assert abs(D.getObject('LidarC1').Shape.BoundBox.ZMin-145)<1e-5
assert max(D.getObject(n).Shape.BoundBox.ZMax for n in parts)==137
result={'status':'OK','arquivo_reaberto':True,'objetos':len(D.Objects),'base_compacta_mm':[62,62,3],'largura_anterior_mm':130,'reducao_largura_percentual':100*(130-62)/130,'colunas_xy_mm':[[-21.5,82.5],[21.5,82.5]],'contato_colunas_piso':True,'testes_carcaca_envelopes':len(checks),'retirada_lateral_amostrada_mm':[0,5,15,40,80,110],'altura_base_C1_mm':145,'altura_teto_mm':137,'limites':'Amostras discretas; não prova movimento contínuo. Sem ensaio de furação real, cabos, rigidez, vibração, térmica ou varredura óptica.'}
(ROOT/'validacao-r03.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False))
App.closeDocument(D.Name)
