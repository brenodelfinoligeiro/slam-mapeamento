"""Contrato geométrico conservador do estudo R02; não é ensaio físico."""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parent
file=ROOT/'slamderson-coberto-r02.FCStd'
assert file.is_file(), 'Falta gerar a revisão R02 com o powerbank real e a carcaça.'
sys.path.insert(0,'/usr/lib/freecad/lib')
import FreeCAD as App
import Part
D=App.openDocument(str(file))
P=D.getObject('Reserva_Powerbank'); b=P.Shape.BoundBox
assert all(abs(a-c)<1e-5 for a,c in zip((b.XLength,b.YLength,b.ZLength),(150,70,30)))
assert abs(b.ZMin-50.8)<1e-5 and abs(P.MassaIndicada_g-420)<1e-5
parts=['Saia','TampaEsquerda','TampaDireita','PortinholaAA','PortinholaPB','TampaServicoPB']
for name in parts:
    s=D.getObject(name).Shape
    assert s.isValid() and len(s.Solids)==1 and s.Volume>0,name
checks=[]
# Caixas dos componentes: verificação conservadora, não colisão de cabos/fios.
for name in parts:
    for cname in ['Reserva_Powerbank','RaspberryPi5','Reserva_ESP','L298N','MPU6050','Reserva_Holder4AA','LidarC1','BercoPB','CintaPowerbank','CintaPowerbank001']:
        b=D.getObject(cname).Shape.BoundBox
        envelope=Part.makeBox(b.XLength,b.YLength,b.ZLength,App.Vector(b.XMin,b.YMin,b.ZMin))
        volume=D.getObject(name).Shape.common(envelope).Volume
        assert volume<1e-5,(name,cname,volume)
        checks.append({'carcaca':name,'componente':cname,'volume_intersecao_mm3':volume})
for name in parts:
    assert D.getObject(name).Shape.common(D.getObject('PisoSuperior').Shape).Volume<1e-5,(name,'PisoSuperior')
# Folga radial dos pneus; não representa deformação de pneu ou obstáculos.
for wheel in ('Mecanica_00','Mecanica_01'):
    b=D.getObject(wheel).Mesh.BoundBox
    y=(b.YMin+b.YMax)/2; z=(b.ZMin+b.ZMax)/2
    keepout=Part.makeCylinder(39.5,200,App.Vector(-100,y,z),App.Vector(1,0,0))
    for name in parts:
        vol=D.getObject(name).Shape.common(keepout).Volume
        assert vol<1e-5,(name,wheel,vol)
# Caminho nominal de retirada das tampas, lateral e abaixo da ponte do C1.
for name,sign in [('TampaEsquerda',-1),('TampaDireita',1)]:
    moved=D.getObject(name).Shape.copy()
    for dx in (0,15,40,80,110):
        q=moved.copy(); q.translate(App.Vector(sign*dx,0,0))
        for post in ('ApoioPonte','ApoioPonte001'):
            assert q.common(D.getObject(post).Shape).Volume<1e-5,(name,dx,post)
assert max(D.getObject(n).Shape.BoundBox.ZMax for n in parts)<D.getObject('LidarC1').Shape.BoundBox.ZMin
service=[]
for component,door,sign in [('Reserva_Powerbank','PortinholaPB',1),('Reserva_Holder4AA','PortinholaAA',-1)]:
    for delta in (0,10,30,70,90):
        q=D.getObject(component).Shape.copy(); q.translate(App.Vector(0,sign*delta,0))
        for shell in parts:
            if shell!=door:
                assert q.common(D.getObject(shell).Shape).Volume<1e-5,(component,delta,shell)
        service.append({'componente':component,'deslocamento_y_mm':sign*delta})
result={'arquivo_reaberto':True,'powerbank_mm':[b for b in (P.Shape.BoundBox.XLength,P.Shape.BoundBox.YLength,P.Shape.BoundBox.ZLength)],'PB_base_z_mm':P.Shape.BoundBox.ZMin,'pecas_principais_validas':len(parts),'testes_carcaca_envelopes':checks,'folga_radial_modelada_mm':5,'retirada_lateral_amostrada_mm':[0,15,40,80,110],'limites':'Não valida cabos, massa total, resistência, temperatura, tolerâncias físicas ou montagem real.'}
result['retirada_baterias_amostrada']=service
(ROOT/'validacao-r02.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':'OK','pecas_principais':len(parts),'testes_envelopes':len(checks),'PB_z':P.Shape.BoundBox.ZMin}))
App.closeDocument(D.Name)
