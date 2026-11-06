#!/usr/bin/env bash
# Sessão digital headless; não conecta robô ou dispositivos.
set -eo pipefail
RAIZ="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
MODO="${1:-mapeamento}"; GRAFO="${2:-/mapas/sala}"
case "$MODO" in mapeamento|localizacao) ;; *) printf '%s\n' 'Modo: mapeamento ou localizacao' >&2; exit 2 ;; esac
SAIDA="${ROBO_NAV_EXECUCAO:-${TMPDIR:-$HOME/.hermes/cache/scratch}/robo-movel-navegacao-sessao}"
MAPAS="${ROBO_NAV_MAPAS:-$HOME/.local/share/robo_movel/mapas}"
[[ "$SAIDA" = /* && "$MAPAS" = /* ]] || { printf '%s\n' 'Diretórios devem ser absolutos' >&2; exit 2; }
mkdir -p "$SAIDA/cache" "$SAIDA/runtime" "$MAPAS"; chmod 700 "$SAIDA/runtime"
docker image inspect robo-movel/navegacao:jazzy >/dev/null
exec docker run --rm -it --init --name robo_movel_navegacao --network none --read-only --cap-drop ALL \
 --security-opt no-new-privileges --tmpfs /tmp:rw,nosuid,nodev,size=512m --cpus 6 --memory 7g --pids-limit 768 \
 --user "$(id -u):$(id -g)" --workdir /work -e HOME=/work -e TMPDIR=/work/cache \
 -e XDG_CACHE_HOME=/work/cache -e XDG_RUNTIME_DIR=/work/runtime -e PYTHONPYCACHEPREFIX=/work/bytecode \
 -e MAKEFLAGS=-j2 -e ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST \
 -v "$RAIZ:/workspace:ro" -v "$SAIDA:/work:rw" -v "$MAPAS:/mapas:rw" robo-movel/navegacao:jazzy bash -c '
  set -eo pipefail
  source /opt/ros/jazzy/setup.bash
  colcon build --base-paths /workspace/src --executor sequential
  source /work/install/setup.bash
  argumentos=(rviz:=false "modo:=$1")
  if [[ "$1" == localizacao ]]; then argumentos+=("arquivo_grafo:=$2"); fi
  # Sessão própria impede o SIGINT do TTY de atingir os nós antes do lifecycle.
  encerrar_ordenadamente() {
    trap "" INT TERM
    codigo=0
    ros2 run navegacao_autonoma encerrar || codigo=$?
    kill -INT "$processo" 2>/dev/null || true
    wait "$processo" || true
    exit "$codigo"
  }
  trap encerrar_ordenadamente INT TERM
  setsid env --default-signal=INT,TERM ros2 launch navegacao_autonoma navegacao_simulada.launch.py "${argumentos[@]}" &
  processo=$!
  wait "$processo"
 ' bash "$MODO" "$GRAFO"
