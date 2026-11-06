"""Exporta a geometria do FCStd reaberto para renderização, sem simplificar malhas."""
from pathlib import Path
import sys,json,tarfile
sys.path.insert(0,'/usr/lib/freecad/lib')
import FreeCAD as App
import Part
import numpy as np
ROOT=Path(__file__).resolve().parent
OUT=Path('/home/lamggm/.hermes/cache/scratch/slamderson-shell-r02/scene'); OUT.mkdir(parents=True,exist_ok=True)
doc=App.openDocument(str(ROOT/'slamderson-coberto-r02.FCStd'))
rows=[]
groups={o.Name:g.Name for g in doc.Objects if hasattr(g,'Group') for o in g.Group}

def export(name,verts,faces,color,source):
    points=np.asarray([(v.x,v.y,v.z) for v in verts],dtype='<f4')
    tris=np.asarray(faces,dtype='<i4')
    record=np.empty(len(tris),dtype=[('n','u1'),('indices','<i4',(3,))]); record['n']=3; record['indices']=tris
    path=OUT/(name+'.ply')
    header=f'ply\nformat binary_little_endian 1.0\nelement vertex {len(points)}\nproperty float x\nproperty float y\nproperty float z\nelement face {len(tris)}\nproperty list uchar int vertex_indices\nend_header\n'
    with path.open('wb') as f: f.write(header.encode()); points.tofile(f); record.tofile(f)
    rows.append({'file':path.name,'name':source.Label,'group':groups[source.Name],'color':list(color),'triangles':len(tris),'source_object':source.Name})

for o in doc.Objects:
    if not hasattr(o,'CorDoEstudo'): continue
    if o.Name=='RaspberryPi5':
        buckets={}
        for solid in o.Shape.Solids:
            b=solid.BoundBox; x,y,z=b.XLength,b.YLength,b.ZLength
            if x>70 and y>40 and z<3: c=(.12,.45,.24)
            elif (x>7 and y>7 and z>4) or (x>9 and y>9 and z<4): c=(.73,.76,.78)
            elif x<2 and y<2: c=(.78,.64,.27)
            else: c=(.17,.19,.21)
            buckets.setdefault(c,[]).append(solid)
        for i,(c,solids) in enumerate(buckets.items()):
            v,t=Part.makeCompound(solids).tessellate(1.2); export(o.Name+str(i),v,t,c,o)
    elif hasattr(o,'Shape'):
        v,t=o.Shape.tessellate(.8); export(o.Name,v,t,o.CorDoEstudo[:3],o)
    else:
        # Mesh.Topology já incorpora Placement no FreeCAD; aplicar outra vez desloca a mecânica em dobro.
        v,t=o.Mesh.Topology
        export(o.Name,v,t,o.CorDoEstudo[:3],o)
(OUT/'scene.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
archive=OUT.parent/'scene.tar'
with tarfile.open(archive,'w') as tf:
    for f in OUT.iterdir(): tf.add(f,arcname=f.name)
print(json.dumps({'archive':str(archive),'bytes':archive.stat().st_size,'objects':len(rows),'triangles':sum(x['triangles'] for x in rows)}))
