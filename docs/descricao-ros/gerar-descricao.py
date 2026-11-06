"""Gera URDF/malhas de visualização em metros a partir da extração CAD R05.
Uso: uv run --with trimesh --with numpy --with fast-simplification --with pyyaml python gerar-descricao.py CACHE_CAD
Não altera CAD/STL de impressão. Não estima massas, contato ou calibração de sensores.
"""
from pathlib import Path
import sys,json,hashlib,math
import xml.etree.ElementTree as ET
import numpy as np
import trimesh
import yaml
ROOT=Path(__file__).resolve().parents[2];CACHE=Path(sys.argv[1]);PKG=ROOT/'src/descricao/robo_movel';OUT=PKG/'descricao';MALHAS=OUT/'malhas';MALHAS.mkdir(parents=True,exist_ok=True)
meta=json.loads((CACHE/'exportacao-cad.json').read_text());assert meta['revisao']=='R05'
registro=json.loads((ROOT/meta['registro_origem']).read_text());assert hashlib.sha256((ROOT/registro['arquivo']).read_bytes()).hexdigest()==meta['sha256_CAD']==registro['sha256_CAD']
R=np.asarray(meta['rotacao_CAD_para_ROS']);base=np.asarray(meta['origem_base_CAD_mm']);frames=meta['frames_CAD_mm']
def deslocamento(nome):return (R@(np.asarray(frames[nome])-base)*.001).tolist()
def numeros(v):return ' '.join(format(float(x),'.12g') for x in v)
robo=ET.Element('robot',{'name':'robo_movel'})
robo.append(ET.Comment('Derivado do CAD R05; metros; datums de montagem não substituem calibração física. Sem inércias inventadas.'))
colors={'estrutura':'.22 .34 .44 1','metal':'.64 .68 .72 1','motores':'.88 .68 .12 1','placas':'.14 .43 .25 1','reserva':'.60 .35 .70 .35','pilhas':'.68 .41 .15 1','bateria':'.12 .13 .16 1','pneu':'.045 .05 .06 1','cubo':'.72 .64 .25 1','disco':'.12 .13 .16 1','sensor':'.13 .16 .20 1'}
for name,color in colors.items():ET.SubElement(ET.SubElement(robo,'material',{'name':name}),'color',{'rgba':color})
links={name:ET.SubElement(robo,'link',{'name':name}) for name in ['base_footprint',*frames]}
def junta(nome,tipo,pai,filho,xyz):
 j=ET.SubElement(robo,'joint',{'name':nome,'type':tipo});ET.SubElement(j,'parent',{'link':pai});ET.SubElement(j,'child',{'link':filho});ET.SubElement(j,'origin',{'xyz':numeros(xyz),'rpy':'0 0 0'})
 if tipo=='continuous':ET.SubElement(j,'axis',{'xyz':'0 1 0'})
 return j
junta('base_footprint_joint','fixed','base_footprint','base_link',[0,0,meta['altura_base_m']])
for name in frames:
 if name=='base_link':continue
 joint={'left_wheel_link':'left_wheel_joint','right_wheel_link':'right_wheel_joint'}.get(name,name.removesuffix('_link')+'_joint')
 junta(joint,'continuous' if name in ('left_wheel_link','right_wheel_link') else 'fixed','base_link',name,deslocamento(name))
