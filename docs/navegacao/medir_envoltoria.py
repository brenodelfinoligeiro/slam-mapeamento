"""Envoltória XY conservadora do CAD normalizado, sem modificar malhas."""
from pathlib import Path
import argparse,hashlib,json,math,struct,xml.etree.ElementTree as ET


def medir(raiz):
    pacote=Path(raiz)/'src/descricao/robo_movel'
    u=ET.parse(pacote/'descricao/robo_movel.urdf').getroot()
    juntas={j.find('child').get('link'):j for j in u.findall('joint')}
    def vetor(texto):return tuple(map(float,texto.split()))
    def origem(link):
        if link not in juntas:return (0.,0.,0.)
        j=juntas[link];o=j.find('origin')
        xyz=vetor(o.get('xyz','0 0 0')) if o is not None else (0.,0.,0.)
        if o is not None and vetor(o.get('rpy','0 0 0'))!=(0.,0.,0.):raise ValueError('Rotação de junta requer transformação completa; não inferir identidade')
        return tuple(a+b for a,b in zip(origem(j.find('parent').get('link')),xyz))
    raios={};hashes={}
    for link in u.findall('link'):
        nome=link.get('name');pos=origem(nome);movel=nome in juntas and juntas[nome].get('type')=='continuous'
        if movel and vetor(juntas[nome].find('axis').get('xyz'))!=(0.,1.,0.):raise ValueError('Eixo móvel diferente da hipótese auditada')
        for vis in link.findall('visual'):
            mesh=vis.find('geometry/mesh')
            if mesh is None:continue
            if vetor(mesh.get('scale','1 1 1'))!=(1.,1.,1.):raise ValueError('A malha deve estar normalizada em metros')
            o=vis.find('origin')
            if o is not None and any(vetor(o.get(k,'0 0 0'))!=(0.,0.,0.) for k in ['xyz','rpy']):raise ValueError('Origem visual não trivial exige transformação completa')
            uri=mesh.get('filename');prefixo='package://robo_movel/'
            if not uri.startswith(prefixo):raise ValueError('URI não pertence ao pacote de descrição')
            arquivo=(pacote/uri[len(prefixo):]).resolve()
            if not arquivo.is_relative_to(pacote.resolve()):raise ValueError('Malha fora do pacote')
            bruto=arquivo.read_bytes();n=struct.unpack_from('<I',bruto,80)[0]
            if len(bruto)!=84+50*n:raise ValueError('STL binário inconsistente')
            maior=0.
            for face in struct.iter_unpack('<12fH',bruto[84:]):
                for k in (3,6,9):
                    x,y,z=face[k:k+3]
                    if not all(math.isfinite(v) for v in (x,y,z)):raise ValueError('Vértice inválido')
                    x=abs(pos[0])+math.hypot(x,z) if movel else x+pos[0]
                    y+=pos[1];maior=max(maior,math.hypot(x,y))
            raios[arquivo.name]=maior;hashes[arquivo.name]=hashlib.sha256(bruto).hexdigest()
    if not raios:raise ValueError('Sem malhas para medir')
    raio=max(raios.values())
    return {'raio_envoltoria_cad_m':raio,'margem_proposta_m':.02,'raio_planejamento_m':math.ceil((raio+.02)*100)/100,
            'por_malha_m':raios,'sha256_malhas':hashes,
            'metodo':'Projeção XY de todas as malhas visuais, incluindo envelope completo de giro das rodas; somente referência CAD, não calibração física.'}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('raiz');o=p.parse_args()
    print(json.dumps(medir(o.raiz),ensure_ascii=False,indent=2))
