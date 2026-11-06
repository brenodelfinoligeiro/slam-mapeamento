#!/usr/bin/env bash
# Sessão interativa headless. Teleop roda via docker exec no MESMO contêiner.
set -eo pipefail
RAIZ="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
SAIDA="${TMPDIR:-$HOME/.hermes/cache/scratch}/robo-movel-sessao"
mkdir -p "$SAIDA/cache"
docker image inspect robo-movel/simulacao:jazzy >/dev/null
exec docker run --rm -it --init --name robo_movel_simulacao --network none   --cap-drop ALL --security-opt no-new-privileges --read-only   --tmpfs /tmp:rw,nosuid,nodev,size=256m --cpus 4 --memory 6g   --user "$(id -u):$(id -g)" --workdir /work   -e HOME=/work -e TMPDIR=/work/cache -e XDG_CACHE_HOME=/work/cache   -e PYTHONPYCACHEPREFIX=/work/bytecode -e MAKEFLAGS=-j2   -e ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST   -v "$RAIZ:/workspace:ro" -v "$SAIDA:/work:rw"   robo-movel/simulacao:jazzy bash -c '
    set -eo pipefail
    source /opt/ros/jazzy/setup.bash
    colcon build --base-paths /workspace/src --executor sequential
    source /work/install/setup.bash
    exec ros2 launch navegacao_simulada simulacao.launch.py rviz:=false
  '
