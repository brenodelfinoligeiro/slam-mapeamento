"""Guia de montagem + 24 fichas com seis vistas por página, sem alterar STL.
Uso: python gerar-manual-seis-vistas.py PASTA_ASSETS
"""
from pathlib import Path
import sys,json,io,hashlib,subprocess,collections
from xml.sax.saxutils import escape
from PIL import Image,ImageDraw,ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4,landscape
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph,Table,TableStyle
from reportlab.lib.styles import ParagraphStyle
R=Path(__file__).resolve().parent; AS=Path(sys.argv[1])
K=json.loads((R/'kit-r04.json').read_text()); M=json.loads((R/'manifesto-vistas.json').read_text()); A=json.loads((AS/'render-report-seis.json').read_text()); G=json.loads((R/'roteiro-montagem-r04.json').read_text()); F=json.loads((AS/'sceneManual/figuras-report.json').read_text())
assert len(M['pecas'])==len(A['pecas'])==24 and len(G['paginas'])==10 and len(F['figuras'])==7
assert hashlib.sha256((R/M['arquivo_origem']).read_bytes()).hexdigest()==M['sha256_zip']
assert hashlib.sha256((R/'slamderson-impressao-r04.FCStd').read_bytes()).hexdigest()==F['sha256_FCStd']
assert json.loads((R/'validacao-montagem-r04.json').read_text())['status']=='OK'
for name,pat in [('Regular','DejaVu Sans'),('Bold','DejaVu Sans:style=Bold')]:
 font=subprocess.check_output(['fc-match','-f','%{file}',pat],text=True).strip(); pdfmetrics.registerFont(TTFont(name,font))
pilfont=ImageFont.truetype(subprocess.check_output(['fc-match','-f','%{file}','DejaVu Sans:style=Bold'],text=True).strip(),34)
BLUE=colors.HexColor('#20394c'); GREY=colors.HexColor('#586b79'); LINE=colors.HexColor('#d6dfe5'); ORANGE=colors.HexColor('#8c3d18')
W,H=landscape(A4); total=len(G['paginas'])+len(M['pecas']); OUT=R/'slamderson-r04-montagem-e-seis-vistas.pdf'
c=canvas.Canvas(str(OUT),pagesize=(W,H),pageCompression=1); c.setTitle('Slamderson R04 — montagem e seis vistas por peça'); c.setAuthor('Projeto Slamderson')
BASE=ParagraphStyle('base',fontName='Regular',fontSize=9.7,leading=13.1,textColor=BLUE)
layout=[]; images=[]; sheets=[]

def text(x,y,t,size=10,bold=False,color=BLUE):
 c.setFillColor(color); c.setFont('Bold' if bold else 'Regular',size); c.drawString(x*mm,y*mm,t)
def para(x,y,w,t,size=9.7,bold=False,color=BLUE,markup=False):
 st=ParagraphStyle('temp',parent=BASE,fontName='Bold' if bold else 'Regular',fontSize=size,leading=size*1.35,textColor=color)
 pp=Paragraph(t if markup else escape(t),st); _,h=pp.wrap(w*mm,170*mm); bottom=y-h/mm
 assert x>=9 and x+w<=288 and bottom>=12,(current,t[:60],bottom)
 pp.drawOn(c,x*mm,bottom*mm); layout.append({'pagina':current,'tipo':'texto','bbox_mm':[x,bottom,x+w,y]}); return bottom

def header(title,subtitle='',kind='MONTAGEM'):
 text(12,200,'SLAMDERSON / R04 — '+kind,9,True,color=GREY)
 assert pdfmetrics.stringWidth(title,'Bold',16)<273*mm,title
 text(12,190,title,16,True)
 if subtitle: para(12,183,273,subtitle,8.8,color=GREY)
 c.setStrokeColor(LINE); c.line(12*mm,174*mm,285*mm,174*mm)
def footer():
 text(12,6,'Estudo R04: conferir hardware real; figuras explodidas não são poses de operação.',7.2,color=GREY)
 c.setFont('Regular',8); c.drawRightString(285*mm,6*mm,f'{current:02d} / {total}')
def jpeg(im):
 bg=Image.new('RGB',im.size,'white')
 if im.mode=='RGBA': bg.paste(im,mask=im.getchannel('A'))
 else: bg.paste(im.convert('RGB'))
 b=io.BytesIO(); bg.save(b,format='JPEG',quality=93,subsampling=0,optimize=True); b.seek(0); return ImageReader(b)
