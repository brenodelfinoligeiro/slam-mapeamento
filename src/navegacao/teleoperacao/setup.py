from pathlib import Path
from collections.abc import Sequence
from setuptools import setup, find_packages
NOME = 'teleoperacao'
RAIZ = Path(__file__).parent
dados: list[tuple[str, Sequence[str]]] = [('share/ament_index/resource_index/packages', ['recursos/'+NOME]), ('share/'+NOME, ['package.xml'])]
for pasta in ('inicializacao', 'configuracao', 'visualizacao'):
    for arquivo in sorted((RAIZ/pasta).rglob('*')):
        if arquivo.is_file() and '__pycache__' not in arquivo.parts:
            relativo = arquivo.relative_to(RAIZ)
            dados.append(('share/'+NOME+'/'+str(relativo.parent), [str(relativo)]))
setup(name=NOME, version='0.0.0', packages=find_packages(exclude=('testes','testes.*')), data_files=dados,
      install_requires=['setuptools'], extras_require={'test':['pytest']}, zip_safe=True,
      maintainer='lamggm', maintainer_email='a_definir@example.com', license='A definir',
      description='Ferramentas ROS 2 de simulação em português',
      entry_points={'console_scripts': ['teclado = teleoperacao.no:main']})
