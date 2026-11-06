"""Confere integridade e procedência explícita dos modelos CAD coletados."""
from hashlib import sha256
import json
from pathlib import Path

RAIZ = next(p for p in Path(__file__).resolve().parents if (p / 'docs').is_dir() and (p / 'src').is_dir())
PASTA = RAIZ / 'docs' / 'modelos-3d'


def teste_modelos_cad_com_procedencia_e_integridade():
    manifesto = json.loads((PASTA / 'manifesto.json').read_text(encoding='utf-8'))
    assert (PASTA / 'catalogo.md').is_file()
    assert manifesto['modelos'], 'É necessário salvar ao menos um modelo real.'
    for modelo in manifesto['modelos']:
        assert modelo['componente']
        assert modelo['correspondencia']
        assert modelo['origem_url'].startswith('https://')
        assert modelo['licenca']['situacao'] in ('identificada', 'nao_identificada')
        arquivo = (PASTA / modelo['caminho']).resolve()
        assert arquivo.is_relative_to(PASTA.resolve())
        assert modelo['validacao']['estado'] in ('importado', 'nao_inspecionado', 'erro')
        assert modelo['validacao']['sha256'] == modelo['sha256']
        if modelo['validacao'].get('geometria_valida') is False:
            assert modelo.get('uso_recomendado') == 'somente_proveniencia'
        if not arquivo.exists():
            inventario = json.loads((RAIZ / 'docs/arquivos-somente-locais.json').read_text())
            omitidos = {item['caminho']: item for item in inventario['arquivos']}
            item = omitidos.get(arquivo.relative_to(RAIZ).as_posix())
            assert item and item['motivo'], f'CAD ausente sem justificativa: {arquivo}'
            assert item['sha256'] == modelo['sha256']
            continue
        dados = arquivo.read_bytes()
        assert dados and sha256(dados).hexdigest() == modelo['sha256']
        assert not dados.lstrip().lower().startswith((b'<!doctype html', b'<html'))
        if arquivo.suffix.lower() in ('.step', '.stp'):
            assert dados.lstrip().startswith(b'ISO-10303-21;')
        assert modelo['validacao']['estado'] in ('importado', 'nao_inspecionado', 'erro')
        assert modelo['validacao']['sha256'] == modelo['sha256']
        if modelo['validacao'].get('geometria_valida') is False:
            assert modelo.get('uso_recomendado') == 'somente_proveniencia'
