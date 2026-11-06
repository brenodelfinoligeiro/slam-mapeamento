#!/usr/bin/env bash
# Sessão headless; teleop roda por docker exec NO MESMO contêiner.
set -eo pipefail
RAIZ="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
MODO="${1:-mapeamento}"
GRAFO="${2:-/mapas/sala}"
case "$MODO" in mapeamento|localizacao) ;; *) printf '%s\n' 'Modo: mapeamento ou localizacao' >&2; exit 2 ;; esac
SAIDA="${ROBO_SLAM_EXECUCAO:-${TMPDIR:-$HOME/.hermes/cache/scratch}/robo-movel-slam-sessao}"
MAPAS="${ROBO_SLAM_MAPAS:-$HOME/.local/share/robo_movel/mapas}"
[[ "$MAPAS" = /* && "$SAIDA" = /* ]] || { printf '%s\n' 'Diretórios precisam ser absolutos' >&2; exit 2; }
mkdir -p "$SAIDA/cache" "$SAIDA/runtime" "$MAPAS"; chmod 700 "$SAIDA/runtime"
docker image inspect robo-movel/slam:jazzy >/dev/null
exec docker run --rm -it --init --name robo_movel_slam --network none --cap-drop ALL \
 --security-opt no-new-privileges --read-only --tmpfs /tmp:rw,nosuid,nodev,size=256m \
 --cpus 4 --memory 6g --pids-limit 512 --user "$(id -u):$(id -g)" --workdir /work \
 -e HOME=/work -e TMPDIR=/work/cache -e XDG_CACHE_HOME=/work/cache -e XDG_RUNTIME_DIR=/work/runtime \
 -e PYTHONPYCACHEPREFIX=/work/bytecode -e MAKEFLAGS=-j2 -e ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST \
 -v "$RAIZ:/workspace:ro" -v "$SAIDA:/work:rw" -v "$MAPAS:/mapas:rw" \
 robo-movel/slam:jazzy bash -c '
   set -eo pipefail
   source /opt/ros/jazzy/setup.bash
   colcon build --base-paths /workspace/src --executor sequential
   source /work/install/setup.bash
   argumentos=(rviz:=false "modo:=$1")
   if [[ "$1" == localizacao ]]; then argumentos+=("arquivo_grafo:=$2"); fi
   exec ros2 launch mapeamento_slam slam_simulado.launch.py "${argumentos[@]}"
 ' bash "$MODO" "$GRAFO"
