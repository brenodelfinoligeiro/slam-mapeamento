"""Captura RViz real em Xvfb privado; somente no contêiner de ensaio."""
from pathlib import Path
import json,os,runpy,signal,socket,subprocess,sys,time
from PyQt5.QtGui import QGuiApplication
import rclpy


def confirmar_salvamento_instalado():
    """Confirma modal só no Xvfb privado; fonte /workspace continua somente leitura."""
    import ctypes as C
    assert os.environ.get('DISPLAY')==':97'
    x=C.CDLL('libX11.so.6');teste=C.CDLL('libXtst.so.6');D=C.c_void_p
    x.XOpenDisplay.argtypes=[C.c_char_p];x.XOpenDisplay.restype=D
    x.XStringToKeysym.argtypes=[C.c_char_p];x.XStringToKeysym.restype=C.c_ulong
    x.XKeysymToKeycode.argtypes=[D,C.c_ulong];x.XKeysymToKeycode.restype=C.c_ubyte
    x.XFlush.argtypes=[D];x.XCloseDisplay.argtypes=[D]
    teste.XTestFakeKeyEvent.argtypes=[D,C.c_uint,C.c_int,C.c_ulong]
    display=x.XOpenDisplay(None)
    if not display:raise RuntimeError('Sem Xvfb privado para confirmar modal')
    try:
        tecla=x.XKeysymToKeycode(display,x.XStringToKeysym(b'Return'));assert tecla
        assert teste.XTestFakeKeyEvent(display,tecla,1,0)
        assert teste.XTestFakeKeyEvent(display,tecla,0,0)
        x.XFlush(display)
    finally:x.XCloseDisplay(display)


PASTA=Path(sys.argv[1]);PASTA.mkdir(parents=True,exist_ok=True)
os.environ['DISPLAY']=':97';os.environ['LIBGL_ALWAYS_SOFTWARE']='1'
log_x=(PASTA/'xvfb.log').open('w')
xserver=subprocess.Popen(['Xvfb',':97','-screen','0','1280x900x24','-nolisten','tcp','-ac'],stdout=log_x,stderr=subprocess.STDOUT)
log=(PASTA/'lancamento-rviz.log').open('w');processo=None;sonda=None;resultado=None;fechado=False
try:
    pronto=False
    for _ in range(100):
        if xserver.poll() is not None:raise RuntimeError('Xvfb terminou antes de ficar pronto')
        try:
            with socket.socket(socket.AF_UNIX) as conexao:conexao.connect('/tmp/.X11-unix/X97')
            pronto=True;break
        except OSError:time.sleep(.1)
    if not pronto:raise TimeoutError('Xvfb não aceitou conexões em dez segundos')
    processo=subprocess.Popen(['ros2','launch','navegacao_autonoma','navegacao_simulada.launch.py','rviz:=true'],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    modulo=runpy.run_path(str(Path(__file__).with_name('validar-navegacao.py')))
    rclpy.init();sonda=modulo['Sonda']();aplicacao=QGuiApplication([])
    modulo['grafo'](sonda)
    # Mesma preparação manual de mapa do ensaio de navegação; não fornecer mapa perfeito.
    for _ in range(4):
        sonda.dirigir(.20,0.,4.8);sonda.dirigir(0.,.6,modulo['math'].pi/(2*.6))
    sonda.dirigir(0.,0.,.25);sonda.esperar(sonda.parada,prazo=3.);sonda.girar(1.)
    sonda.modo(True);sonda.girar(.15)
    objetivo,fim=sonda.objetivo((-2.,1.4,0.))
    sonda.esperar(lambda:bool(sonda.planos) and sonda.em_movimento(),prazo=12.);sonda.girar(3.)
    assert processo.poll() is None
    aplicacao.processEvents();tela=aplicacao.primaryScreen();assert tela is not None
    assert tela.grabWindow(0).save(str(PASTA/'previa-navegacao.png'))
    modulo['cancelar'](sonda,objetivo,fim)
    resultado={'rviz_real':True,'scan_mapa_modelo_costmaps_e_plano_nav2_ativos':True,'captura':'previa-navegacao.png','inspecao_visual_pendente':True}
finally:
    if sonda is not None and processo is not None and processo.poll() is None and rclpy.ok():
        from navegacao_autonoma.encerrar import encerrar
        (PASTA/'encerramento-lifecycle.json').write_text(json.dumps(encerrar(sonda),indent=2)+'\n')
    if sonda is not None:sonda.cliente.destroy();sonda.destroy_node()
    if rclpy.ok():rclpy.shutdown()
    if processo is not None and processo.poll() is None:
        fechar=Path(__file__).parents[1]/'descricao-ros/fechar-rviz.py'
        try:runpy.run_path(str(fechar))['fechar_rviz']()
        except RuntimeError as erro:(PASTA/'fechamento-ausente.log').write_text(str(erro))
        fechado=False
        for _ in range(50):
            if any('rviz2-' in linha and 'process has finished cleanly' in linha for linha in (PASTA/'lancamento-rviz.log').read_text().splitlines()):fechado=True;break
            time.sleep(.1)
        if not fechado:
            aplicacao.processEvents();aplicacao.primaryScreen().grabWindow(0).save(str(PASTA/'modal-fechamento.png'))
            confirmar_salvamento_instalado()
            for _ in range(50):
                if any('rviz2-' in linha and 'process has finished cleanly' in linha for linha in (PASTA/'lancamento-rviz.log').read_text().splitlines()):fechado=True;break
                time.sleep(.1)
        processo.send_signal(signal.SIGINT)
        try:processo.wait(timeout=25)
        except subprocess.TimeoutExpired:os.killpg(processo.pid,signal.SIGTERM);processo.wait(timeout=8)
    log.close()
    if xserver.poll() is None:xserver.terminate()
    xserver.wait(timeout=5);log_x.close()
assert processo is not None and processo.returncode==0
assert fechado,'RViz não encerrou pela janela'
texto=(PASTA/'lancamento-rviz.log').read_text()
assert 'Traceback' not in texto and 'process has died' not in texto,texto
assert 'could not load mesh' not in texto.lower() and 'could not load resource' not in texto.lower(),texto
assert resultado is not None
resultado['encerramento_limpo']=True
(PASTA/'resultado-rviz.json').write_text(json.dumps(resultado,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(resultado,ensure_ascii=False))
