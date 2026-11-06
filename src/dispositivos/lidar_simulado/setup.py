from setuptools import find_packages, setup


setup(
    name='lidar_simulado',
    version='0.1.0',
    packages=find_packages(exclude=['testes']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['recursos/lidar_simulado']),
        ('share/lidar_simulado', ['package.xml']),
        ('share/lidar_simulado/configuracao', ['configuracao/mundo.yaml']),
    ],
    install_requires=['setuptools', 'PyYAML'],
    extras_require={'test': ['pytest']},
    zip_safe=True,
    maintainer='lamggm',
    maintainer_email='a_definir@example.com',
    description='LiDAR geométrico virtual para SLAM 2D acadêmico.',
    license='A definir',
    entry_points={
        'console_scripts': ['simular_lidar = lidar_simulado.no_lidar:main'],
    },
)
