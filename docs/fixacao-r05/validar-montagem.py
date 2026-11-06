"""Auditoria BREP R05 salva/reaberta. Nenhuma aprovacao fisica implicita."""
from pathlib import Path
import sys,json,itertools,hashlib,time
sys.path.insert(0,'/usr/lib/freecad/lib')
import FreeCAD as A
import Part
R=Path(__file__).resolve().parent; ROOT=R.parents[1]; K=json.loads((R/'kit-r05.json').read_text()); D=A.openDocument(str(R/'slamderson-fixacao-r05.FCStd')); V=A.Vector
errors=[]; counts={}; t0=time.time()
def overlap(a,b):
 x=a.BoundBox; y=b.BoundBox
 return all(min(getattr(x,hi),getattr(y,hi))-max(getattr(x,lo),getattr(y,lo))>1e-7 for lo,hi in [('XMin','XMax'),('YMin','YMax'),('ZMin','ZMax')])
def vol(a,b):
 if not overlap(a,b): return 0.
 aa=[s for s in a.Solids if overlap(s,b)]; bb=[s for s in b.Solids if overlap(s,a)]
 if not aa or not bb: return 0.
 return Part.makeCompound(aa).common(Part.makeCompound(bb)).Volume
printed=[D.getObject(n) for p in K['pecas'] for n in p['objetos']]
assert len(printed)==K['quantidade_pecas_montagem']
assert all(o.Shape.isValid() and len(o.Shape.Solids)==1 and o.Shape.Volume>0 and hasattr(o,'CorDoEstudo') and o.CodigoPeca for o in printed)
assert not [o.Name for o in D.Objects if o.Name.startswith(('Porca','CintaPowerbank'))]
components=['RaspberryPi5','L298N','MPU6050','Reserva_ESP','Reserva_Powerbank','Reserva_Holder4AA','LidarC1']
def check(a,b,typ,an,bn,tol=2e-4):
 counts[typ]=counts.get(typ,0)+1; vv=vol(a,b)
 if vv>tol: errors.append({'tipo':typ,'a':an,'b':bn,'mm3':round(vv,7)})
for a,b in itertools.combinations(printed,2): check(a.Shape,b.Shape,'pecas',a.Name,b.Name)
print('PARES',json.dumps(errors),flush=True)
for a in printed:
 for n in components: check(a.Shape,D.getObject(n).Shape,'componente',a.Name,n)
print('COMPONENTES',json.dumps([e for e in errors if e['tipo']=='componente']),flush=True)
for j in K['parafusos']:
 for n in [j['objeto_parafuso'],j['objeto_arruela']]:
  if n is None: continue
  s=D.getObject(n).Shape
  for a in printed: check(s,a.Shape,'ferragem_plastico',n,a.Name)
  for cn in components: check(s,D.getObject(cn).Shape,'ferragem_componente',n,cn)
print('FERRAGENS',json.dumps([e for e in errors if e['tipo'].startswith('ferragem')]),flush=True)
# Nao contar envelope dentado4.7 vs piloto4.3 como colisao acidental: interferencia termica intencional.
# Geometria de alojamento: >=2mm radial em torno do diametro externo e >=2mm fundo.
insert_rows=[]
for i in K['insertos']:
 p=V(*i['entrada_mm']); a=V(*i['eixo_para_dentro']); own=D.getObject(i['objeto']).Shape
 # Evitar contatos numericos na entrada. Anel radial ate4.35(2.35+2), ao longo5.68.
 radial=Part.makeCylinder(4.35,5.66,p+a*.01,a).cut(Part.makeCylinder(2.351,5.68,p,a))
 missing=radial.cut(own).Volume
 bottom=Part.makeCylinder(2.15,2.,p+a*6,a); missbottom=bottom.cut(own).Volume
 counts['alojamentos']=counts.get('alojamentos',0)+1
 if missing>1e-3: errors.append({'tipo':'parede_radial_menor_2mm','a':i['id'],'b':i['objeto'],'mm3_faltantes':round(missing,6)})
 if missbottom>1e-3: errors.append({'tipo':'fundo_menor_2mm','a':i['id'],'b':i['objeto'],'mm3_faltantes':round(missbottom,6)})
 ins=D.getObject('Inserto_'+i['id']).Shape
 for cn in components: check(ins,D.getObject(cn).Shape,'inserto_componente',i['id'],cn)
 insert_rows.append({'id':i['id'],'parede_radial_2mm':missing<1e-3,'fundo_2mm':missbottom<1e-3,'interferencia_termica_radial_mm':.2})
