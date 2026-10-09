#!/bin/sh
set -eu

carbon6_repo=${CARBON6_REPO:-"${HOME:?HOME is required}/carbon6-openrig"}
if [ -z "${CARBON6_NODE_BIN:-}" ]; then
  carbon6_node_root=$(find "$HOME/.local/opt" -maxdepth 1 -type d -name 'node-v22*-linux-x64' 2>/dev/null | sort | tail -n 1)
  CARBON6_NODE_BIN=${carbon6_node_root:+"$carbon6_node_root/bin"}
fi
export CARBON6_NODE_BIN
export CODEX_HOME=${CODEX_HOME:-"$HOME/.codex-openrig"}
cd "$carbon6_repo"

stop_daemon() {
  sh openrig/rig.sh daemon stop >/dev/null 2>&1 || true
  exit 0
}
trap stop_daemon INT TERM

if ! sh openrig/rig.sh daemon status >/dev/null 2>&1; then
  sh openrig/rig.sh daemon start --wait-for-kernel --wait-for-kernel-ms 120000
fi

while sleep 30; do
  if ! sh openrig/rig.sh daemon status >/dev/null 2>&1; then
    exit 1
  fi
done