def pic(im,x,y,w,h):
 iw,ih=im.size; factor=min(w/iw,h/ih); dw=iw*factor; dh=ih*factor
 c.drawImage(jpeg(im),(x+(w-dw)/2)*mm,(y+(h-dh)/2)*mm,dw*mm,dh*mm)
 images.append({'pagina':current,'bbox_mm':[x,y,x+w,y+h]})

def annotate(row):
 original=Image.open(AS/'sceneManual/figuras'/row['arquivo']).convert('RGBA'); out=Image.new('RGBA',(1720,1100),'white'); out.alpha_composite(original,(160,0)); d=ImageDraw.Draw(out)
 cols=[[],[]]
 for a in row['rotulos']: cols[0 if a['pixel'][0]<700 else 1].append(a)
 qty={p['codigo']:p['quantidade'] for p in K['pecas']}
 for side,items in enumerate(cols):
  items.sort(key=lambda a:a['pixel'][1]); ys=[]
  for a in items: ys.append(max(70,min(1000,a['pixel'][1]),ys[-1]+78 if ys else 70))
  if ys and ys[-1]>1020: ys=[y-(ys[-1]-1020) for y in ys]
  for a,y in zip(items,ys):
   code=a['codigo']; label=code+(' x'+str(qty[code]) if qty[code]>1 else '')
   x=12 if side==0 else 1570; endx=143 if side==0 else 1554; px,py=a['pixel']; px+=160
   d.line([(endx,y+19),(150 if side==0 else 1560,y+19),(px,py)],fill='#294b60',width=3); d.ellipse((px-5,py-5,px+5,py+5),fill='#294b60')
   bb=d.textbbox((x,y),label,font=pilfont); d.rectangle((bb[0]-3,bb[1]-3,bb[2]+3,bb[3]+3),fill='white'); d.text((x,y),label,font=pilfont,fill='#20394c')
 return out
figures={f['arquivo']:annotate(f) for f in F['figuras']}
(AS/'anotadas').mkdir(exist_ok=True)
for name,im in figures.items(): im.convert('RGB').save(AS/'anotadas'/name)

def table_at(rows,widths,y,fontsize=9,rowheight=None):
 style=ParagraphStyle('table',parent=BASE,fontSize=fontsize,leading=fontsize*1.18)
 cells=[[Paragraph(escape(str(v)),style) for v in row] for row in rows]
 tb=Table(cells,colWidths=[v*mm for v in widths],rowHeights=None if rowheight is None else [rowheight*mm]*len(rows))
 tb.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e4edf2')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LINEBELOW',(0,0),(-1,0),.6,LINE),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f6f8fa')]),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3)]))
 tw,th=tb.wrap(273*mm,160*mm); bottom=y-th/mm; assert bottom>=16,(current,bottom)
 tb.drawOn(c,12*mm,bottom*mm); layout.append({'pagina':current,'tipo':'tabela','bbox_mm':[12,bottom,12+sum(widths),y]}); return bottom

def alert(y,t,x=165,w=120):
 end=para(x+3,y-4,w-6,'PARE / CONFIRA',9.3,True,ORANGE); end=para(x+3,end-2,w-6,t,9.0,color=ORANGE)
 c.setStrokeColor(colors.HexColor('#e0b69e')); c.setLineWidth(.7); c.rect(x*mm,(end-3)*mm,w*mm,(y-end+3)*mm)
 assert end-3>=12,(current,'alerta',end)
 return end-3