meshes=[];global_bounds=[]
for g in meta['grupos']:
 m=trimesh.load_mesh(CACHE/g['arquivo'],process=False);assert len(m.faces)>0 and np.isfinite(m.vertices).all();before=m.bounds.copy();count=len(m.faces)
 target=g['limite_visual_triangulos']
 if g['nome']=='lidar':target=30000
 if g['nome']=='ferragens':target=40000
 if target and count>target:
  requested=target
  while True:
   reduced=m.simplify_quadric_decimation(face_count=requested,aggression=4)
   erro=float(np.max(np.abs(reduced.bounds-before)))
   if erro<=.0005: m=reduced;break
   requested=min(count,requested*2)
   if requested==count:break
 path=MALHAS/(g['nome']+'_r05.stl');m.export(path,file_type='stl');check=trimesh.load_mesh(path,process=False)
 assert np.isfinite(check.vertices).all() and len(check.faces)>0 and max(check.extents)<.5
 error=float(np.max(np.abs(check.bounds-before)));assert error<=.00051,(g['nome'],error)
 uri='package://robo_movel/descricao/malhas/'+path.name
 v=ET.SubElement(links[g['link']],'visual',{'name':g['nome']});ET.SubElement(v,'origin',{'xyz':'0 0 0','rpy':'0 0 0'});geo=ET.SubElement(v,'geometry');ET.SubElement(geo,'mesh',{'filename':uri,'scale':'1 1 1'});ET.SubElement(v,'material',{'name':g['material']})
 # Malhas de colisão estática: geometria de referência, sem aprovação de contato/dinâmica.
 if g['nome'] in ('estrutura','chassi','rodizio'):
  c=ET.SubElement(links[g['link']],'collision',{'name':g['nome']});ET.SubElement(c,'origin',{'xyz':'0 0 0','rpy':'0 0 0'});ET.SubElement(ET.SubElement(c,'geometry'),'mesh',{'filename':uri,'scale':'1 1 1'})
 g2={k:v for k,v in g.items() if k!='arquivo'};g2.update({'arquivo':'descricao/malhas/'+path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'triangulos_exportados':len(check.faces),'erro_max_bbox_m':error,'bbox_exportado_m':check.bounds.tolist()});meshes.append(g2)
 off=np.asarray(deslocamento(g['link']));global_bounds.append(before+off)
 print(g['nome'],count,'->',len(check.faces),'erro_bbox_m',error,flush=True)
# Pneus e cubos: cilindros de aproximação, sem raio de rolamento medido.
for side in ('left','right'):
 link=side+'_wheel_link';origin=np.asarray(frames[link])
 for typ,source in [('pneu',meta['pneus_bbox_CAD_mm'][side]),('cubo',meta['cubos_bbox_CAD_mm'][side])]:
  b=np.asarray(source);center=(b[:3]+b[3:])/2;off=R@(center-origin)*.001;dims=(b[3:]-b[:3])*.001
  c=ET.SubElement(links[link],'collision',{'name':typ});ET.SubElement(c,'origin',{'xyz':numeros(off),'rpy':numeros([math.pi/2,0,0])});ET.SubElement(ET.SubElement(c,'geometry'),'cylinder',{'radius':format(max(dims[1:])/2,'.12g'),'length':format(dims[0],'.12g')})
ET.indent(robo,space='  ');OUT.mkdir(exist_ok=True);ET.ElementTree(robo).write(OUT/'robo_movel.urdf',encoding='utf-8',xml_declaration=True)
lo=np.min([b[0] for b in global_bounds],axis=0);hi=np.max([b[1] for b in global_bounds],axis=0);foot=[[float(x),float(y)] for x,y in [(lo[0],lo[1]),(hi[0],lo[1]),(hi[0],hi[1]),(lo[0],hi[1])]]
meta.pop('grupos');meta['meshes']=meshes;meta['juntas_moveis']=['left_wheel_joint','right_wheel_joint'];meta['frames_ROS_relativos_base_m']={n:deslocamento(n) for n in frames};meta['bbox_ROS_relativa_base_m']=[lo.tolist(),hi.tolist()];meta['footprint_retangular_conservador_m']=foot;meta['colisoes']='Malhas estáticas e cilindros aproximados. Não é modelo validado para dinâmica/Gazebo.';meta['sha256_urdf']=hashlib.sha256((OUT/'robo_movel.urdf').read_bytes()).hexdigest()
(OUT/'origem-cad.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
config={'origem':'CAD R05; não são medidas físicas/calibração','unidade':'m','calibrado':False,'distancia_entre_rodas':meta['distancia_rodas_m'],'raio_vertical_referencia':meta['raio_vertical_roda_m'],'footprint_retangular_referencia':foot,'sensor_frames_de_dados':{'imu':'pendente: datum imu_mount_link não define eixos do dado bruto','lidar':'pendente: datum lidar_mount_link não é o plano óptico laser'},'rodizio_acima_plano_rodas_mm':meta['rodizio_acima_plano_rodas_mm']}
(PKG/'configuracao/geometria_cad.yaml').write_text(yaml.safe_dump(config,allow_unicode=True,sort_keys=False))
print(json.dumps({'links':len(links),'juntas':len(robo.findall('joint')),'malhas':len(meshes),'triangulos':sum(g['triangulos_exportados'] for g in meshes),'rodizio_acima_mm':meta['rodizio_acima_plano_rodas_mm']},ensure_ascii=False))
