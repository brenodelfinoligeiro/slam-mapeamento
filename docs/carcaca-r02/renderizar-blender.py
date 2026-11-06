"""Renderizar a revisão R02 exportada do FreeCAD; nenhum CAD é modificado."""
import bpy,sys,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(sys.argv[sys.argv.index('--')+1])
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
S=bpy.context.scene; S.render.engine='CYCLES'; S.cycles.device='CPU'; S.cycles.samples=24; S.cycles.use_denoising=True
S.render.resolution_x=1600; S.render.resolution_y=1500; S.render.resolution_percentage=100; S.render.image_settings.file_format='PNG'
S.world.use_nodes=True; S.world.node_tree.nodes['Background'].inputs[0].default_value=(.8,.85,.91,1); S.world.node_tree.nodes['Background'].inputs[1].default_value=.45
S.view_settings.view_transform='AgX'
rows=json.loads((ROOT/'scene.json').read_text()); items=[]
for row in rows:
    bpy.ops.wm.ply_import(filepath=str(ROOT/row['file']))
    o=bpy.context.selected_objects[0]; o.name=row['source_object']; o['g']=row['group']; o['source_name']=row['source_object']; items.append(o)
    mat=bpy.data.materials.new(o.name); mat.use_nodes=True
    p=mat.node_tree.nodes['Principled BSDF']; p.inputs['Base Color'].default_value=(*row['color'],1); p.inputs['Roughness'].default_value=.4 if row['group'] in ('Tampas','CarcacaBase') else .52
    o.data.materials.append(mat)
bpy.ops.mesh.primitive_plane_add(size=4000,location=(0,100,-.3)); plane=bpy.context.object
mat=bpy.data.materials.new('Piso'); mat.diffuse_color=(.88,.9,.93,1); plane.data.materials.append(mat)
for loc,power,size in [((260,-270,460),2200000,300),((-280,40,320),1500000,260),((40,400,430),1900000,250)]:
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.data.energy=power; o.data.shape='DISK'; o.data.size=size; o.rotation_euler=(Vector((0,110,85))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(); cam=bpy.context.object; cam.data.type='ORTHO'; cam.data.clip_end=5000; S.camera=cam

def render(name,target,loc,scale):
    cam.location=loc; cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.ortho_scale=scale; S.render.filepath=str(ROOT/name); bpy.ops.render.render(write_still=True)
render('fechado.png',(0,106,87),(380,-490,345),315)
render('traseira.png',(0,106,87),(380,510,320),315)
# Interior ilustrativo: carcaça oculta e níveis separados para explicar a distribuição.
for o in items:
    if o['g'] in ('CarcacaBase','Tampas','Acessos'): o.hide_render=True
    elif o['g']=='Superior': o.location.z=50
    elif o['g']=='Lidar': o.location.z=90
render('interior.png',(0,107,123),(400,-520,410),380)
# Acesso: retirada lateral das duas metades e afastamento das portinholas.
for o in items:
    o.hide_render=False; o.location=(0,0,0); n=o['source_name']
    if n=='TampaEsquerda': o.location.x=-115
    elif n=='TampaDireita': o.location.x=115
    elif n=='PortinholaAA' or n.startswith('UniaoAA'): o.location.y=-40
    elif n=='PortinholaPB' or n.startswith('UniaoPB'): o.location.y=50
    elif n=='TampaServicoPB' or n.startswith('UniaoServicoPB'): o.location.x=40
    elif n.startswith('UniaoTampas'): o.hide_render=True
render('acesso.png',(0,107,87),(420,-540,420),520)
(ROOT/'render-r02.json').write_text(json.dumps({'blender':bpy.app.version_string,'engine':'CYCLES','samples':24,'meshes':len(items),'triangles':sum(r['triangles'] for r in rows),'files':['fechado.png','traseira.png','interior.png','acesso.png'],'note':'Derivado do FCStd reaberto. Interior e acesso são apresentações explicativas, não poses de operação.'},indent=2))