groups=collections.defaultdict(list)
for j in K['parafusos']: groups[j['grupo']].append(j)
where={'A':'P11 / saia e tampas: 4 inferiores + 4 superiores','B':'P01 / P02: uma união por lateral','C':'P03-P05 e P04-P06: uma união lateral por metade','D':'P10 sob o teto: dois parafusos por ponte','E':'P07: acesso frontal às AA','F':'P08: acesso traseiro ao Basike','G':'P09: painel lateral de serviço do Basike','H':'P12 / orelhas da saia; não são os furos das colunas','I':'Chassi / P15-P16-P17 / P12; interface física pendente','J':'P19 / P18 / P12; NÃO entra no sensor C1','K':'Pi / P21 / P12; usar M2.5, não M3','L':'P13 / chassi; cabeça abaixo do apoio do Basike','M':'P14 / chassi; cabeça abaixo do apoio do holder','N':'L298N / P22 / chassi; conferir módulo real','O':'MPU / P23 / chassi; conferir módulo real','P':'P24 / P12; porcas sob o piso'}
assert set(groups)==set(where)
current=0
for g in G['paginas']:
 current+=1; header(g['titulo'],g.get('subtitulo',''))
 c.bookmarkPage(g['id']); c.addOutlineEntry(g['titulo'],g['id'],0,False)
 typ=g['tipo']
 if typ=='abertura':
  left=168; right=168
  for i,(title,body) in enumerate(g['blocos']):
   x=12 if i<3 else 154; y=left if i<3 else right
   y=para(x,y,131,title,11,True)-3; y=para(x,y,131,body,10)-7
   if i<3: left=y
   else: right=y
 elif typ=='inventario':
  rows=[['Código','Qtd.','Modelo','Envelope XYZ (mm)','Ficha / página']]
  for i,p in enumerate(M['pecas']):
   rr=next(q for q in K['pecas'] if q['codigo']==p['codigo']); dims=' x '.join(f'{v:.1f}'.replace('.',',') for v in rr['dimensoes_impressao_mm'])
   rows.append([p['codigo'],p['quantidade'],p['nome'],dims,f'{len(G["paginas"])+i+1:02d}'])
  bottom=table_at(rows,[16,13,122,72,50],168,8.8,5.65)
  para(12,bottom-4,273,'Quantidades somadas: '+str(sum(p['quantidade'] for p in M['pecas']))+' impressos. Não imprimir placas, pilhas, motores, rodas, chassi de referência ou as ferragens do CAD. O cupom P25 não faz parte do ZIP entregue.',8.6,color=GREY)
 elif typ=='ferragens':
  rows=[['Bitola','Comprimento','Cabeça','Qtd.']]
  for b in K['bom_parafusos']: rows.append([b['metrica'],str(b['comprimento_mm'])+' mm',b['cabeca'],b['quantidade']])
  bottom=table_at(rows,[43,51,141,38],168,10,7.1)
  nuts=collections.Counter(j['metrica'] for j in K['parafusos']); washers=collections.Counter()
  for j in K['parafusos']: washers[j['metrica']]+=int(j['arruela_cabeca'])+int(j['arruela_porca'])
  info=[('Porcas e arruelas do modelo',f'Porcas: {nuts["M3"]} M3 e {nuts["M2.5"]} M2.5. Arruelas: {washers["M3"]} M3 e {washers["M2.5"]} M2.5. Use isolantes nas interfaces das placas. O CAD representa arruelas de 0,5 mm; mudar a pilha exige conferir o comprimento e a saída da rosca.'),('Materiais e ferramentas','Chaves Allen compatíveis com as cabeças compradas, chave para as porcas, pinça e paquímetro. Duas cintas de velcro de 10 mm para o Basike; retenção/fitas do ESP e espuma isolante de 2 mm. Tamanho, material e caminho das cintas devem ser verificados fisicamente.'),('Atenção aos comprimentos','Allen: comprimento medido sob a cabeça. Escareado: inclui a cabeça. Não use ponta de parafuso contra bateria ou componente. Os 52 parafusos listados não incluem os quatro parafusos do C1, nem ferragens dos motores/encoders; esses pontos continuam pendentes.')]
  y=bottom-6
  for title,body in info:
   y=para(12,y,273,title,10,True)-2; y=para(12,y,273,body,9.3)-4
 elif typ=='mapa':
  rows=[['Grupo','Qtd.','Fixador','Aplicação']]
  for code,js in groups.items():
   j=js[0]; rows.append([code,len(js),j['metrica']+' x '+str(j['comprimento_mm'])+(' ESC' if j['cabeca'].startswith('escareada') else ''),where[code]])
  bottom=table_at(rows,[22,19,44,188],168,9.5,7.2)
  para(12,bottom-4,273,'ESC = cabeça escareada. Nas uniões com bolso sextavado, a porca é alojada no plástico; nos demais pontos, a porca fica livre do lado oposto. Carregue as porcas antes de fechar seu acesso. A matriz de furação do sensor C1 não foi liberada.',8.8,color=GREY)
 elif typ=='etapa':
  pic(figures[g['figura']],10,74,145,93); para(12,68,139,g['legenda'],8.7,color=GREY)
  y=168
  for i,t in enumerate(g['passos'],1): y=para(165,y,120,f'<b>{i}.</b> '+escape(t),9.6,markup=True)-3.5
  alert(y-1,g['alerta'])
 elif typ=='fechamento':
  pic(figures[g['figuras'][0]],10,104,145,68); text(12,172,'Frente: P07 / lateral: P09',8.5,True)
  pic(figures[g['figuras'][1]],10,28,145,68); text(12,97,'Traseira: P08 / lateral: P09',8.5,True)
  y=168
  for i,t in enumerate(g['passos'],1): y=para(165,y,120,f'<b>{i}.</b> '+escape(t),9.5,markup=True)-3.5
  alert(y-1,g['alerta'])
 footer(); c.showPage()

