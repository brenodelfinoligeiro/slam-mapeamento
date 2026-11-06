"""Auditoria de fatiamento em diretório isolado; NÃO envia comandos à impressora.
Uso: python auditar-slicer.py PASTA_R05 [CODIGO_STL]; requer OrcaSlicer instalado.
G-code de auditoria fica fora do pacote a entregar.
"""
from pathlib import Path
import sys,json,subprocess,hashlib,time
R=Path(sys.argv[1]).resolve(); ONLY=sys.argv[2] if len(sys.argv)>2 else None
PRO=Path('/opt/orca-slicer/resources/profiles'); TMP=R/'auditoria-slicer'; TMP.mkdir(exist_ok=True)
def locate(name,category):
 own=PRO/'Creality'/category/(name+'.json')
 if own.exists(): return own
 matches=sorted(PRO.glob('*/'+category+'/'+name+'.json'))
 if not matches: matches=list(PRO.rglob(name+'.json'))
 assert matches,name
 return matches[0]
def flatten(path,stack=None):
 stack=stack or []
 assert str(path) not in stack,path
 j=json.loads(path.read_text()); base={}
 if j.get('inherits'): base=flatten(locate(j['inherits'],path.parent.name),stack+[str(path)])
 base.update(j); base.pop('inherits',None)
 return base
names={'machine':'Creality Ender-3 V3 SE 0.4 nozzle','process':'0.20mm Standard @Creality Ender3V3SE 0.4','filament':'Creality Generic PLA @Ender-3V3-all'}
configs={}; source=[]
for typ,name in names.items():
 path=locate(name,typ); j=flatten(path)
 if typ=='machine': j['printer_settings_id']=name
 if typ=='process': j['print_settings_id']=name
 if typ=='filament': j['filament_settings_id']=[name]
 source.append({'tipo':typ,'nome':name,'arquivo_instalado':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
 if typ=='process':
  j.update({'layer_height':'0.2','initial_layer_print_height':'0.2','wall_loops':'4','top_shell_layers':'5','bottom_shell_layers':'5','sparse_infill_density':'25%','sparse_infill_pattern':'gyroid','brim_type':'outer_only','brim_width':'5','brim_object_gap':'0.2','skirt_loops':'0','enable_support':'1','support_type':'normal(auto)','support_on_build_plate_only':'1','support_threshold_angle':'30','print_sequence':'by layer'})
 # Preset de usuário COMPLETO herdado do preset de sistema exato; a CLI usa
 # inherits para checar compatibilidade, mesmo com os valores já expandidos.
 j['inherits']=name; j['name']='R05 auditoria / '+name
 j['from']='user'; j['instantiation']='true'; dest=TMP/(typ+'.json'); dest.write_text(json.dumps(j,indent=2)); configs[typ]=dest
assert json.loads(configs['machine'].read_text())['printable_area']==['0x0','220x0','220x220','0x220']
K=json.loads((R/'kit-r05.json').read_text()); results=[]
for p in K['pecas']:
 if ONLY and p['codigo']!=ONLY: continue
 out=TMP/p['codigo']; out.mkdir(exist_ok=True)
 cmd=['orca-slicer','--datadir',str(TMP/'dados-isolados'),'--load-settings',str(configs['machine'])+';'+str(configs['process']),'--load-filaments',str(configs['filament']),'--orient','0','--arrange','1','--slice','0','--outputdir',str(out),str(R/p['arquivo'])]
 t=time.time()
 with (out/'log.txt').open('w') as log: proc=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,timeout=300)
 files=[{'arquivo':str(f.relative_to(TMP)),'bytes':f.stat().st_size} for f in out.rglob('*') if f.is_file()]
 row={'codigo':p['codigo'],'exit_code':proc.returncode,'segundos_execucao':round(time.time()-t,2),'arquivos':files}
 results.append(row); print(json.dumps(row),flush=True)
 if proc.returncode:
  print((out/'log.txt').read_text()[-8000:]); break
report={'programa':'OrcaSlicer 2.4.2','impressora':'Creality Ender-3 V3 SE 0.4 nozzle','volume_mm':[220,220,250],'filamento_de_referencia':'Generic PLA; não comprova filamento/temperatura reais','processo':'0.20mm;4 paredes;25% gyroid;5 camadas topo/fundo;brim5mm;suportes normais automáticos só na mesa','fontes_perfis':source,'resultados':results,'limites':'Auditoria de geometria/fatiamento. Não executar G-code de auditoria na impressora; não são presets fisicamente calibrados.'}
(R/('auditoria-orca-'+ONLY+'.json' if ONLY else 'auditoria-orca.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
assert results and all(x['exit_code']==0 for x in results)
if not ONLY: assert len(results)==len(K['pecas'])
