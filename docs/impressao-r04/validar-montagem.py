"""Audita o FCStd R04 reaberto; colisões BREP, caminhos amostrados e fixadores."""
from pathlib import Path
import sys,json,itertools,hashlib,time
sys.path.insert(0,'/usr/lib/freecad/lib')
import FreeCAD as A
import Part
R=Path(__file__).resolve().parent; K=json.loads((R/'kit-r04.json').read_text()); D=A.openDocument(str(R/'slamderson-impressao-r04.FCStd'))
V=A.Vector

def overlap(a,b):
 x=a.BoundBox; y=b.BoundBox
 return all(min(getattr(x,hi),getattr(y,hi))-max(getattr(x,lo),getattr(y,lo))>1e-7 for lo,hi in [('XMin','XMax'),('YMin','YMax'),('ZMin','ZMax')])
def vol(a,b):
 if not overlap(a,b): return 0.
 # Selecionar sólidos por caixa antes de chamar booleanas do CAD complexo da Pi.
 aa=[s for s in a.Solids if overlap(s,b)]; bb=[s for s in b.Solids if overlap(s,a)]
 if not aa or not bb: return 0.
 return Part.makeCompound(aa).common(Part.makeCompound(bb)).Volume
printed=[D.getObject(n) for p in K['pecas'] for n in p['objetos']]
assert len(printed)==K['quantidade_total_a_imprimir']-1
assert all(o.Shape.isValid() and len(o.Shape.Solids)==1 for o in printed)
errors=[]; pair_checks=0; component_checks=0
for a,b in itertools.combinations(printed,2):
 vv=vol(a.Shape,b.Shape); pair_checks+=1
 if vv>1e-4: errors.append({'tipo':'pecas','a':a.Name,'b':b.Name,'mm3':vv})
components=['RaspberryPi5','L298N','MPU6050','Reserva_ESP','Reserva_Powerbank','Reserva_Holder4AA','LidarC1']
for a in printed:
 for n in components:
  vv=vol(a.Shape,D.getObject(n).Shape); component_checks+=1
  if vv>1e-4: errors.append({'tipo':'componente','a':a.Name,'b':n,'mm3':vv})
# Todos os parafusos devem atravessar os próprios furos sem cortar plástico.
bolt_checks=0
for j in K['parafusos']:
 s=D.getObject(j['objeto_parafuso']).Shape
 for a in printed:
  vv=vol(s,a.Shape); bolt_checks+=1
  if vv>2e-4: errors.append({'tipo':'parafuso_plastico','grupo':j['grupo'],'a':j['objeto_parafuso'],'b':a.Name,'mm3':vv})
# Porcas/arruelas não podem atravessar paredes ou berços.
hw_checks=0
for o in D.Objects:
 if not o.Name.startswith(('Porca_','Arruela')): continue
 for a in printed:
  vv=vol(o.Shape,a.Shape); hw_checks+=1
  if vv>2e-4: errors.append({'tipo':'porca_arruela','a':o.Name,'b':a.Name,'mm3':vv})
# Apoios Pi de 6 mm alinhados com cilindros reais r=1.35 no CAD oficial.
pi=D.getObject('RaspberryPi5').Shape
circles={(round(f.Surface.Center.x,4),round(f.Surface.Center.y,4)) for f in pi.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-1.35)<1e-5 and abs(f.Surface.Axis.z)>.99}
assert all(any(abs(x-cx)<1e-4 and abs(y-cy)<1e-4 for cx,cy in circles) for x,y in K['pi_furos_CAD_xy_mm'])
# Comprimento efetivo: projeção sobre o eixo deve cobrir a espessura toda da porca.
threads=[]
for j in K['parafusos']:
 c=V(*j['posicao_cabeca_mm']); a=V(*j['eixo_para_dentro']); p,axis=j['porca']; p=V(*p); ax=V(*axis); th=2.4 if j['metrica']=='M3' else 2
 near=min((p-c).dot(a),(p+ax*th-c).dot(a)); far=max((p-c).dot(a),(p+ax*th-c).dot(a)); protr=j['comprimento_mm']-far
 assert near>=0 and protr>=.35,(j['grupo'],protr)
 threads.append({'grupo':j['grupo'],'projecao_apos_porca_mm':round(protr,3)})
# Caminho lateral: cada conjunto de dois quartos desloca sem a ferragem A superior.
paths=0
support=[D.getObject(n) for p in K['pecas'] if p['codigo'] in ['P18','P19','P20'] for n in p['objetos']]
for codes,sg in [(['P03','P05'],-1),(['P04','P06'],1)]:
 for p in K['pecas']:
  if p['codigo'] not in codes: continue
  for dx in (0,5,15,40,80,110):
   s=D.getObject(p['objetos'][0]).Shape.copy(); s.translate(V(sg*dx,0,0))
   for t in support:
    vv=vol(s,t.Shape); paths+=1
    if vv>1e-4: errors.append({'tipo':'retirada_tampa','a':p['codigo'],'dx':dx,'b':t.Name,'mm3':vv})
# Rodas: folga conservadora modelada, não deformação ou espaço para obstáculos.
wheel_checks=0
for wheel in ['Mecanica_00','Mecanica_01']:
 b=D.getObject(wheel).Mesh.BoundBox; keep=Part.makeCylinder(39.5,200,V(-100,(b.YMin+b.YMax)/2,(b.ZMin+b.ZMax)/2),V(1,0,0))
 for p in K['pecas']:
  if p['codigo'] not in ['P01','P02','P03','P04','P05','P06']: continue
  vv=vol(D.getObject(p['objetos'][0]).Shape,keep); wheel_checks+=1
  if vv>1e-4: errors.append({'tipo':'roda','a':p['codigo'],'b':wheel,'mm3':vv})
source=R.parents[1]/K['origem']; assert hashlib.sha256(source.read_bytes()).hexdigest()==K['sha256_origem']
result={'status':'FALHOU' if errors else 'OK','pares_pecas':pair_checks,'pares_componentes':component_checks,'parafuso_plastico':bolt_checks,'porca_arruela_plastico':hw_checks,'pi_alinhada_no_CAD':True,'extremidades_rosca':threads,'amostras_retirada_tampa':paths,'folga_roda':wheel_checks,'erros':errors,'limites':'Sem hardware real. Não verifica rosca real C1, furação real do chassi/ESP/holder, cabos, tolerâncias reais, esforço ou térmica.'}
(R/'validacao-montagem-r04.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['extremidades_rosca']},ensure_ascii=False))
A.closeDocument(D.Name)
assert not errors,'Interferências acima devem ser resolvidas; não liberar STL com ressalva genérica.'