for j in K['parafusos']:
 i=next(i for i in K['insertos'] if i['id']==j['inserto']); p=V(*j['posicao_cabeca_mm']); a=V(*j['eixo_para_dentro']); dist=(V(*i['entrada_mm'])-p).dot(a); eng=j['comprimento_mm']-dist
 assert 3<=eng<=5.3 and eng<5.68 and eng<6 and abs(eng-j['engate_mm'])<1e-6
# Confirmar furos oficiais da Pi preservados e pinos2.2 nao metal.
pi=D.getObject('RaspberryPi5').Shape
circles={(round(f.Surface.Center.x,4),round(f.Surface.Center.y,4)) for f in pi.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-1.35)<1e-5 and abs(f.Surface.Axis.z)>.99}
assert all(any(abs(x-cx)<1e-4 and abs(y-cy)<1e-4 for cx,cy in circles) for x,y in K['pi_furos_CAD_xy_mm'])
# Retirada lateral das duas meias tampas; pontes P10 acompanham cada metade.
# Obstaculos fixos: demais pecas, todas placas/envelopes. Nao inclui fixadores removidos.
moving_codes={'P03','P04','P05','P06','P10'}
fixed=[o for o in printed if o.CodigoPeca not in moving_codes]+[D.getObject(n) for n in components]
for sg,codes,bridge in [(-1,['P03','P05'],'UniaoTetoE'),(1,['P04','P06'],'UniaoTetoD')]:
 movers=[D.getObject(p['objetos'][0]) for p in K['pecas'] if p['codigo'] in codes]+[D.getObject(bridge)]
 # Primeiro elevar2mm (teto139 < baseC1 140), depois retirar lateralmente.
 # Movimento puramente horizontal colide com bosses F externos da portinhola PB.
 for dz,dx in [(0,0),(.5,0),(1,0),(2,0),(2,5),(2,15),(2,40),(2,80),(2,110)]:
  for o in movers:
   s=o.Shape.copy(); s.translate(V(sg*dx,0,dz))
   for obs in fixed: check(s,obs.Shape,'retirada_tampa',o.Name+'@'+str((dx,dz)),obs.Name)
# Gaveta: bateria desliza para tras apos retirar P08; folga rigida de laterais e labios.
pb=D.getObject('Reserva_Powerbank').Shape
obstacles=[o for o in printed if o.CodigoPeca!='P08']+[D.getObject(n) for n in components if n!='Reserva_Powerbank']
for dy in (0,1,5,20,40,75,100):
 s=pb.copy(); s.translate(V(0,dy,0))
 for obs in obstacles: check(s,obs.Shape,'saque_powerbank','PB@'+str(dy),obs.Name)
# Celulas AA, retirada vertical amostrada com tampas/piso removidos (manutencao modulo inferior).
aa_obs=[o for o in printed if o.CodigoPeca not in {'P03','P04','P05','P06','P10','P12','P18','P19','P20','P24','P26','P27'}]
for idx in range(1,5):
 orig=D.getObject('AA_'+str(idx)).Shape
 for dz in (0,5,15,30,60):
  s=orig.copy(); s.translate(V(0,0,dz))
  for obs in aa_obs: check(s,obs.Shape,'saque_pilhas','AA_'+str(idx)+'@'+str(dz),obs.Name)
for p,sha in K['fontes_preservadas_sha256'].items(): assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==sha
res={'status':'FALHOU' if errors else 'OK','contagens':counts,'pecas_1_solido_valido':len(printed),'insertos_auditados':insert_rows,'engate_intervalo_mm':[min(j['engate_mm'] for j in K['parafusos']),max(j['engate_mm'] for j in K['parafusos'])],'fontes_R04_preservadas':True,'pi_furos2_7_preservados':True,'porcas_cintas_velcro':0,'erros':errors,'duracao_s':round(time.time()-t0,2),'limites':['Caminhos discretos nao provam movimento continuo.','Tampas: elevar2mm antes de deslocar lateralmente; nao puxar apenas na horizontal.','Bateria sai para +Y com P08 removida; celulas AA com modulo superior desmontado.','Acesso termico depende da sequencia documentada; nao modelo de ferro especifico.','Nao valida furacao fisica chassi, C1, holder, ESP nem resistencia FDM.']}
(R/'validacao-montagem-r05.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in res.items() if k!='insertos_auditados'},ensure_ascii=False),flush=True)
A.closeDocument(D.Name)
assert not errors,'Interferencias devem ser resolvidas antes de entrega.'
