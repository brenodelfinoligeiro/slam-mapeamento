"""Consolida evidencia final e verifica arquivos/quantidades do CAD salvo sem modifica-lo."""
from pathlib import Path
import sys,json,hashlib,itertools
sys.path.insert(0,'/usr/lib/freecad/lib')
import FreeCAD as A
import Part
R=Path(__file__).resolve().parent; ROOT=R.parents[1]; K=json.loads((R/'kit-r05.json').read_text()); validations={}
for name in ['validacao-montagem-r05.json','validacao-funcional-r05.json','validacao-referencias-r05.json','validacao-stl.json']:
 validations[name]=json.loads((R/name).read_text()); assert validations[name]['status']=='OK',name
assert len(K['insertos'])==len(K['parafusos'])==len({j['inserto'] for j in K['parafusos']})
assert K['porcas']==K['velcro']==K['cintas']==0
D=A.openDocument(str(R/'slamderson-fixacao-r05.FCStd'))
instances=[]
for p in K['pecas']:
 for name in p['objetos']:
  o=D.getObject(name); assert o.CodigoPeca==p['codigo'] and hasattr(o,'CorDoEstudo') and o.Shape.isValid() and len(o.Shape.Solids)==1
  b=o.Shape.BoundBox
  instances.append({'codigo':p['codigo'],'objeto':name,'bbox_CAD_mm':[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]})
assert len(instances)==K['quantidade_pecas_montagem']
# Ferragens contra ferragens: rosca nominal e diametros iguais se tocam sem volume de intersecao.
hardware=[D.getObject(j['objeto_parafuso']) for j in K['parafusos']]+[D.getObject(j['objeto_arruela']) for j in K['parafusos'] if j['objeto_arruela']]+[D.getObject('Inserto_'+i['id']) for i in K['insertos']]
errors=[]; checks=0
for a,b in itertools.combinations(hardware,2):
 checks+=1; x=a.Shape.BoundBox; y=b.Shape.BoundBox
 if not all(min(getattr(x,hi),getattr(y,hi))-max(getattr(x,lo),getattr(y,lo))>1e-7 for lo,hi in [('XMin','XMax'),('YMin','YMax'),('ZMin','ZMax')]): continue
 aa=[s for s in a.Shape.Solids if s.BoundBox.intersect(y)]; bb=[s for s in b.Shape.Solids if s.BoundBox.intersect(x)]
 vv=Part.makeCompound(aa).common(Part.makeCompound(bb)).Volume if aa and bb else 0.
 if vv>2e-4: errors.append({'a':a.Name,'b':b.Name,'mm3':vv})
assert not errors,errors
for name in ['pecas-impressao-r05.FCStd','cupom-insertos-r05.FCStd']:
 d=A.openDocument(str(R/name)); obs=[o for o in d.Objects if hasattr(o,'CodigoPeca')]
 assert len(obs)==(K['quantidade_tipos_STL'] if name.startswith('pecas') else 1)
 assert all(o.Shape.isValid() and len(o.Shape.Solids)==1 and hasattr(o,'CorDoEstudo') for o in obs)
 A.closeDocument(d.Name)
for p,h in K['fontes_preservadas_sha256'].items(): assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h
files=[p for p in R.iterdir() if p.suffix in {'.FCStd','.py','.md','.csv','.log','.json'} and p.name not in {'requisitos-insertos.json','validacao-entrega-r05.json'}]+list((R/'stl').glob('*.stl'))
result={'status':'OK','prototipo_nao_liberado_fabricacao':True,'validadores':{n:v['status'] for n,v in validations.items()},'CAD_montagem_reaberto':True,'CAD_catalogo_e_cupom_reabertos':True,'tipos_STL':K['quantidade_tipos_STL'],'pecas_montagem':len(instances),'quantidade_com_cupom':K['quantidade_total_a_imprimir'],'parafusos_M3':len(K['parafusos']),'insertos_M3':len(K['insertos']),'arruelas':K['arruelas_M3_0_5mm'],'pares_ferragem_x_ferragem':checks,'erros_ferragem':errors,'min_folga_ponta_fim_inserto_mm':min(j['folga_ponta_ao_fim_inserto_mm'] for j in K['parafusos']),'min_folga_ponta_fundo_mm':min(j['folga_ponta_fundo_mm'] for j in K['parafusos']),'instancias_CAD':instances,'fontes_R04_preservadas_sha256':K['fontes_preservadas_sha256'],'arquivos_sha256':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)},'observacao':'Este manifesto nao inclui requisitos-insertos.json mantido pelo pai, backups automaticos ou a si mesmo. Todos os ensaios sao digitais, sem FDM/montagem real.'}
(R/'validacao-entrega-r05.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['instancias_CAD','arquivos_sha256','fontes_R04_preservadas_sha256']},ensure_ascii=False))
