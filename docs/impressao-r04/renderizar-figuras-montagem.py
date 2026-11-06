"""Figuras ilustrativas, explodidas e etiquetáveis, do CAD R04 reaberto."""
import bpy,sys,json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(sys.argv[sys.argv.index('--')+1]); data=json.loads((R/'montagem-scene.json').read_text()); OUT=R/'figuras'; OUT.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
S=bpy.context.scene; S.render.engine='CYCLES'; S.cycles.device='CPU'; S.cycles.samples=16; S.cycles.use_denoising=True
S.render.resolution_x=1400; S.render.resolution_y=1100; S.render.resolution_percentage=100; S.render.image_settings.file_format='PNG'; S.render.image_settings.color_mode='RGBA'; S.render.film_transparent=True
S.world.use_nodes=True; S.world.node_tree.nodes['Background'].inputs[0].default_value=(.85,.89,.94,1); S.world.node_tree.nodes['Background'].inputs[1].default_value=.65; S.view_settings.view_transform='AgX'
for loc,power,size in [((300,-320,460),1700000,280),((-320,120,330),1100000,260),((60,440,340),1300000,240)]:
 bpy.ops.object.light_add(type='AREA',location=loc); q=bpy.context.object; q.data.energy=power; q.data.shape='DISK'; q.data.size=size; q.rotation_euler=(Vector((0,100,90))-q.location).to_track_quat('-Z','Y').to_euler()
items=[]
for row in data['objetos']:
 bpy.ops.wm.ply_import(filepath=str(R/row['arquivo'])); o=bpy.context.selected_objects[0]; o.name=row['objeto']; o['code']=row['codigo']; o['center']=row['centro']; items.append(o)
 code=row['codigo']; col=(.25,.37,.47)
 if code in ['P03','P04','P05','P06']: col=(.70,.77,.81)
 elif code=='P11': col=(.72,.28,.22)
 elif code in ['P13','P14','P24']: col=(.17,.48,.53)
 elif code in ['P15','P16','P17','P18','P20','P21','P22','P23']: col=(.61,.37,.24)
 elif code in ['RaspberryPi5','L298N','MPU6050']: col=(.18,.42,.29)
 elif code=='Mecanica_04': col=(.58,.62,.65)
 mat=bpy.data.materials.new(code); mat.use_nodes=True; bs=mat.node_tree.nodes['Principled BSDF']; bs.inputs['Base Color'].default_value=(*col,1); bs.inputs['Roughness'].default_value=.6; o.data.materials.append(mat)
bpy.ops.object.camera_add(); cam=bpy.context.object; cam.data.type='ORTHO'; cam.data.clip_end=5000; S.camera=cam
anchor_override={'P01':(84,50,85),'P02':(84,165,85),'P03':(-50,65,136),'P04':(50,65,136),'P05':(-50,166,136),'P06':(50,166,136),'P12':(-45,115,90),'P13':(-50,140,50.8),'P14':(-25,40,50.4),'P19':(0,100,143)}
stages=[
 ('base',['Mecanica_04','P13','P14','P15','P16','P17','P22','P23','L298N','MPU6050'],['P13','P14','P15','P16','P17','P22','P23']),
 ('saia',['Mecanica_04','P01','P02','P11'],['P01','P02','P11']),
 ('modulo',['P12','P18','P19','P20','P21','P24','RaspberryPi5'],['P12','P18','P19','P20','P21','P24']),
 ('piso',['Mecanica_04','P01','P02','P11','P12','P15','P16','P17'],['P01','P02','P12','P15','P16','P17']),
 ('tetos',['P03','P04','P05','P06','P10'],['P03','P04','P05','P06','P10']),
 ('fechado-frente',['P01','P02','P03','P04','P05','P06','P07','P08','P09','P18','P19','P20','LidarC1'],['P07','P09']),
 ('fechado-tras',['P01','P02','P03','P04','P05','P06','P07','P08','P09','P18','P19','P20','LidarC1'],['P08','P09'])]
reports=[]
for name,visible,labels in stages:
 for o in items:
  code=o['code']; o.hide_render=code not in visible; o.location=(0,0,0)
  if name=='base' and code in ['L298N','MPU6050']: o.location.z=12
  if name=='saia':
   if code=='P01': o.location.y=-22
   if code=='P02': o.location.y=22
   if code=='P11': o.location.z=15
  if name=='modulo':
   if code=='RaspberryPi5': o.location.z=14
   if code=='P19': o.location.z=12
   if code=='P20': o.location.z=22
  if name=='piso' and code=='P12': o.location.z=48
  if name=='tetos':
   if code in ['P03','P05']: o.location.x=-30
   if code in ['P04','P06']: o.location.x=30
   if code in ['P03','P04']: o.location.y=-18
   if code in ['P05','P06']: o.location.y=18
   if code=='P10': o.location.x=38 if o['center'][0]<0 else -38; o.location.z=-20
 bpy.context.view_layer.update()
 shown=[o for o in items if not o.hide_render]; points=[o.matrix_world@Vector(v) for o in shown for v in o.bound_box]
 lo=Vector(tuple(min(p[i] for p in points) for i in range(3))); hi=Vector(tuple(max(p[i] for p in points) for i in range(3))); center=(lo+hi)/2
 direction=Vector((400,510,360) if name=='fechado-tras' else (400,-510,420)).normalized(); cam.location=center+direction*700; cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
 rot=cam.rotation_euler.to_matrix(); right=rot@Vector((1,0,0)); up=rot@Vector((0,1,0)); xx=[(p-center).dot(right) for p in points]; yy=[(p-center).dot(up) for p in points]; cam.data.ortho_scale=max(max(xx)-min(xx),(max(yy)-min(yy))*1400/1100)*1.34
 bpy.context.view_layer.update(); S.render.filepath=str(OUT/(name+'.png')); bpy.ops.render.render(write_still=True)
 anchors=[]
 for code in labels:
  o=next(o for o in shown if o['code']==code); point=Vector(anchor_override.get(code,o['center']))+o.location; p=world_to_camera_view(S,cam,point)
  anchors.append({'codigo':code,'pixel':[p.x*1400,(1-p.y)*1100]})
 reports.append({'arquivo':name+'.png','rotulos':anchors,'nota':'Afastamentos ilustrativos; não são posições de operação nem prova de trajetória de montagem.'})
(R/'figuras-report.json').write_text(json.dumps({'sha256_FCStd':data['sha256_FCStd'],'figuras':reports},ensure_ascii=False,indent=2)+'\n')
