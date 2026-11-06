"""Valida o RViz da simulação num Xvfb privado dentro do contêiner."""
from pathlib import Path
import json,os,runpy,signal,socket,subprocess,sys,time
from PyQt5.QtGui import QGuiApplication
import rclpy

PASTA=Path(sys.argv[1]);PASTA.mkdir(parents=True,exist_ok=True)
os.environ['DISPLAY']=':97'
os.environ['LIBGL_ALWAYS_SOFTWARE']='1'
log_x=(PASTA/'xvfb.log').open('w')
xserver=subprocess.Popen(['Xvfb',':97','-screen','0','1280x900x24','-nolisten','tcp','-ac'],stdout=log_x,stderr=subprocess.STDOUT)
log=(PASTA/'lancamento-rviz.log').open('w')
processo=None;sonda=None;resultado=None
try:
    pronto=False
    for _ in range(100):
        if xserver.poll() is not None:raise RuntimeError('Xvfb terminou antes da prontidão')
        try:
            with socket.socket(socket.AF_UNIX) as conexao:conexao.connect('/tmp/.X11-unix/X97')
            pronto=True;break
        except OSError:time.sleep(.1)
    if not pronto:raise TimeoutError('Xvfb não aceitou conexões em dez segundos')
    processo=subprocess.Popen(['ros2','launch','navegacao_simulada','simulacao.launch.py','rviz:=true'],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    classe=runpy.run_path(str(Path(__file__).with_name('validar-fluxo.py')))['Sonda']
    rclpy.init();sonda=classe();aplicacao=QGuiApplication([])
    sonda.esperar(lambda:sonda.contagens['/odom']>20 and sonda.contagens['/simulacao/referencia']>20,prazo=25.)
    sonda.girar(2.)
    sonda.dirigir(.18,0.,3.)
    sonda.dirigir(.16,.65,3.)
    sonda.enviar(0.,0.);sonda.girar(1.2)
    assert processo.poll() is None,'Launch terminou antes da captura'
    aplicacao.processEvents();tela=aplicacao.primaryScreen();assert tela is not None
    assert tela.grabWindow(0).save(str(PASTA/'previa-simulacao.png'))
    resultado={'rviz_real':True,'sensores_e_movimento_ativos':True,'captura':'previa-simulacao.png','inspecao_visual_pendente':True}
finally:
    if sonda is not None:sonda.destroy_node()
    if rclpy.ok():rclpy.shutdown()
    if processo is not None and processo.poll() is None:
        fechar=Path(__file__).parents[1]/'descricao-ros/fechar-rviz.py'
        runpy.run_path(str(fechar))['fechar_rviz']()
        fechado=False
        for _ in range(50):
            if 'rviz2-' in (PASTA/'lancamento-rviz.log').read_text() and any('rviz2-' in l and 'process has finished cleanly' in l for l in (PASTA/'lancamento-rviz.log').read_text().splitlines()):fechado=True;break
            time.sleep(.1)
        assert fechado,'RViz não encerrou pela janela'
        processo.send_signal(signal.SIGINT)
        try:processo.wait(timeout=20)
        except subprocess.TimeoutExpired:os.killpg(processo.pid,signal.SIGTERM);processo.wait(timeout=8)
    log.close()
    if xserver.poll() is None:xserver.terminate()
    xserver.wait(timeout=5);log_x.close()
assert processo is not None and processo.returncode==0
texto=(PASTA/'lancamento-rviz.log').read_text()
assert 'Traceback' not in texto and 'process has died' not in texto,texto
assert 'could not load mesh' not in texto.lower() and 'could not load resource' not in texto.lower(),texto
assert resultado is not None
resultado['encerramento_limpo']=True
(PASTA/'resultado-rviz.json').write_text(json.dumps(resultado,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(resultado,ensure_ascii=False))