viewnames={'superior':('SUPERIOR (+Z)','X direita; Y cima'),'frontal':('FRONTAL (-Y)','X direita; Z cima'),'lateral':('DIREITA (+X)','Y direita; Z cima'),'inferior':('INFERIOR (-Z)','X direita; -Y cima'),'traseira':('TRASEIRA (+Y)','-X direita; Z cima'),'esquerda':('ESQUERDA (-X)','-Y direita; Z cima')}
order=['superior','frontal','lateral','inferior','traseira','esquerda']
for p,a in zip(M['pecas'],A['pecas']):
 current+=1; assert p['codigo']==a['codigo'] and p['sha256']==a['sha256'] and len(a['vistas'])==6
 title=p['codigo']+' — '+p['nome']; dims=' x '.join(f'{v:.1f}'.replace('.',',') for v in a['dimensoes_STL_mm'])
 header(title,'Modelo único | Qtd.: '+str(p['quantidade'])+' | Envelope STL XYZ: '+dims+' mm | Seis vistas nesta página','SEIS VISTAS')
 c.bookmarkPage(p['codigo']); c.addOutlineEntry(title,p['codigo'],0,False)
 for i,v in enumerate(order):
  x=12+(i%3)*93; y=108 if i<3 else 31; name=p['codigo']+'_'+v+'.png'; assert name in a['vistas']; image=Image.open(AS/'renders6'/name).convert('RGBA'); bb=image.getchannel('A').getbbox()
  assert bb and bb[0]>12 and bb[1]>12 and bb[2]<image.width-12 and bb[3]<image.height-12,(p['codigo'],v,bb)
  label,axes=viewnames[v]; text(x,y+60,label,9.7,True)
  c.setStrokeColor(LINE); c.setLineWidth(.4); c.rect(x*mm,y*mm,87*mm,58*mm)
  pic(image,x+.5,y+.5,86,57); text(x,y-4,axes,7.5,color=GREY)
 text(12,17,p['arquivo_zip'],8,color=GREY)
 text(12,11,'Referencial do STL de impressão. Escala automática, comum às seis vistas desta página; não é cotagem de fabricação.',7.5,color=GREY)
 footer(); sheets.append({'pagina':current,'codigo':p['codigo'],'arquivo_zip':p['arquivo_zip'],'sha256':p['sha256'],'vistas':[p['codigo']+'_'+v+'.png' for v in order]}); c.showPage()
assert current==total==34 and len(sheets)==24 and all(len(p['vistas'])==6 for p in sheets)
c.save()
report={'paginas':current,'paginas_montagem':len(G['paginas']),'modelos_unicos':len(sheets),'vistas_ortograficas':sum(len(p['vistas']) for p in sheets),'imagens_montagem':len(F['figuras']),'sha256_zip':M['sha256_zip'],'sha256_FCStd':F['sha256_FCStd'],'sha256_pdf':hashlib.sha256(OUT.read_bytes()).hexdigest(),'bytes_pdf':OUT.stat().st_size,'fichas':sheets,'boxes':layout,'imagens_na_pagina':images,'limites':G['escopo']}
(R/'validacao-manual-seis-vistas.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['paginas','paginas_montagem','modelos_unicos','vistas_ortograficas','imagens_montagem','bytes_pdf']},ensure_ascii=False))
