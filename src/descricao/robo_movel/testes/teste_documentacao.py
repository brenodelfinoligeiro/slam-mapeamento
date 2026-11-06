"""Verifica a separação entre documentação acadêmica e código do projeto."""
from pathlib import Path

RAIZ_PACOTE = Path(__file__).resolve().parents[1]
RAIZ_TRABALHO = next(p for p in Path(__file__).resolve().parents if (p / 'docs').is_dir() and (p / 'src').is_dir())
IGNORADOS = {'build', 'install', 'log', '.venv', '__pycache__', '.pytest_cache', '.git'}
CAPITULOS = (
    'LEIA-ME.md',
    '01-visao-geral.md',
    '02-arquitetura.md',
    '03-componentes-e-ligacoes.md',
    '04-comunicacao-uart.md',
    '05-desenvolvimento-e-execucao.md',
    '06-validacao-e-calibracao.md',
    '07-decisoes-e-pendencias.md',
    'convencoes.md',
    'responsabilidades.md',
)


def teste_documentacao_centralizada_em_docs():
    documentacao = RAIZ_TRABALHO / 'docs'
    assert documentacao.is_dir(), 'A documentação deve ficar em docs/ na raiz.'
    for capitulo in CAPITULOS:
        assert (documentacao / capitulo).is_file(), f'Capítulo ausente: {capitulo}'
    dispersos = [
        str(arquivo.relative_to(RAIZ_TRABALHO))
        for arquivo in RAIZ_TRABALHO.rglob('*.md')
        if not IGNORADOS.intersection(arquivo.relative_to(RAIZ_TRABALHO).parts)
        and arquivo.relative_to(RAIZ_TRABALHO).parts[0] != 'docs'
        and arquivo not in (RAIZ_TRABALHO / 'AGENTS.md', RAIZ_TRABALHO / 'README.md')
    ]
    assert not dispersos, f'Documentação fora de docs/: {dispersos}'
    assert not (RAIZ_PACOTE / 'documentacao').exists()
