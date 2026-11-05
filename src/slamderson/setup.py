from pathlib import Path
from setuptools import find_packages, setup

NOME_PACOTE = 'slamderson'
RAIZ = Path(__file__).parent
arquivos_dados = [
    ('share/ament_index/resource_index/packages', ['recursos/' + NOME_PACOTE]),
    ('share/' + NOME_PACOTE, ['package.xml']),
]
for pasta in ('inicializacao', 'configuracao', 'descricao', 'mapas', 'visualizacao'):
    for arquivo in sorted((RAIZ / pasta).rglob('*')):
        if arquivo.is_dir() or '__pycache__' in arquivo.parts:
            continue
        caminho_relativo = arquivo.relative_to(RAIZ)
        destino = 'share/' + NOME_PACOTE + '/' + str(caminho_relativo.parent)
        arquivos_dados.append((destino, [str(caminho_relativo)]))

setup(
    name=NOME_PACOTE,
    version='0.0.0',
    packages=find_packages(exclude=('testes', 'testes.*')),

    data_files=arquivos_dados,
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='lamggm',
    maintainer_email='a_definir@example.com',
    description='Pacote ROS 2 acadêmico do robô móvel diferencial Slamderson.',
    license='A definir',
    extras_require={'test': ['pytest']},
    entry_points={'console_scripts': []},
)
