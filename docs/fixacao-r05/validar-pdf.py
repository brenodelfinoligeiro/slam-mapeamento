"""Reabrir PDF R05, auditar fichas/textos e rasterizar todas as paginas para QC."""
from pathlib import Path
import json,sys,hashlib,subprocess,math
from pypdf import PdfReader
import pypdfium2 as pdfium
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent; OUT=Path(sys.argv[1]);OUT.mkdir(parents=True,exist_ok=True)
K=json.loads((R/'kit-r05.json').read_text());M=json.loads((R/'manifesto-vistas.json').read_text());G=json.loads((R/'roteiro-montagem-r05.json').read_text()); V=json.loads((R/'validacao-manual-seis-vistas.json').read_text())
f=R/'slamderson-r05-montagem-e-seis-vistas.pdf';d=PdfReader(f);guide=len(G['paginas']);assert len(d.pages)==guide+len(M['pecas'])==V['paginas']
labels=['SUPERIOR (+Z)','FRONTAL (-Y)','DIREITA (+X)','INFERIOR (-Z)','TRASEIRA (+Y)','ESQUERDA (-X)']; texts=[];sheets=[]
for i,p in enumerate(d.pages):
 t=p.extract_text();assert t and '\x00' not in t and '\ufffd' not in t,(i,'caractere ausente');texts.append(t)
 assert abs(float(p.mediabox.width)-841.8898)<.05 and abs(float(p.mediabox.height)-595.2756)<.05
 if i>=guide:
  row=M['pecas'][i-guide]; assert row['codigo'] in t and row['arquivo_zip'] in t
  assert all(q in t for q in labels),(i,'vista faltante');assert len(p.images)==6,(i,'imagens',len(p.images))
  sheets.append({'pagina':i+1,'codigo':row['codigo'],'imagens':len(p.images),'vistas':labels})
assert len({p['codigo'] for p in sheets})==len(K['pecas'])
assert '68 insertos' in texts[3] and '4,3' in texts[5] and '6 mm' in texts[5]
assert 'INFERIORES' in texts[7] and 'SUPERIORES' in texts[10]
assert 'BAIXO' in texts[9] and 'ELEVAR 2 mm' in texts[10]
assert 'módulo superior/teto desmontado' in texts[11]
(OUT/'texto-por-pagina.json').write_text(json.dumps(texts,ensure_ascii=False,indent=2)+'\n')
fontpath=subprocess.check_output(['fc-match','-f','%{file}','DejaVu Sans:style=Bold'],text=True).strip();font=ImageFont.truetype(fontpath,19)
render=pdfium.PdfDocument(str(f));thumbs=[]
for i in range(len(render)):
 page=render[i];im=page.render(scale=1.6).to_pil().convert('RGB');im.save(OUT/f'pagina-{i+1:02d}.png');im.thumbnail((440,312))
 thumb=Image.new('RGB',(460,346),'#dbe3eb');thumb.paste(im,((460-im.width)//2,24));ImageDraw.Draw(thumb).text((12,2),f'Pagina {i+1:02d}',font=font,fill='#20394c');thumbs.append(thumb);page.close()
contacts=[]
for batch in range(math.ceil(len(thumbs)/14)):
 ts=thumbs[batch*14:(batch+1)*14];sheet=Image.new('RGB',(460*3,346*math.ceil(len(ts)/3)),'white')
 for n,im in enumerate(ts):sheet.paste(im,((n%3)*460,(n//3)*346))
 p=OUT/f'contato-{batch+1}.jpg';sheet.save(p,quality=92);contacts.append(str(p))
report={'status':'OK','paginas':len(d.pages),'paginas_guia':guide,'fichas_unicas':len(sheets),'vistas':6*len(sheets),'paginas_rasterizadas':len(render),'sha256_pdf':hashlib.sha256(f.read_bytes()).hexdigest(),'sha256_zip':M['sha256_zip'],'fichas':sheets,'contatos':contacts,'limites':'Auditoria documental e renderizacao; nao comprova montagem fisica.'}
(R/'validacao-pdf-r05.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='fichas'},ensure_ascii=False))
