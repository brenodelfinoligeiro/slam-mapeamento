from setuptools import find_packages, setup


nome_pacote = "odometria_rodas"

setup(
    name=nome_pacote,
    version="0.1.0",
    packages=find_packages(exclude=["testes"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["recursos/" + nome_pacote]),
        ("share/" + nome_pacote, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    extras_require={"test": ["pytest"]},
    zip_safe=True,
    maintainer="lamggm",
    maintainer_email="a_definir@example.com",
    description="Odometria planar por contadores idealizados de rodas.",
    license="A definir",
    entry_points={
        "console_scripts": ["calcular_odometria = odometria_rodas.no:main"],
    },
)
