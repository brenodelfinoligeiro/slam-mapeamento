#!/usr/bin/env python3
"""Audita a bibliografia de software sem rede ou execução ROS."""
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote

VAULT = Path(__file__).resolve().parents[1]
FONTES = VAULT / '05-fontes'
RAIZ = VAULT.parents[1]


def main():
    manifest = json.loads((FONTES / 'software-fontes.json').read_text())
    ledger = json.loads((FONTES / 'citacoes.json').read_text())
    sources = {item['id']: item for item in ledger['sources']}
    assert len(sources) == len(ledger['sources']), 'IDs duplicados'
    inventory = json.loads((RAIZ / 'docs/arquivos-somente-locais.json').read_text())
    local = {item['caminho']: item for item in inventory['arquivos']}
    bibliography = (FONTES / 'referencias.bib').read_text()
    ids = []
    citation_documents = [FONTES / 'Software-e-monografia.md']
    for item in manifest['sources']:
        sid = item['id']
        ids.append(sid)
        source = sources[sid]
        assert source['url'].rstrip('/') == item['url'].rstrip('/')
        note = VAULT / (item['note'] + '.md')
        citation_documents.append(note)
        assert note.is_file(), note
        assert item['quote'] in [q['text'] for q in source['quotes']]
        evidence = VAULT / item['evidence']
        data = evidence.read_bytes()
        assert hashlib.sha256(data).hexdigest() == item['sha256'], evidence
        normalize = lambda text: re.sub(r'\s+', ' ', text).strip()
        assert normalize(item['quote']) in normalize(data.decode('utf-8')), evidence
        for key, hash_key in [('metadata_evidence', 'metadata_sha256'),
                              ('pdf_path', 'pdf_sha256')]:
            if item.get(key):
                attachment = VAULT / item[key]
                content = attachment.read_bytes()
                assert hashlib.sha256(content).hexdigest() == item[hash_key], attachment
                rel = attachment.relative_to(RAIZ).as_posix()
                assert local[rel]['sha256'] == item[hash_key], rel
                if key == 'pdf_path':
                    assert content.startswith(b'%PDF-'), attachment
                    assert item['pdf_pages'] > 0
        relative = evidence.relative_to(RAIZ).as_posix()
        assert local[relative]['sha256'] == item['sha256'], relative
        assert re.search(r'@\w+\{source' + str(sid) + r'\s*,', bibliography)
        assert (RAIZ / item['local_path']).exists(), item['local_path']
        if item.get('doi'):
            assert item['doi'] in bibliography
    assert len(ids) == len(set(ids))
    links = 0
    for note in VAULT.rglob('*.md'):
        text = note.read_text()
        for target in re.findall(r'\[\[([^\]|]+)(?:\|[^\]]*)?\]\]', text):
            target = target.split('#')[0]
            if not target:
                continue
            path = VAULT / target
            assert path.exists() or path.with_suffix('.md').exists(), (note, target)
            links += 1
        for target in re.findall(r'(?<!!)\[[^\]\n]*\]\(([^)\n]+)\)', text):
            if target.startswith(('http:', 'https:', '#', 'mailto:')):
                continue
            path = (note.parent / unquote(target.split('#')[0])).resolve()
            assert path.exists(), (note, target)
            links += 1
    for note in citation_documents:
        text = note.read_text()
        assert not re.search('slam' + 'derson', text, re.I), note
        assert not any(ord(c) < 32 and c not in '\n\r\t' for c in text), note
    result = {'fontes_software': len(ids), 'documentos_citados': len(citation_documents),
              'links_locais_vault': links, 'hashes_e_trechos': 'ok',
              'bibliografia_e_ids': 'ok', 'nome_privado_nos_textos_novos': 'ausente',
              'limite': 'Auditoria documental; não executa ROS, simulação ou hardware.'}
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
