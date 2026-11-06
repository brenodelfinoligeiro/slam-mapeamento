"""Valida agrupadores sem manifesto e descrição isolada dos outros domínios."""
from pathlib import Path
RAIZ = Path(__file__).resolve().parents[1]
TRABALHO = next(p for p in RAIZ.parents if (p/'docs').is_dir() and (p/'src').is_dir())

def teste_estrutura_solicitada():
    grupos={'descricao','localizacao','dispositivos','navegacao','percepcao'}
    assert {p.name for p in (TRABALHO/'src').iterdir() if p.is_dir()} == grupos
    for nome in grupos:assert not (TRABALHO/'src'/nome/'package.xml').exists()
    assert RAIZ.parent.name=='descricao'
    for dominio in ('controle','mapeamento','dispositivos','localizacao','navegacao','percepcao'):
        assert not (RAIZ/'robo_movel'/dominio).exists()
    for recurso in ('inicializacao','configuracao','descricao','visualizacao'):
        assert (RAIZ/recurso).is_dir()
