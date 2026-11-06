from pathlib import Path
from setuptools import setup,find_packages
P=Path(__file__).parent
setup(name='navegacao_autonoma',version='0.1.0',packages=find_packages(exclude=('testes','testes.*')),
 data_files=[('share/ament_index/resource_index/packages',['recursos/navegacao_autonoma']),('share/navegacao_autonoma',['package.xml'])]+[
 (f'share/navegacao_autonoma/{pasta}',[str(f.relative_to(P)) for f in (P/pasta).glob('*') if f.is_file()]) for pasta in ['inicializacao','configuracao','visualizacao']],
 install_requires=['setuptools'],extras_require={'test':['pytest']},zip_safe=True,
 maintainer='lamggm',maintainer_email='a_definir@example.com',license='A definir',
 description='Navegação autônoma Nav2 arbitrada',entry_points={'console_scripts':[
 'proteger = navegacao_autonoma.no_protecao:main','ir_para = navegacao_autonoma.ir_para:main',
 'inicializar = navegacao_autonoma.inicializar:main','encerrar = navegacao_autonoma.encerrar:main']})
