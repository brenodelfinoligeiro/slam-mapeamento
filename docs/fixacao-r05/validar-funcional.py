"""Ensaios BREP adicionais de acesso termico, retencao e congruencia de instancias."""
from pathlib import Path
import sys,json,itertools,math
sys.path.insert(0,'/usr/lib/freecad/lib')
import FreeCAD as A
import Part
R=Path(__file__).resolve().parent; K=json.loads((R/'kit-r05.json').read_text()); D=A.openDocument(str(R/'slamderson-fixacao-r05.FCStd')); V=A.Vector
errors=[]; accesses=[]; captures=[]; congr=[]
def overlap(a,b):
 x=a.BoundBox; y=b.BoundBox
 return all(min(getattr(x,hi),getattr(y,hi))-max(getattr(x,lo),getattr(y,lo))>1e-7 for lo,hi in [('XMin','XMax'),('YMin','YMax'),('ZMin','ZMax')])
def vol(a,b):
 if not overlap(a,b): return 0.
 aa=[s for s in a.Solids if overlap(s,b)]; bb=[s for s in b.Solids if overlap(s,a)]
 return Part.makeCompound(aa).common(Part.makeCompound(bb)).Volume if aa and bb else 0.
for i in K['insertos']:
 p=V(*i['entrada_mm']); a=V(*i['eixo_para_dentro']); own=D.getObject(i['objeto']).Shape
 # Ferro hipotetico: ponta livre OD7 nos primeiros15mm, haste OD10 nos20mm seguintes.
 # Somente peca propria isolada: placas, pares e tampas nao montados durante instalacao.
 tool=Part.makeCylinder(3.5,14.99,p-a*.01,-a).fuse(Part.makeCylinder(5,20,p-a*15,-a))
 vv=vol(tool,own)
 if vv>1e-4: errors.append({'tipo':'acesso_ferro_peca_isolada','inserto':i['id'],'objeto':i['objeto'],'mm3':vv})
 accesses.append({'inserto':i['id'],'livre_peca_isolada':vv<=1e-4,'ponta_OD7_15mm_haste_OD10_20mm':True})
# Captura vertical dos envelopes: primeira pose livre e pose logo alem da folga de projeto.
for n,codes,free,caught in [('RaspberryPi5',['P27'],.50,.60),('MPU6050',['P28'],.45,.60),('L298N',['P30'],.45,.60),('Reserva_ESP',['P26'],1.35,1.50)]:
 clamps=[D.getObject(o).Shape for p in K['pecas'] if p['codigo'] in codes for o in p['objetos']]
 vals=[]
 for dz in (free,caught):
  s=D.getObject(n).Shape.copy(); s.translate(V(0,0,dz)); vals.append(sum(vol(s,c) for c in clamps))
 if vals[0]>1e-4 or vals[1]<=1e-4: errors.append({'tipo':'captura_vertical','objeto':n,'volumes':vals})
 captures.append({'objeto':n,'elevacao_livre_mm':free,'elevacao_bloqueada_mm':caught,'volume_intersecao_livre_mm3':vals[0],'volume_intersecao_bloqueada_mm3':vals[1],'limite':'Nao valida pads reais nem aplica compressao aos componentes; ESP continua envelope a medir.'})
# Todas as copias de um tipo STL precisam ser a mesma forma ate rotacao/translacao rigida.
# Testar as24 rotacoes ortogonais preservando orientacao (sem espelhamento de STL).
def centered(s):
 s=s.copy(); b=s.BoundBox; s.translate(V(-(b.XMin+b.XMax)/2,-(b.YMin+b.YMax)/2,-(b.ZMin+b.ZMax)/2)); return s
rots=[]
for ax in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]:
 for ay in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]:
  x,y=V(*ax),V(*ay)
  if abs(x.dot(y))>.1: continue
  rots.append(A.Rotation(x,y,x.cross(y),'ZXY'))
for p in K['pecas']:
 if len(p['objetos'])<2: continue
 ref=centered(D.getObject(p['objetos'][0]).Shape)
 for name in p['objetos'][1:]:
  other=centered(D.getObject(name).Shape); matched=None
  for rot in rots:
   s=other.copy(); s.Placement=A.Placement(V(0,0,0),rot).multiply(s.Placement)
   if max(abs(getattr(s.BoundBox,k)-getattr(ref.BoundBox,k)) for k in ('XLength','YLength','ZLength'))>1e-5: continue
   if abs(s.Volume-ref.Volume)>1e-4: continue
   if abs(ref.Volume-vol(s,ref))<1e-3: matched=rot.Q; break
  if matched is None: errors.append({'tipo':'instancia_nao_congruente','codigo':p['codigo'],'objeto':name})
  congr.append({'codigo':p['codigo'],'referencia':p['objetos'][0],'objeto':name,'rotacao_quaternion_para_referencia':matched,'congruente':matched is not None})
result={'status':'FALHOU' if errors else 'OK','acesso_ferro':accesses,'captura_vertical':captures,'instancias_repetidas':congr,'erros':errors,'limites':['Ferramenta hipotetica, nao ferro real medido. Instalar TODOS insertos em pecas separadas antes de placas/chassi/pares.','Captura de envelope nao confirma bordas/pads livres da placa real.','Congruencia por rotacao rigida nao altera orientacao recomendada para imprimir.']}
(R/'validacao-funcional-r05.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':result['status'],'acessos_ferro':len(accesses),'capturas':captures,'congruencias':len(congr),'erros':errors},ensure_ascii=False))
assert not errors
