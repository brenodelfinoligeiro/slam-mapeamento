"""CLI de persistência: --arquivo /work/mapas/sala [--timeout 20]."""
import argparse
import math
import sys
import time
from mapeamento_slam.persistencia import preparar_saida, salvar


def tempo_positivo(valor):
    tempo = float(valor)
    if not math.isfinite(tempo) or tempo <= 0:
        raise argparse.ArgumentTypeError('timeout deve ser finito e positivo')
    return tempo


def criar_requisicao(tipo, servico, arquivo):
    requisicao = tipo.Request()
    if servico == 'serialize_map':
        requisicao.filename = arquivo
    else:
        requisicao.map_topic = '/map'
        requisicao.map_url = arquivo
        requisicao.image_format = 'pgm'
        requisicao.map_mode = 'trinary'
        requisicao.free_thresh = 0.196
        requisicao.occupied_thresh = 0.65
    return requisicao


def chamar_servico(no, ros, tipo, nome, requisicao, timeout):
    fim = time.monotonic() + timeout
    cliente = no.create_client(tipo, nome)
    try:
        if not cliente.wait_for_service(timeout_sec=timeout):
            raise TimeoutError(f'serviço indisponível: {nome}')
        restante = fim - time.monotonic()
        if restante <= 0:
            raise TimeoutError(f'prazo esgotado: {nome}')
        futuro = cliente.call_async(requisicao)
        ros.spin_until_future_complete(no, futuro, timeout_sec=restante)
        if not futuro.done():
            futuro.cancel()
            raise TimeoutError(f'sem resposta no prazo: {nome}')
        return futuro.result()
    finally:
        no.destroy_client(cliente)


def main(args=None):
    parser = argparse.ArgumentParser(
        description='Salva PGM/YAML e grafo do SLAM no modo mapeamento; não sobrescreve arquivos.',
        epilog='Para recarregar: slam_simulado.launch.py modo:=localizacao '
               'arquivo_grafo:=/work/mapas/sala (prefixo sem extensão).')
    parser.add_argument('--arquivo', required=True, help='prefixo absoluto sem extensão, por exemplo /mapas/sala')
    parser.add_argument('--timeout', type=tempo_positivo, default=20.0,
                        help='prazo em segundos por serviço, incluindo descoberta (padrão: 20)')
    argumentos = parser.parse_args(args)
    ros = None
    no = None
    try:
        preparar_saida(argumentos.arquivo)
        # Importações tardias permitem --help e validação de CLI sem ROS instalado.
        import rclpy
        from slam_toolbox.srv import SerializePoseGraph
        from nav2_msgs.srv import SaveMap
        ros = rclpy
        ros.init(args=[])
        no = ros.create_node('salvar_mapa')
        tipos = {'serialize_map': SerializePoseGraph, 'save_map': SaveMap}

        def chamar(servico, arquivo):
            tipo = tipos[servico]
            nome = '/slam_toolbox/serialize_map' if servico == 'serialize_map' else '/salvador_mapa/save_map'
            return chamar_servico(no, ros, tipo, nome,
                                  criar_requisicao(tipo, servico, arquivo), argumentos.timeout)

        arquivos = salvar(argumentos.arquivo, chamar)
        print('Mapa e grafo verificados: ' + ', '.join(str(p) for p in arquivos))
        return 0
    except (Exception, KeyboardInterrupt) as erro:
        print(f'Falha ao salvar mapa: {erro}. Arquivos parciais podem permanecer; use outro prefixo.',
              file=sys.stderr)
        return 1
    finally:
        if no is not None:
            no.destroy_node()
        if ros is not None and ros.ok():
            ros.shutdown()


if __name__ == '__main__':
    sys.exit(main())
