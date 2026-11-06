"""Seis projeções ortográficas dos STL efetivamente entregues, sem alterar os arquivos.
Blender: --background --factory-startup --disable-autoexec --python SCRIPT -- PASTA
"""
from pathlib import Path
import sys,json,hashlib
import bpy
import numpy as np
from mathutils import Matrix,Vector
R=Path(sys.argv[sys.argv.index('--')+1]); M=json.loads((R/'manifesto-vistas.json').read_text())
OUT=R/'renders6'; OUT.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
S=bpy.context.scene; S.render.engine='CYCLES'; S.cycles.device='CPU'; S.cycles.samples=12; S.cycles.use_denoising=True
S.render.resolution_x=1000; S.render.resolution_y=1000; S.render.resolution_percentage=100
S.render.image_settings.file_format='PNG'; S.render.image_settings.color_mode='RGBA'; S.render.film_transparent=True
S.world.use_nodes=True; S.world.node_tree.nodes['Background'].inputs[0].default_value=(.8,.85,.9,1); S.world.node_tree.nodes['Background'].inputs[1].default_value=.65
S.view_settings.view_transform='AgX'
for pos,power,size in [((130,-160,240),550000,180),((-150,80,150),400000,170),((80,170,110),300000,140)]:
 bpy.ops.object.light_add(type='AREA',location=pos); o=bpy.context.object; o.data.energy=power; o.data.shape='DISK'; o.data.size=size; o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(); cam=bpy.context.object; cam.data.type='ORTHO'; cam.data.ortho_scale=124; cam.data.clip_end=2000; S.camera=cam
mat=bpy.data.materials.new('Peça'); mat.use_nodes=True; bs=mat.node_tree.nodes['Principled BSDF']; bs.inputs['Base Color'].default_value=(.28,.39,.50,1); bs.inputs['Roughness'].default_value=.6
views=[('superior',(0,0,400),(1,0,0),(0,1,0),(0,0,1)),('frontal',(0,-400,0),(1,0,0),(0,0,1),(0,-1,0)),('lateral',(400,0,0),(0,1,0),(0,0,1),(1,0,0))]
views += [('inferior',(0,0,-400),(1,0,0),(0,-1,0),(0,0,-1)),('traseira',(0,400,0),(-1,0,0),(0,0,1),(0,1,0)),('esquerda',(-400,0,0),(0,-1,0),(0,0,1),(-1,0,0))]
records=[]
for row in M['pecas']:
 f=R/'stl'/row['arquivo_zip']; raw=f.read_bytes(); assert hashlib.sha256(raw).hexdigest()==row['sha256']
 count=int.from_bytes(raw[80:84],'little'); assert len(raw)==84+50*count
 dtype=np.dtype([('normal','<f4',(3,)),('vertices','<f4',(3,3)),('attr','<u2')])
 vv=np.frombuffer(raw,offset=84,count=count,dtype=dtype)['vertices'].reshape(-1,3)
 vertices,idx=np.unique(vv,axis=0,return_inverse=True); faces=idx.reshape(-1,3)
 lo=vertices.min(axis=0); hi=vertices.max(axis=0); dims=hi-lo; center=(lo+hi)/2
 # Só a apresentação é normalizada: o arquivo STL e suas unidades não mudam.
 positions=(vertices-center)*(100/max(dims))
 mesh=bpy.data.meshes.new(row['codigo']); mesh.from_pydata(positions.tolist(),[],faces.tolist()); mesh.update()
 ob=bpy.data.objects.new(row['codigo'],mesh); S.collection.objects.link(ob); ob.data.materials.append(mat)
 paths=[]
 for name,loc,right,up,back in views:
  cam.location=loc; cam.rotation_euler=Matrix((right,up,back)).transposed().to_euler()
  target=OUT/(row['codigo']+'_'+name+'.png')
  cached=R/'renders'/target.name
  if cached.exists():
   import shutil; shutil.copy2(cached,target)
  else:
   S.render.filepath=str(target); bpy.ops.render.render(write_still=True)
  paths.append(target.name)
 records.append({'codigo':row['codigo'],'arquivo_zip':row['arquivo_zip'],'sha256':row['sha256'],'dimensoes_STL_mm':dims.tolist(),'triangulos':count,'vistas':paths})
 bpy.data.objects.remove(ob,do_unlink=True); bpy.data.meshes.remove(mesh)
assert len(records)==24 and sum(len(x['vistas']) for x in records)==144
(R/'render-report-seis.json').write_text(json.dumps({'blender':bpy.app.version_string,'projecao':'ortografica','orientacao':'STL de impressão: seis direções ortográficas; sem modificar os STL','pecas':records},ensure_ascii=False,indent=2)+'\n')
