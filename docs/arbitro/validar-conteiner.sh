#!/usr/bin/env bash
set -eo pipefail
RAIZ="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
SAIDA="${1:?Informe diretório absoluto novo}"
[[ "$SAIDA" = /* && ! -e "$SAIDA" ]] || { printf '%s\n' 'Saída deve ser absoluta e nova' >&2; exit 2; }
mkdir -p "$SAIDA/cache"
docker run --rm --init --network none --read-only --cap-drop ALL --security-opt no-new-privileges \
 --tmpfs /tmp:rw,nosuid,nodev,size=256m --cpus 4 --memory 6g --pids-limit 512 \
 --user "$(id -u):$(id -g)" --workdir /work -e HOME=/work -e TMPDIR=/work/cache \
 -e PYTHONPYCACHEPREFIX=/work/bytecode -e MAKEFLAGS=-j2 -e ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST \
 -v "$RAIZ:/workspace:ro" -v "$SAIDA:/work:rw" robo-movel/slam:jazzy bash -c '
   set -eo pipefail
   source /opt/ros/jazzy/setup.bash
   colcon list --base-paths /workspace/src
   colcon build --base-paths /workspace/src --executor sequential --event-handlers console_direct+
   source /work/install/setup.bash
   colcon test --base-paths /workspace/src --return-code-on-test-failure --event-handlers console_direct+
   colcon test-result --verbose
   python3 /workspace/docs/arbitro/validar-fluxo.py /work/fluxo
   python3 /workspace/docs/arbitro/validar-fluxo.py /work/reinicio --reinicio
 '
