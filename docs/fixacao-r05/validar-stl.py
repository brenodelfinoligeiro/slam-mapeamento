"""Verificacao independente: reabrir todos os binarios STL exportados, em milimetros."""
from pathlib import Path
import json,hashlib
import numpy as np
import trimesh
R=Path(__file__).resolve().parent; K=json.loads((R/'kit-r05.json').read_text()); rows=[]
assert {p.name for p in (R/'stl').glob('*.stl')}=={Path(p['arquivo']).name for p in K['pecas']},'STL extra ou ausente'
for p in K['pecas']:
 f=R/p['arquivo']; m=trimesh.load_mesh(f,process=True)
 assert np.isfinite(m.vertices).all() and len(m.faces)>0,p['codigo']
 assert m.is_watertight and m.is_winding_consistent and m.volume>0,p['codigo']
 assert len(m.split(only_watertight=False))==1,p['codigo']
 assert np.all(m.bounds[0]>=-1e-5) and abs(m.bounds[0][2])<1e-5,p['codigo']
 dims=m.extents; assert dims[0]+16<=220 and dims[1]+16<=220 and dims[2]<=250,p['codigo']
 assert np.allclose(dims,p['dimensoes_impressao_mm'],atol=.15),p['codigo']
 assert abs(m.volume/p['volume_mm3']-1)<.015,(p['codigo'],m.volume,p['volume_mm3'])
 assert hashlib.sha256(f.read_bytes()).hexdigest()==p['sha256']
 rows.append({'codigo':p['codigo'],'quantidade':p['quantidade'],'dimensoes_mm':dims.tolist(),'componentes':1,'fechado':True,'orientacao_consistente':True,'volume_positivo':True,'Z_min_mm':float(m.bounds[0][2]),'folga_apos_brim5_mm':[(220-dims[0])/2-5,(220-dims[1])/2-5]})
assert len(rows)==K['quantidade_tipos_STL'] and sum(r['quantidade'] for r in rows)==K['quantidade_total_a_imprimir']
result={'status':'OK','tipos_STL':len(rows),'quantidade_com_cupom':sum(r['quantidade'] for r in rows),'modelos':rows,'limite':'Sem impressao fisica; nao comprova tolerancia, resistencia ou material.'}
(R/'validacao-stl.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':'OK','STLs':len(rows),'total_impresso_incluindo_cupom':sum(r['quantidade'] for r in rows),'maior_eixo_xy_mm':max(max(r['dimensoes_mm'][:2]) for r in rows),'menor_folga_apos_brim_mm':min(min(r['folga_apos_brim5_mm']) for r in rows)}))
