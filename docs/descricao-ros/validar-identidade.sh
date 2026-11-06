#!/usr/bin/env bash
# Executar somente no contêiner isolado, com /workspace:ro e /work gravável.
set -eo pipefail
source /opt/ros/jazzy/setup.bash
export PYTHONDONTWRITEBYTECODE=1
export PYTEST_ADDOPTS="-o cache_dir=/work/pytest-cache"
mkdir -p /work/cache /work/runtime
chmod 700 /work/runtime
cd /work
if [ "${1:-}" = construir ]; then
  colcon list --base-paths /workspace/src
  colcon build --base-paths /workspace/src --packages-select robo_movel --event-handlers console_direct+
  source /work/install/setup.bash
  cd /work/cache
  python3 - <<'PY'
from pathlib import Path
import importlib, importlib.util, json, hashlib, subprocess
from ament_index_python.packages import get_package_share_directory
import robo_movel
assert str(Path(robo_movel.__file__).resolve()).startswith('/work/install/'), robo_movel.__file__
modulos=[]
for pasta in Path('/workspace/src/robo_movel/robo_movel').iterdir():
    if pasta.is_dir() and (pasta/'__init__.py').is_file():
        modulo=importlib.import_module('robo_movel.'+pasta.name)
        assert str(Path(modulo.__file__).resolve()).startswith('/work/install/'), modulo.__file__
        modulos.append(modulo.__name__)
compartilhada=Path(get_package_share_directory('robo_movel'))
assert str(compartilhada).startswith('/work/install/')
metadados=json.loads((compartilhada/'descricao/origem-cad.json').read_text())
for malha in metadados['meshes']:
    assert hashlib.sha256((compartilhada/malha['arquivo']).read_bytes()).hexdigest()==malha['sha256']
politica=json.loads(Path('/workspace/docs/nomenclatura-ros.json').read_text())
for antigo in politica['termos_proibidos']:
    assert importlib.util.find_spec(antigo) is None
    resultado=subprocess.run(['ros2','pkg','prefix',antigo],capture_output=True,text=True)
    assert resultado.returncode!=0
    assert not (Path('/work/install')/antigo).exists()
subprocess.run(['check_urdf',str(compartilhada/'descricao/robo_movel.urdf')],check=True)
resultado={'status':'OK','pacote':'robo_movel','importacao_instalada':robo_movel.__file__,'modulos_importados':sorted(modulos),'malhas_verificadas':len(metadados['meshes']),'identidade_anterior_ausente_na_instalacao':True}
Path('/work/validacao-instalacao.json').write_text(json.dumps(resultado,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(resultado,ensure_ascii=False))
PY
  python3 -u /workspace/docs/descricao-ros/validar-tf.py /work
  LIBGL_ALWAYS_SOFTWARE=1 python3 -u /workspace/docs/descricao-ros/validar-visualizacao.py /work
elif [ "${1:-}" = testar ]; then
  source /work/install/setup.bash
  colcon test --base-paths /workspace/src --packages-select robo_movel --event-handlers console_direct+
  colcon test-result --verbose
  python3 - <<'PY'
from pathlib import Path
import xml.etree.ElementTree as ET
arquivos=list(Path('/work/build/robo_movel').rglob('*.xml'))
relatorios=[]
for arquivo in arquivos:
    raiz=ET.parse(arquivo).getroot()
    casos=raiz.findall('.//testcase')
    if casos:
        assert not raiz.findall('.//failure') and not raiz.findall('.//error')
        relatorios.append({'arquivo':str(arquivo),'casos':len(casos)})
assert relatorios, 'Nenhum caso de teste executado'
print(relatorios)
PY
else
  printf 'Uso: bash validar-identidade.sh construir|testar\n' >&2
  exit 2
fi
