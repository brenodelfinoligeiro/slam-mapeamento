"""Valida o inventário local e a navegação da cópia pública sem baixar anexos."""
from hashlib import sha256
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

RAIZ = next(p for p in Path(__file__).resolve().parents if (p / 'docs').is_dir() and (p / 'src').is_dir())
DOCS = RAIZ / 'docs'
VAULT = DOCS / json.loads((DOCS / 'nomenclatura-ros.json').read_text())['base_conhecimento']


def teste_inventario_de_referencias_somente_locais():
    inventario = json.loads((DOCS / 'arquivos-somente-locais.json').read_text())
    assert inventario['versao'] == 1
    caminhos = set()
    for item in inventario['arquivos']:
        relativo = Path(item['caminho'])
        assert not relativo.is_absolute() and '..' not in relativo.parts
        assert relativo.parts[0] == 'docs'
        assert item['caminho'] not in caminhos
        caminhos.add(item['caminho'])
        assert re.fullmatch(r'[0-9a-f]{64}', item['sha256'])
        assert item['motivo'].strip()
        arquivo = RAIZ / relativo
        if arquivo.exists():
            assert sha256(arquivo.read_bytes()).hexdigest() == item['sha256']


def teste_links_ativos_publicados_ou_explicitamente_locais():
    inventario = json.loads((DOCS / 'arquivos-somente-locais.json').read_text())
    somente_locais = {(RAIZ / item['caminho']).resolve() for item in inventario['arquivos']}
    erros = []
    for nota in DOCS.rglob('*.md'):
        if 'historico' in nota.relative_to(DOCS).parts:
            continue  # O histórico preserva a estrutura e os caminhos antigos.
        texto = re.sub(r'```.*?```', '', nota.read_text(), flags=re.S)
        alvos = []
        for bruto in re.findall(r'!?\[[^\]\n]*\]\(([^)\n]+)\)', texto):
            url = bruto.strip().strip('<>')
            partes = urlsplit(url)
            if partes.scheme or partes.netloc or not partes.path:
                continue
            alvos.append((nota.parent / unquote(partes.path)).resolve())
        for bruto in re.findall(r'\[\[([^\]]+)\]\]', texto):
            caminho = bruto.split('|', 1)[0].split('#', 1)[0]
            if not caminho:
                continue
            if not Path(caminho).suffix:
                caminho += '.md'
            base = VAULT if nota.is_relative_to(VAULT) else DOCS
            alvos.append((base / caminho).resolve())
        for alvo in alvos:
            if not alvo.exists() and alvo not in somente_locais:
                erros.append(f'{nota.relative_to(RAIZ)} -> {alvo}')
    assert not erros, '\n'.join(erros)
