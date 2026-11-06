"""Só no contêiner de ensaio, após mapear/encerrar; não usar em sessão ativa."""
from pathlib import Path
import subprocess,json,hashlib
saida=Path('/work/negativos');saida.mkdir(exist_ok=True)
casos=[('modo_invalido',['ros2','launch','mapeamento_slam','slam_simulado.launch.py','modo:=navegacao','rviz:=false'],'modo deve ser'),
('grafo_ausente',['ros2','launch','mapeamento_slam','slam_simulado.launch.py','modo:=localizacao','rviz:=false'],'arquivo_grafo'),
('grafo_inexistente',['ros2','launch','mapeamento_slam','slam_simulado.launch.py','modo:=localizacao','arquivo_grafo:=/work/mapas/nao_existe','rviz:=false'],'ausente ou vazio'),
('mapa_existente',['ros2','run','mapeamento_slam','salvar_mapa','--arquivo','/work/mapas/ensaio'],'destino já existe'),
('servico_ausente',['ros2','run','mapeamento_slam','salvar_mapa','--arquivo','/work/mapas/sem_servico','--timeout','1'],'serviço indisponível'),
('sensor_parametro_invalido',['ros2','run','lidar_simulado','simular_lidar','--ros-args','-p','numero_raios:=0'],'numero_raios')]
antes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in Path('/work/mapas').glob('ensaio.*')}
resultados={}
for nome,args,trecho in casos:
 res=subprocess.run(args,capture_output=True,text=True,timeout=25)
 texto=res.stdout+'\n'+res.stderr;(saida/(nome+'.log')).write_text(texto)
 assert res.returncode!=0 and trecho in texto,(nome,res.returncode,texto)
 if nome.startswith(('modo','grafo')):assert 'process started with pid' not in texto
 resultados[nome]={'status':'rejeitado_como_esperado','returncode':res.returncode,'processos_nao_iniciados':nome.startswith(('modo','grafo'))}
assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in antes.items())
assert not list(Path('/work/mapas').glob('sem_servico.*'))
(saida/'resultado.json').write_text(json.dumps(resultados,ensure_ascii=False,indent=2)+'\n');print(json.dumps(resultados,ensure_ascii=False))
