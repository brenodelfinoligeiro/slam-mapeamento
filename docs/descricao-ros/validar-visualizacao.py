"""Abre RViz real sob Xvfb e captura a tela; só usar no contêiner isolado de ensaio."""
from pathlib import Path
import sys,subprocess,signal,time,json,os,socket,runpy
from PyQt5.QtGui import QGuiApplication
OUT=Path(sys.argv[1]);OUT.mkdir(parents=True,exist_ok=True);log=(OUT/'rviz.log').open('w')
os.environ['DISPLAY']=':97'
xlog=(OUT/'xvfb.log').open('w')
xserver=subprocess.Popen(['Xvfb',':97','-screen','0','1280x900x24','-nolisten','tcp','-ac'],stdout=xlog,stderr=subprocess.STDOUT,start_new_session=True)
ready=False
for _ in range(100):
    if xserver.poll() is not None: raise RuntimeError('Xvfb terminou antes de aceitar cliente')
    try:
        with socket.socket(socket.AF_UNIX) as conn: conn.connect('/tmp/.X11-unix/X97')
        ready=True
        break
    except OSError: time.sleep(.1)
if not ready:
    xserver.terminate();xserver.wait(timeout=5)
    raise TimeoutError('Xvfb sem prontidao em 10 segundos')

proc=subprocess.Popen(['ros2','launch','robo_movel','visualizar.launch.py','gui:=false'],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
app=QGuiApplication([])
try:
 for i in range(30):
  app.processEvents();time.sleep(1)
  if proc.poll() is not None:raise RuntimeError('RViz/launch terminou antes da captura')
  if i in (12,24):
   screen=app.primaryScreen();assert screen is not None
   assert screen.grabWindow(0).save(str(OUT/f'rviz-{i:02d}.png'))
 text=(OUT/'rviz.log').read_text()
 assert 'rviz2' in text and 'OpenGl' in text,text
 errors=[line for line in text.splitlines() if any(s in line.lower() for s in ['could not load resource','could not load mesh','error retrieving file','failed to load','[error]','process has died'])]
 assert not errors,errors
 runpy.run_path(str(Path(__file__).with_name('fechar-rviz.py')))['fechar_rviz']()
 fechado=False
 for _ in range(50):
  app.processEvents();time.sleep(.1)
  if any('rviz2-' in line and 'process has finished cleanly' in line for line in (OUT/'rviz.log').read_text().splitlines()): fechado=True;break
 assert fechado,'RViz não encerrou pela janela no prazo de 5 segundos'
 resultado={'status':'OK','capturas':['rviz-12.png','rviz-24.png'],'rviz_real':True,'inspecao_visual_pendente':True}
finally:
 if proc.poll() is None:proc.send_signal(signal.SIGINT)
 try:proc.wait(timeout=15)
 except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGTERM);proc.wait(timeout=5)
 log.close()
 if xserver.poll() is None: xserver.terminate()
 xserver.wait(timeout=5);xlog.close()
text=(OUT/'rviz.log').read_text()
assert proc.returncode==0,proc.returncode
assert '[ERROR]' not in text and 'Traceback' not in text,text
resultado['encerramento_limpo']=True
(OUT/'validacao-rviz.json').write_text(json.dumps(resultado,indent=2)+'\n')
print(json.dumps(resultado))
