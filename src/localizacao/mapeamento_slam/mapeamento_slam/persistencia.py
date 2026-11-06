"""Salvar somente com status upstream e artefatos novos verificáveis."""
import math
from pathlib import Path
import re
import yaml

EXTENSOES = ('.posegraph', '.data', '.pgm', '.yaml')


def preparar_saida(arquivo, raiz=None):
    prefixo = Path(arquivo).expanduser()
    if not arquivo or not prefixo.is_absolute():
        raise ValueError('--arquivo deve ser um prefixo absoluto')
    prefixo = prefixo.resolve()
    if prefixo == Path('/'):
        raise ValueError('--arquivo precisa de um nome de prefixo')
    if raiz is not None and (not prefixo.is_relative_to(Path(raiz).resolve()) or prefixo == Path(raiz).resolve()):
        raise ValueError('--arquivo deve ficar dentro da raiz permitida (sem escapar por symlink)')
    # SaveMap Jazzy repassa o prefixo ao map_saver_cli; usa esse alfabeto.
    if not re.fullmatch(r'[A-Za-z0-9_./-]+', str(prefixo)) or prefixo.suffix:
        raise ValueError('--arquivo exige prefixo sem extensão, espaços ou caracteres de shell')
    arquivos = tuple(Path(str(prefixo) + extensao) for extensao in EXTENSOES)
    if any(p.exists() or p.is_symlink() for p in arquivos):
        raise ValueError('destino já existe; use outro prefixo para não aceitar arquivos antigos')
    prefixo.parent.mkdir(parents=True, exist_ok=True)
    return prefixo, arquivos


def verificar_arquivos(prefixo, arquivos):
    for arquivo in arquivos:
        if not arquivo.is_file() or arquivo.stat().st_size == 0:
            raise RuntimeError(f'arquivo não gravado ou vazio: {arquivo}')
    try:
        dados = yaml.safe_load(Path(str(prefixo) + '.yaml').read_text())
        imagem = Path(dados['image'])
        if not imagem.is_absolute():
            imagem = prefixo.parent / imagem
        if imagem.resolve() != Path(str(prefixo) + '.pgm').resolve():
            raise ValueError('YAML aponta para outra imagem')
        resolucao = float(dados['resolution'])
        origem = dados['origin']
        if not math.isfinite(resolucao) or resolucao <= 0:
            raise ValueError('resolução inválida')
        if len(origem) != 3 or not all(math.isfinite(float(v)) for v in origem):
            raise ValueError('origem inválida')
        # map_saver_cli Jazzy produz PGM binário P5, máximo 255.
        conteudo = imagem.read_bytes()
        cabecalho = re.match(rb'P5\s+(?:#[^\n]*\n\s*)*(\d+)\s+(\d+)\s+(\d+)[\r\n ]', conteudo)
        if not cabecalho:
            raise ValueError('cabeçalho PGM inválido')
        largura, altura, maximo = map(int, cabecalho.groups())
        if largura <= 0 or altura <= 0 or maximo != 255:
            raise ValueError('dimensões PGM inválidas')
        if len(conteudo) - cabecalho.end() != largura * altura:
            raise ValueError('PGM truncado ou com dados excedentes')
    except (OSError, ValueError, TypeError, KeyError, yaml.YAMLError) as erro:
        raise RuntimeError(f'mapa salvo inválido: {erro}') from erro


def salvar(arquivo, chamar, raiz=None):
    """chamar(servico, prefixo) é o transporte ROS; não é um publicador de mapas."""
    prefixo, arquivos = preparar_saida(arquivo, raiz)
    for servico in ('serialize_map', 'save_map'):
        resposta = chamar(servico, str(prefixo))
        if servico == 'serialize_map':
            sucesso = (resposta is not None and hasattr(resposta, 'RESULT_SUCCESS')
                       and getattr(resposta, 'result', None) == resposta.RESULT_SUCCESS)
        else:
            # nav2_msgs/SaveMap usa bool; False NÃO é sucesso uint8==0.
            sucesso = resposta is not None and getattr(resposta, 'result', None) is True
        if not sucesso:
            raise RuntimeError(f'{servico}: resposta sem sucesso: {resposta!r}')
    verificar_arquivos(prefixo, arquivos)
    return arquivos
