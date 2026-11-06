"""Regressões de unidades, cinemática e rastreabilidade do URDF já gerado do CAD."""
from pathlib import Path
from hashlib import sha256
import json
import math
import struct
import xml.etree.ElementTree as ET

PACOTE = Path(__file__).resolve().parents[1]


def teste_arvore_tem_um_pai_por_link_sem_ciclos():
    robo = ET.parse(PACOTE / 'descricao/robo_movel.urdf').getroot()
    links = {n.attrib['name'] for n in robo.findall('link')}
    joints = robo.findall('joint')
    pais = {j.find('child').attrib['link']: j.find('parent').attrib['link'] for j in joints}
    assert len(pais) == len(joints) == len(links) - 1
    assert links - set(pais) == {'base_footprint'}
    for link in links:
        vistos = set()
        while link in pais:
            assert link not in vistos
            vistos.add(link)
            link = pais[link]
        assert link == 'base_footprint'


def teste_rotacao_cad_ros_nao_espelha_o_robo():
    m = json.loads((PACOTE / 'descricao/origem-cad.json').read_text())
    r = m['rotacao_CAD_para_ROS']
    det = (r[0][0]*(r[1][1]*r[2][2]-r[1][2]*r[2][1])
           - r[0][1]*(r[1][0]*r[2][2]-r[1][2]*r[2][0])
           + r[0][2]*(r[1][0]*r[2][1]-r[1][1]*r[2][0]))
    assert math.isclose(det, 1.0)
    assert r == [[0, -1, 0], [1, 0, 0], [0, 0, 1]]
    for a in range(3):
        for b in range(3):
            assert math.isclose(sum(r[a][i]*r[b][i] for i in range(3)), float(a == b), abs_tol=1e-12)


def teste_origens_das_juntas_reproduzem_o_cad_em_metros():
    m = json.loads((PACOTE / 'descricao/origem-cad.json').read_text())
    robo = ET.parse(PACOTE / 'descricao/robo_movel.urdf').getroot()
    base = m['origem_base_CAD_mm']
    for joint in robo.findall('joint'):
        child = joint.find('child').attrib['link']
        valor = [float(x) for x in joint.find('origin').attrib['xyz'].split()]
        if child == 'base_link':
            esperado = [0, 0, m['altura_base_m']]
        else:
            delta = [m['frames_CAD_mm'][child][i]-base[i] for i in range(3)]
            esperado = [sum(m['rotacao_CAD_para_ROS'][i][j]*delta[j] for j in range(3))*.001 for i in range(3)]
        assert all(math.isclose(a, b, abs_tol=1e-11) for a, b in zip(valor, esperado))


def teste_rodas_continuas_usam_eixo_ros_y_e_lados_corretos():
    robo = ET.parse(PACOTE / 'descricao/robo_movel.urdf').getroot()
    joints = {j.attrib['name']: j for j in robo.findall('joint')}
    assert {j.attrib['name'] for j in joints.values() if j.attrib['type'] == 'continuous'} == {'left_wheel_joint', 'right_wheel_joint'}
    for lado, sinal in [('left', 1), ('right', -1)]:
        j = joints[lado + '_wheel_joint']
        assert j.find('axis').attrib['xyz'] == '0 1 0'
        assert float(j.find('origin').attrib['xyz'].split()[1]) * sinal > 0


def teste_malhas_em_metros_resolvem_e_preservam_hashes_e_facetas():
    m = json.loads((PACOTE / 'descricao/origem-cad.json').read_text())
    robo = ET.parse(PACOTE / 'descricao/robo_movel.urdf').getroot()
    caminhos = set()
    for geometry in robo.findall('.//mesh'):
        assert geometry.attrib['scale'] == '1 1 1'
        uri = geometry.attrib['filename']
        assert uri.startswith('package://robo_movel/descricao/malhas/')
        caminho = PACOTE / uri.removeprefix('package://robo_movel/')
        assert caminho.is_file()
        caminhos.add(caminho.relative_to(PACOTE).as_posix())
    assert caminhos == {g['arquivo'] for g in m['meshes']}
    for g in m['meshes']:
        raw = (PACOTE / g['arquivo']).read_bytes()
        assert sha256(raw).hexdigest() == g['sha256']
        assert len(raw) == 84 + 50 * struct.unpack('<I', raw[80:84])[0]
        assert struct.unpack('<I', raw[80:84])[0] == g['triangulos_exportados']
        assert g['erro_max_bbox_m'] <= .00051
        assert all(abs(x) < 1 for p in g['bbox_exportado_m'] for x in p)
    assert sha256((PACOTE / 'descricao/robo_movel.urdf').read_bytes()).hexdigest() == m['sha256_urdf']


def teste_folhas_cad_sem_duplicar_compostos_e_sem_cupom_no_robo():
    m = json.loads((PACOTE / 'descricao/origem-cad.json').read_text())
    objetos = [o['objeto'] for g in m['meshes'] for o in g['objetos']]
    assert len(objetos) == len(set(objetos))
    assert not {'Inferior', 'Superior', 'Lidar', 'CarcacaBase', 'Tampas', 'Acessos', 'FerragensR05', 'CupomInsertos'} & set(objetos)
    estrutura = next(g for g in m['meshes'] if g['nome'] == 'estrutura')
    assert len(estrutura['objetos']) == m['pecas_impressas'] == 44


def teste_sem_simular_calibracao_inercias_ou_contato_do_rodizio():
    m = json.loads((PACOTE / 'descricao/origem-cad.json').read_text())
    robo = ET.parse(PACOTE / 'descricao/robo_movel.urdf').getroot()
    assert m['sensores_calibrados'] is False and m['inerciais_medidas'] is False
    assert m['rodizio_acima_plano_rodas_mm'] > 0
    assert not robo.findall('.//inertial') and not robo.findall('.//transmission')
    assert not {'imu_link', 'laser', 'laser_frame'} & {x.attrib['name'] for x in robo.findall('link')}
