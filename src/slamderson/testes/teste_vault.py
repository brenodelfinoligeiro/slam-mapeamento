"""Verifica a base documental e a integridade das referências locais."""
from hashlib import sha256
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
VAULT = RAIZ / 'docs' / 'vault-slamderson'


def teste_vault_com_fontes_e_orientacao():
    assert (VAULT / '.obsidian' / 'app.json').is_file()
    assert (VAULT / 'Inicio.md').is_file()
    assert (VAULT / '01-componentes' / 'Encoder-MH-Sensor-Series.md').is_file()
    assert (VAULT / '05-fontes' / 'Catalogo-de-fontes.md').is_file()
    orientacoes = (RAIZ / 'AGENTS.md').read_text(encoding='utf-8')
    assert 'docs/vault-slamderson' in orientacoes
    assert 'fontes' in orientacoes.lower()
    manifesto = json.loads((VAULT / '05-fontes' / 'manifesto-arquivos.json').read_text())
    assert len(manifesto['arquivos']) >= 3
    for referencia in manifesto['arquivos']:
        arquivo = (VAULT / referencia['caminho']).resolve()
        assert arquivo.is_relative_to(VAULT.resolve())
        assert referencia['paginas'] > 0
        assert referencia['url_download'].startswith('https://')
        if not arquivo.exists():
            inventario = json.loads((RAIZ / 'docs/arquivos-somente-locais.json').read_text())
            omitidos = {item['caminho']: item for item in inventario['arquivos']}
            item = omitidos.get(arquivo.relative_to(RAIZ).as_posix())
            assert item and item['motivo'], f'PDF ausente sem justificativa: {arquivo}'
            assert item['sha256'] == referencia['sha256']
            continue
        dados = arquivo.read_bytes()
        assert dados.startswith(b'%PDF-')
        assert sha256(dados).hexdigest() == referencia['sha256']
        assert referencia['paginas'] > 0
        assert referencia['url_download'].startswith('https://')
