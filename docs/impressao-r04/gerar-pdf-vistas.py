"""PDF de 24 modelos / 72 vistas derivadas dos STL do ZIP entregue.
Uso: python gerar-pdf-vistas.py PASTA_DOS_RENDERS (render-report.json + renders/).
"""
from pathlib import Path
import sys,json,io,hashlib,subprocess
from PIL import Image,ImageOps
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from xml.sax.saxutils import escape
R=Path(__file__).resolve().parent; ASSETS=Path(sys.argv[1])
M=json.loads((R/'manifesto-vistas.json').read_text()); A=json.loads((ASSETS/'render-report.json').read_text())
assert len(M['pecas'])==len(A['pecas'])==24
assert len({p['codigo'] for p in M['pecas']})==24
for name,pattern in [('Regular','DejaVu Sans'),('Bold','DejaVu Sans:style=Bold')]:
 f=subprocess.check_output(['fc-match','-f','%{file}',pattern],text=True).strip(); pdfmetrics.registerFont(TTFont(name,f))
W,H=A4; BLUE=colors.HexColor('#20394c'); GREY=colors.HexColor('#627281'); LINE=colors.HexColor('#d3dce3')
OUT=R/'slamderson-r04-24-pecas-tres-vistas.pdf'
c=canvas.Canvas(str(OUT),pagesize=A4,pageCompression=1)
c.setTitle('Slamderson R04 — três vistas de cada peça'); c.setAuthor('Projeto Slamderson'); c.setSubject('24 modelos únicos dos STL entregues; 72 projeções ortográficas')
style=ParagraphStyle('notas',fontName='Regular',fontSize=8.1,leading=11,textColor=GREY)
files=[]; checked=[]

def text(x,y,t,size=10,bold=False,color=BLUE):
 c.setFillColor(color); c.setFont('Bold' if bold else 'Regular',size); c.drawString(x*mm,y*mm,t)
def paragraph(x,y,width,txt,size=8.1):
 st=ParagraphStyle('p',parent=style,fontSize=size,leading=size*1.35)
 p=Paragraph(escape(txt),st); w,h=p.wrap(width*mm,100*mm); p.drawOn(c,x*mm,y*mm-h)
 return h/mm

def view(path,x,y,title,axes):
 im=Image.open(path).convert('RGBA'); alpha=im.getchannel('A'); bbox=alpha.getbbox(); assert bbox is not None,path.name
 assert bbox[0]>12 and bbox[1]>12 and bbox[2]<im.width-12 and bbox[3]<im.height-12,(path.name,bbox)
 bg=Image.new('RGB',im.size,'white'); bg.paste(im,mask=alpha)
 buf=io.BytesIO(); bg.save(buf,format='JPEG',quality=93,subsampling=0,optimize=True); buf.seek(0)
 text(x,y+92,title,10,True)
 c.setStrokeColor(LINE); c.setLineWidth(.45); c.rect(x*mm,y*mm,88*mm,88*mm)
 c.drawImage(ImageReader(buf),(x+.4)*mm,(y+.4)*mm,87.2*mm,87.2*mm)
 text(x,y-5,axes,8,color=GREY)
 checked.append({'arquivo':path.name,'alpha_bbox':bbox,'pixels':[im.width,im.height]})

for idx,(p,a) in enumerate(zip(M['pecas'],A['pecas']),1):
 assert p['codigo']==a['codigo'] and p['sha256']==a['sha256']
 assert len(a['vistas'])==3
 text(12,282,'SLAMDERSON / R04',10,True,color=GREY)
 title=p['codigo']+' — '+p['nome']
 assert pdfmetrics.stringWidth(title,'Bold',16)<186*mm
 text(12,271,title,16,True)
 c.setStrokeColor(LINE); c.line(12*mm,265*mm,198*mm,265*mm)
 view(ASSETS/'renders'/a['vistas'][0],12,160,'SUPERIOR  (+Z)','+X : direita  |  +Y : cima')
 view(ASSETS/'renders'/a['vistas'][1],12,46,'FRONTAL  (−Y)','+X : direita  |  +Z : cima')
 view(ASSETS/'renders'/a['vistas'][2],110,46,'LATERAL DIREITA  (+X)','+Y : direita  |  +Z : cima')
 text(110,246,'MODELO ÚNICO',10,True,color=GREY)
 text(110,235,'Quantidade no kit: '+str(p['quantidade']),13,True)
 text(110,221,'Envelope do STL (mm)',10,True)
 for i,(axis,d) in enumerate(zip('XYZ',a['dimensoes_STL_mm'])):
  text(113,211-i*8,axis+' = '+f'{d:.1f}'.replace('.',','),12)
 paragraph(110,177,86,'Orientação do STL de impressão. Escala de apresentação automática, igual nas três vistas desta página e variável entre peças.',8.3)
 text(12,29,p['arquivo_zip'],8.5,color=GREY)
 paragraph(12,23,186,'Projeções no referencial do arquivo, não nas direções do robô montado. Sem escala 1:1 ou cotagem completa de fabricação. Encaixe físico não ensaiado.',8)
 text(12,7,'Fonte: ZIP STL R04  |  SHA-256 da peça: '+p['sha256'][:16],7,color=GREY)
 c.setFont('Regular',8); c.drawRightString(198*mm,7*mm,f'{idx:02d} / 24')
 c.bookmarkPage(p['codigo']); c.addOutlineEntry(title,p['codigo'],0,False)
 files.append({'pagina':idx,'codigo':p['codigo'],'nome':p['nome'],'arquivo_zip':p['arquivo_zip'],'sha256':p['sha256'],'vistas':a['vistas']})
 c.showPage()
c.save()
assert len(checked)==72
report={'paginas':len(files),'modelos_unicos':len({p['codigo'] for p in files}),'vistas':len(checked),'sha256_zip_origem':M['sha256_zip'],'sha256_pdf':hashlib.sha256(OUT.read_bytes()).hexdigest(),'bytes_pdf':OUT.stat().st_size,'paginas_modelos':files,'imagens_conferidas':checked,'limites':'Projeções do STL, não desenho de fabricação completo ou ensaio físico.'}
(R/'validacao-pdf-vistas.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['paginas','modelos_unicos','vistas','bytes_pdf','sha256_pdf']},ensure_ascii=False))
