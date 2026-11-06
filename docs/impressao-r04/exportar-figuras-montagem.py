"""Exportação somente leitura da montagem R04 para figuras de montagem."""
from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,'/usr/lib/freecad/lib')
import FreeCAD as A
import Part
import numpy as np
R=Path(__file__).resolve().parent; OUT=Path(sys.argv[1]); OUT.mkdir(parents=True,exist_ok=True)
f=R/'slamderson-impressao-r04.FCStd'; old=hashlib.sha256(f.read_bytes()).hexdigest(); D=A.openDocument(str(f))
records=[]
for o in D.Objects:
 code=getattr(o,'CodigoPeca','')
 if not code and o.Name not in ['Mecanica_04','RaspberryPi5','L298N','MPU6050','LidarC1']: continue
 if hasattr(o,'Shape'): v,t=o.Shape.tessellate(.35); b=o.Shape.BoundBox
 else: v,t=o.Mesh.Topology; b=o.Mesh.BoundBox
 xyz=np.asarray([(q.x,q.y,q.z) for q in v],dtype='<f4'); tri=np.asarray(t,dtype='<i4')
 faces=np.empty(len(tri),dtype=[('n','u1'),('idx','<i4',(3,))]); faces['n']=3; faces['idx']=tri
 name=o.Name+'.ply'; header=f'ply\nformat binary_little_endian 1.0\nelement vertex {len(xyz)}\nproperty float x\nproperty float y\nproperty float z\nelement face {len(tri)}\nproperty list uchar int vertex_indices\nend_header\n'
 with (OUT/name).open('wb') as p: p.write(header.encode()); xyz.tofile(p); faces.tofile(p)
 records.append({'arquivo':name,'objeto':o.Name,'codigo':code or o.Name,'rotulo':o.Label,'centro':[(b.XMin+b.XMax)/2,(b.YMin+b.YMax)/2,(b.ZMin+b.ZMax)/2],'triangulos':len(tri)})
assert sum(bool(x['codigo'].startswith('P') and x['codigo'][1:].isdigit()) for x in records)==42
(OUT/'montagem-scene.json').write_text(json.dumps({'sha256_FCStd':old,'objetos':records},ensure_ascii=False,indent=2)+'\n')
assert hashlib.sha256(f.read_bytes()).hexdigest()==old
print(json.dumps({'objetos':len(records),'triangulos':sum(x['triangulos'] for x in records)}))
A.closeDocument(D.Name)
