"""Validação anterior à criação de processos ROS."""
from pathlib import Path


def validar_grafo(arquivo):
    """Recebe prefixo sem extensão; a desserialização real pertence ao upstream."""
    if not arquivo:
        raise ValueError('arquivo_grafo é obrigatório para localização')
    prefixo = Path(arquivo).expanduser().absolute()
    if prefixo.suffix:
        raise ValueError('arquivo_grafo deve ser um prefixo sem extensão')
    for extensao in ('.posegraph', '.data'):
        caminho = Path(str(prefixo) + extensao)
        if not caminho.is_file() or caminho.stat().st_size == 0:
            raise ValueError(f'arquivo do grafo ausente ou vazio: {caminho}')
    return str(prefixo)


def parametros_do_modo(modo, arquivo_grafo):
    if modo not in ('mapeamento', 'localizacao'):
        raise ValueError('modo deve ser mapeamento ou localizacao')
    parametros: dict[str, object] = {'mode': 'mapping' if modo == 'mapeamento' else 'localization'}
    if modo == 'localizacao' or arquivo_grafo:
        parametros['map_file_name'] = validar_grafo(arquivo_grafo)
        # Estimativa inicial do cenário, NÃO pose perfeita recebida do simulador.
        # Pode ser corrigida pelo operador em /initialpose durante localização.
        parametros['map_start_pose'] = [0.0, 0.0, 0.0]
    return parametros
