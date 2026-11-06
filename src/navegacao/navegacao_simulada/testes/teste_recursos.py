from pathlib import Path
import xml.etree.ElementTree as ET

def teste_manifesto_e_recursos():
    pasta = Path(__file__).resolve().parents[1]
    assert ET.parse(pasta/'package.xml').getroot().findtext('name') == pasta.name
    assert (pasta/'recursos'/pasta.name).is_file()


def teste_referencia_virtual_tem_transformacao_explicita():
    pasta=Path(__file__).resolve().parents[1]
    fonte=(pasta/'inicializacao/simulacao.launch.py').read_text()
    assert 'static_transform_publisher' in fonte
    assert "'simulacao_mundo'" in fonte and "'odom'" in fonte


def teste_origem_virtual_pode_ser_desabilitada_para_slam():
    import ast
    pasta=Path(__file__).resolve().parents[1]
    fonte=(pasta/'inicializacao/simulacao.launch.py').read_text()
    assert "DeclareLaunchArgument('origem_virtual',default_value='true')" in fonte
    arvore=ast.parse(fonte)
    nos=[x for x in ast.walk(arvore) if isinstance(x,ast.Call) and isinstance(x.func,ast.Name) and x.func.id=='Node']
    origem=[x for x in nos if any(k.arg=='name' and isinstance(k.value,ast.Constant) and k.value.value=='origem_virtual' for k in x.keywords)]
    assert len(origem)==1
    condicao=next(k.value for k in origem[0].keywords if k.arg=='condition')
    assert 'IfCondition' in ast.dump(condicao) and 'origem_virtual' in ast.dump(condicao)
