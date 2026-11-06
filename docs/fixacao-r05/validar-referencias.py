"""Folgas conservadoras contra rodas/cubos e caixas dos demais meshes de referencia."""
from pathlib import Path
import sys,json
sys.path.insert(0,'/usr/lib/freecad/lib')
import FreeCAD as A
import Part
R=Path(__file__).resolve().parent; K=json.loads((R/'kit-r05.json').read_text()); D=A.openDocument(str(R/'slamderson-fixacao-r05.FCStd')); V=A.Vector
printed=[D.getObject(n) for p in K['pecas'] for n in p['objetos']]; errors=[]; checks=0
for o in D.Objects:
 if not hasattr(o,'Mesh'): continue
 b=o.Mesh.BoundBox
 if o.Name in ['Mecanica_00','Mecanica_01','Mecanica_02','Mecanica_03']:
  # Cilindro macico circunscrito a roda/cubo: conservador, nao reproduz pneu oco.
  ref=Part.makeCylinder(max(b.YLength,b.ZLength)/2,b.XLength,V(b.XMin,(b.YMin+b.YMax)/2,(b.ZMin+b.ZMax)/2),V(1,0,0))
 else: ref=Part.makeBox(max(b.XLength,1e-5),max(b.YLength,1e-5),max(b.ZLength,1e-5),V(b.XMin,b.YMin,b.ZMin))
 for p in printed:
  checks+=1; pb=p.Shape.BoundBox
  if not all(min(getattr(pb,hi),getattr(ref.BoundBox,hi))-max(getattr(pb,lo),getattr(ref.BoundBox,lo))>1e-7 for lo,hi in [('XMin','XMax'),('YMin','YMax'),('ZMin','ZMax')]): continue
  vv=p.Shape.common(ref).Volume
  if vv>2e-4: errors.append({'a':p.Name,'referencia':o.Name,'rotulo':o.Label,'mm3':vv})
result={'status':'FALHOU' if errors else 'OK','pares_pecas_x_referencias':checks,'erros':errors,'limite':'Caixas/cilindros conservadores de CAD candidato; nao medicao real. Parafusos no chassi nao auditados aqui: chassi exige gabarito de furacao.'}
(R/'validacao-referencias-r05.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n'); print(json.dumps(result,ensure_ascii=False)); assert not errors
