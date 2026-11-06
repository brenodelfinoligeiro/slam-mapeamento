#!/usr/bin/env bash
# Sem acesso a rede/dispositivos no runtime. Usa a imagem de teste já construída.
set -eo pipefail
RAIZ="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
SAIDA="${1:?Informe diretório absoluto vazio para resultados}"
mkdir -p "$SAIDA/cache"
docker run --rm --init --network none --cap-drop ALL --security-opt no-new-privileges   --read-only --tmpfs /tmp:rw,nosuid,nodev,size=256m --cpus 4 --memory 6g --pids-limit 512   --user "$(id -u):$(id -g)" --workdir /work   -e HOME=/work -e TMPDIR=/work/cache -e XDG_CACHE_HOME=/work/cache   -e PYTHONPYCACHEPREFIX=/work/bytecode -e ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST   -e MAKEFLAGS=-j2 -e PYTEST_ADDOPTS='-o cache_dir=/work/pytest-cache'   -v "$RAIZ:/workspace:ro" -v "$SAIDA:/work:rw"   robo-movel/simulacao:jazzy bash -c '
    set -eo pipefail
    source /opt/ros/jazzy/setup.bash
    colcon list --base-paths /workspace/src
    colcon build --base-paths /workspace/src --executor sequential --event-handlers console_direct+
    source /work/install/setup.bash
    colcon test --base-paths /workspace/src --return-code-on-test-failure --event-handlers console_direct+
    colcon test-result --verbose
    cd /work
    python3 /workspace/docs/simulacao/validar-fluxo.py /work/fluxo
    python3 /workspace/docs/simulacao/validar-fluxo.py /work/reinicio --reinicio
  '
