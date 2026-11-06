#!/usr/bin/env bash
# Runtime isolado, fonte somente leitura e nenhum dispositivo do host.
set -eo pipefail
RAIZ="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
SAIDA="${1:?Informe diretório absoluto novo para resultados}"
[[ "$SAIDA" = /* ]] || { printf '%s\n' 'Saída precisa ser absoluta' >&2; exit 2; }
[[ ! -e "$SAIDA" ]] || { printf '%s\n' 'Preservando saída existente; escolha outro diretório' >&2; exit 2; }
mkdir -p "$SAIDA/cache"
docker run --rm --init --network none --cap-drop ALL --security-opt no-new-privileges \
 --read-only --tmpfs /tmp:rw,nosuid,nodev,size=256m --cpus 4 --memory 6g --pids-limit 512 \
 --user "$(id -u):$(id -g)" --workdir /work \
 -e HOME=/work -e TMPDIR=/work/cache -e XDG_CACHE_HOME=/work/cache -e XDG_RUNTIME_DIR=/work/runtime \
 -e PYTHONPYCACHEPREFIX=/work/bytecode -e ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST \
 -e MAKEFLAGS=-j2 -e PYTEST_ADDOPTS='-o cache_dir=/work/pytest-cache' \
 -v "$RAIZ:/workspace:ro" -v "$SAIDA:/work:rw" robo-movel/slam:jazzy bash -c '
    set -eo pipefail
    mkdir -p /work/runtime; chmod 700 /work/runtime
    source /opt/ros/jazzy/setup.bash
    colcon list --base-paths /workspace/src | tee /work/pacotes.txt
    colcon build --base-paths /workspace/src --executor sequential --event-handlers console_direct+
    source /work/install/setup.bash
    colcon test --base-paths /workspace/src --return-code-on-test-failure --event-handlers console_direct+
    colcon test-result --verbose
    python3 -m pytest -q -o python_files=teste_*.py -o python_functions=teste_* /workspace/docs/slam/testes --junitxml=/work/testes-metricas.xml
    python3 /workspace/docs/simulacao/validar-fluxo.py /work/regressao-base
    python3 /workspace/docs/slam/validar-slam.py /work/mapeamento --grafo /work/mapas/ensaio
    python3 /workspace/docs/slam/validar-slam.py /work/localizacao --modo localizacao --grafo /work/mapas/ensaio
    python3 /workspace/docs/slam/validar-negativos.py
    python3 /workspace/docs/slam/validar-visualizacao.py /work/rviz
  '
