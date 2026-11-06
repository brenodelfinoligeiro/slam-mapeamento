from glob import glob
from setuptools import find_packages, setup

nome_pacote = 'mapeamento_slam'

setup(
    name=nome_pacote,
    version='0.1.0',
    packages=find_packages(exclude=['testes']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['recursos/' + nome_pacote]),
        ('share/' + nome_pacote, ['package.xml']),
        ('share/' + nome_pacote + '/inicializacao', glob('inicializacao/*.launch.py')),
        ('share/' + nome_pacote + '/configuracao', glob('configuracao/*.yaml')),
        ('share/' + nome_pacote + '/visualizacao', glob('visualizacao/*.rviz')),
    ],
    install_requires=['setuptools'],
    extras_require={'test': ['pytest']},
    zip_safe=True,
    maintainer='lamggm',
    maintainer_email='a_definir@example.com',
    description='Mapeamento e localização por grafo usando SLAM Toolbox.',
    license='A definir',
    entry_points={'console_scripts': ['salvar_mapa = mapeamento_slam.salvar_mapa:main']},
)
