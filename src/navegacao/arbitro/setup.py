from pathlib import Path
from setuptools import setup,find_packages
P=Path(__file__).parent
setup(name='arbitro',version='0.1.0',packages=find_packages(exclude=('testes','testes.*')),
 data_files=[('share/ament_index/resource_index/packages',['recursos/arbitro']),('share/arbitro',['package.xml']),
 ('share/arbitro/inicializacao',[str(f.relative_to(P)) for f in (P/'inicializacao').glob('*.py')])],
 install_requires=['setuptools'],extras_require={'test':['pytest']},zip_safe=True,
 maintainer='lamggm',maintainer_email='a_definir@example.com',license='A definir',
 description='Árbitro de comandos de movimento',entry_points={'console_scripts':['arbitrar = arbitro.no:main']})
