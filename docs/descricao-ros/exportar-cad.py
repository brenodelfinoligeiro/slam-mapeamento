"""Extrai apenas folhas da montagem R05. Não usa STL orientado para impressão.
Uso: /usr/bin/python exportar-cad.py PASTA_CACHE
"""
from pathlib import Path
import sys,json,hashlib
import numpy as np
sys.path.insert(0,'/usr/lib/freecad/lib')
import FreeCAD as A
import Part
R=Path(__file__).resolve().parents[1];OUT=Path(sys.argv[1]);OUT.mkdir(parents=True,exist_ok=True)
REGISTRO=json.loads((R/'descricao-ros/origem-mecanica.json').read_text());CAD=R.parent/REGISTRO['arquivo'];K=json.loads((R/'fixacao-r05/kit-r05.json').read_text());sha=hashlib.sha256(CAD.read_bytes()).hexdigest();D=A.openDocument(str(CAD))
def caixa(nome):
 o=D.getObject(nome);b=(o.Mesh if hasattr(o,'Mesh') else o.Shape).BoundBox
 return [getattr(b,n) for n in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]
def centro(b):return [(b[i]+b[i+3])/2 for i in range(3)]
tire_l=caixa('Mecanica_00');tire_r=caixa('Mecanica_01');cl=centro(tire_l);cr=centro(tire_r);base=[(cl[i]+cr[i])/2 for i in range(3)];ground=min(tire_l[2],tire_r[2])
assert cl[0]>cr[0] and abs(cl[1]-cr[1])<.1 and abs(cl[2]-cr[2])<.1
rot=np.array([[0.,-1.,0.],[1.,0.,0.],[0.,0.,1.]])
assert abs(np.linalg.det(rot)-1)<1e-12
printed=[n for p in K['pecas'] for n in p['objetos']];assert len(printed)==44
hardware=[j['objeto_parafuso'] for j in K['parafusos']]+[j['objeto_arruela'] for j in K['parafusos'] if j['objeto_arruela']]+['Inserto_'+i['id'] for i in K['insertos']]
# A origem do corpo C1 é o centro XY do envelope na face inferior, NÃO plano óptico.
b=caixa('LidarC1');lidar=[(b[0]+b[3])/2,(b[1]+b[4])/2,b[2]]
# Datum mecânico da MPU: ponto médio dos dois furos, na face inferior do PCB.
mpu=D.getObject('MPU6050').Shape;holes=sorted({(round(f.Surface.Center.x,5),round(f.Surface.Center.y,5)) for f in mpu.Faces if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-1.5)<1e-5 and abs(f.Surface.Axis.z)>.99})
assert len(holes)==2,holes
# Face PCB de referência identificada no CAD por apoio do berço/pinos, não pelo Z mínimo dos componentes.
imu=[sum(x for x,y in holes)/2,sum(y for x,y in holes)/2,60.4]
casters=[f'Mecanica_{i:02d}' for i in [5,6,7]];cb=caixa('Mecanica_05');caster=[(cb[0]+cb[3])/2,(cb[1]+cb[4])/2,45.4]
frames={'base_link':base,'left_wheel_link':cl,'right_wheel_link':cr,'caster_link':caster,'lidar_mount_link':lidar,'imu_mount_link':imu}
groups=[
 ('estrutura','base_link',printed,'estrutura',None),
 ('ferragens','base_link',hardware,'metal',None),
 ('chassi','base_link',['Mecanica_04'],'metal',None),
 ('motores','base_link',[f'Mecanica_{i:02d}' for i in range(8,36)],'motores',None),
 ('eletronica','base_link',['RaspberryPi5','L298N','Encoder_E','Encoder_D'],'placas',45000),
 ('holder','base_link',['Reserva_Holder4AA'],'reserva',None),
 ('pilhas','base_link',[n for i in range(1,5) for n in ['AA_'+str(i),'PoloAA_'+str(i)]],'pilhas',None),
 ('esp_reserva','base_link',['Reserva_ESP'],'reserva',None),
 ('powerbank','base_link',['Reserva_Powerbank'],'bateria',None),
 ('pneu_esquerdo','left_wheel_link',['Mecanica_00'],'pneu',18000),
 ('cubo_esquerdo','left_wheel_link',['Mecanica_02'],'cubo',None),
 ('disco_esquerdo','left_wheel_link',['Disco_D'],'disco',None),
 ('pneu_direito','right_wheel_link',['Mecanica_01'],'pneu',18000),
 ('cubo_direito','right_wheel_link',['Mecanica_03'],'cubo',None),
 ('disco_direito','right_wheel_link',['Disco_E'],'disco',None),
 ('rodizio','caster_link',casters,'metal',None),
 ('lidar','lidar_mount_link',['LidarC1'],'sensor',None),
 ('imu','imu_mount_link',['MPU6050'],'placas',None),
]
seen=[];rows=[]
for name,link,names,material,limit in groups:
 verts=[];tris=[];offset=0;objects=[];origin=np.asarray(frames[link])
 for n in names:
  o=D.getObject(n);assert o is not None,n;seen.append(n)
  if hasattr(o,'Mesh'):v,t=o.Mesh.Topology
  else:v,t=o.Shape.tessellate(.5)
  a=np.asarray([[p.x,p.y,p.z] for p in v],dtype=np.float64);f=np.asarray(t,dtype=np.int32)
  assert len(a)>0 and len(f)>0 and np.isfinite(a).all(),n
  local=(a-origin)@rot.T*.001;verts.append(local.astype('<f4'));tris.append(f+offset);offset+=len(a)
  objects.append({'objeto':n,'rotulo':o.Label,'bbox_CAD_mm':caixa(n),'triangulos':len(f)})
 xyz=np.concatenate(verts);faces=np.concatenate(tris);packed=np.empty(len(faces),dtype=[('n','u1'),('idx','<i4',(3,))]);packed['n']=3;packed['idx']=faces
 header=f'ply\nformat binary_little_endian 1.0\nelement vertex {len(xyz)}\nproperty float x\nproperty float y\nproperty float z\nelement face {len(faces)}\nproperty list uchar int vertex_indices\nend_header\n'
 dest=OUT/(name+'.ply')
 with dest.open('wb') as f:f.write(header.encode());xyz.tofile(f);packed.tofile(f)
 rows.append({'nome':name,'arquivo':dest.name,'link':link,'material':material,'limite_visual_triangulos':limit,'objetos':objects,'triangulos_originais':len(faces),'bbox_local_m':[xyz.min(axis=0).tolist(),xyz.max(axis=0).tolist()]})
 print(name,len(faces),flush=True)
