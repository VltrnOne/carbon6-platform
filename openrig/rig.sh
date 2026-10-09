#!/bin/sh
# Thin environment boundary; it never installs tools or copies credentials.
set -eu

if [ -n "${CARBON6_REAL_HOME:-}" ]; then
  carbon6_real_home=$CARBON6_REAL_HOME
elif [ -n "${CODEX_HOME:-}" ]; then
  carbon6_real_home=$(dirname -- "$CODEX_HOME")
else
  carbon6_real_home=${HOME:?HOME is required}
fi
carbon6_runtime_home=${CARBON6_RUNTIME_HOME:-"$carbon6_real_home/.openrig/carbon6-runtime-home"}
carbon6_instance_home=${OPENRIG_HOME:-"$carbon6_real_home/.openrig"}
carbon6_codex_home=${CODEX_HOME:-"$carbon6_real_home/.codex"}
carbon6_node_bin=${CARBON6_NODE_BIN:-/opt/homebrew/opt/node@22/bin}

for carbon6_path in "$carbon6_real_home" "$carbon6_runtime_home" "$carbon6_instance_home" "$carbon6_codex_home" "$carbon6_node_bin"; do
  case "$carbon6_path" in /*) ;; *) echo 'Carbon6 runtime paths must be absolute.' >&2; exit 2 ;; esac
done
if [ "$carbon6_runtime_home" = "$carbon6_real_home" ]; then
  echo 'Runtime HOME must be isolated from the real home skill catalog.' >&2
  exit 2
fi
if [ ! -x "$carbon6_node_bin/node" ]; then
  echo "Supported Node executable missing: $carbon6_node_bin/node" >&2
  exit 2
fi
carbon6_node_major=$("$carbon6_node_bin/node" -p 'process.versions.node.split(".")[0]')
case "$carbon6_node_major" in 22|24) ;; *) echo 'OpenRig requires Node 22 or 24.' >&2; exit 2 ;; esac
if [ "$(uname -s)-$(uname -m)" = Darwin-arm64 ] && [ "$carbon6_node_major" != 22 ]; then
  echo 'Use Node 22 for the verified macOS arm64 compatibility path.' >&2
  exit 2
fi

carbon6_path_env="$carbon6_node_bin:$carbon6_real_home/.npm-global/bin:$carbon6_real_home/.local/bin:${PATH:-/usr/bin:/bin}"
carbon6_rig=$(PATH="$carbon6_path_env" command -v rig) || { echo 'OpenRig CLI is not installed.' >&2; exit 2; }
if [ "${1:-}" = '--environment' ]; then
  printf 'runtime_home=%s\ninstance_home=%s\ncodex_home=%s\nnode=%s\nrig=%s\n' "$carbon6_runtime_home" "$carbon6_instance_home" "$carbon6_codex_home" "$carbon6_node_bin/node" "$carbon6_rig"
  exit 0
fi
mkdir -p "$carbon6_runtime_home/.agents/skills" "$carbon6_runtime_home/.claude/skills"
exec env -u CLAUDE_CONFIG_DIR HOME="$carbon6_runtime_home" OPENRIG_HOME="$carbon6_instance_home" CODEX_HOME="$carbon6_codex_home" PATH="$carbon6_path_env" "$carbon6_rig" "$@"
