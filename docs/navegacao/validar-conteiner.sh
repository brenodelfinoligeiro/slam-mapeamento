#!/usr/bin/env bash
set -eo pipefail
RAIZ="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
SAIDA="${1:?Informe diretório absoluto novo}"
[[ "$SAIDA" = /* && ! -e "$SAIDA" ]] || { printf '%s\n' 'Saída deve ser absoluta e nova' >&2; exit 2; }
mkdir -p "$SAIDA/cache" "$SAIDA/runtime"; chmod 700 "$SAIDA/runtime"
docker run --rm --init --network none --read-only --cap-drop ALL --security-opt no-new-privileges \
 --tmpfs /tmp:rw,nosuid,nodev,size=512m --cpus 6 --memory 7g --pids-limit 768 \
 --user "$(id -u):$(id -g)" --workdir /work -e HOME=/work -e TMPDIR=/work/cache \
 -e XDG_RUNTIME_DIR=/work/runtime -e XDG_CACHE_HOME=/work/cache -e PYTHONPYCACHEPREFIX=/work/bytecode \
 -e MAKEFLAGS=-j2 -e ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST -e NAV2_TESTAR_RUNTIME=1 \
 -v "$RAIZ:/workspace:ro" -v "$SAIDA:/work:rw" robo-movel/navegacao:jazzy bash -c '
   set -eo pipefail
   source /opt/ros/jazzy/setup.bash
   colcon list --base-paths /workspace/src
   colcon build --base-paths /workspace/src --executor sequential
   source /work/install/setup.bash
   colcon test --base-paths /workspace/src --executor sequential --return-code-on-test-failure
   colcon test-result --verbose
   python3 -m pytest -p no:cacheprovider -o python_files=teste_*.py -o python_functions=teste_* -q /workspace/docs/navegacao/testes --junitxml=/work/oraculo.xml
   python3 /workspace/docs/navegacao/validar-navegacao.py /work/fluxo
   python3 /workspace/docs/navegacao/validar-navegacao.py /work/reinicio --reinicio
   python3 /workspace/docs/navegacao/validar-navegacao.py /work/localizacao --reinicio --modo localizacao --grafo /workspace/docs/slam/mapas/ensaio
   python3 /workspace/docs/navegacao/validar-visualizacao.py /work/visualizacao
 '