assert len(seen)==len(set(seen)),'Objeto exportado em dois grupos'
assert set(printed)<=set(seen)
# Grupos/compostos de visualização não são folhas: evita duplicar toda a montagem.
assert not {'Inferior','Superior','Lidar','CarcacaBase','Tampas','Acessos','FerragensR05'}&set(seen)
result={'revisao':'R05','unidade':'m','registro_origem':'docs/descricao-ros/origem-mecanica.json','sha256_CAD':sha,'pecas_impressas':len(printed),'rotacao_CAD_para_ROS':rot.tolist(),'origem_base_CAD_mm':base,'plano_rodas_CAD_mm':ground,'altura_base_m':(base[2]-ground)*.001,'frames_CAD_mm':frames,'distancia_rodas_m':(cl[0]-cr[0])*.001,'raio_vertical_roda_m':max(tire_l[5]-tire_l[2],tire_r[5]-tire_r[2])*.0005,'pneus_bbox_CAD_mm':{'left':tire_l,'right':tire_r},'cubos_bbox_CAD_mm':{'left':caixa('Mecanica_02'),'right':caixa('Mecanica_03')},'rodizio_acima_plano_rodas_mm':min(caixa(n)[2] for n in casters)-ground,'sensores_calibrados':False,'inerciais_medidas':False,'grupos':rows,'limites':['Modelo CAD de referência, não geometria física medida.','Rodízio fica acima do plano das rodas no CAD; não corrigido artificialmente.','Frames imu_mount_link/lidar_mount_link são datums mecânicos, não frames calibrados dos dados.','Rodízio fixo para visualização; não modelo de contato/dinâmica.','Discos de encoder ilustrativos: não inferir PPR.','Sem massas/inércias inventadas.','Derivados CAD permanecem locais por licenças pendentes.']}
(OUT/'exportacao-cad.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');assert hashlib.sha256(CAD.read_bytes()).hexdigest()==sha
A.closeDocument(D.Name)
