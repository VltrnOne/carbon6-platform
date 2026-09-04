#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

DEPT="${1:-}"
TASK="${2:-}"
REGISTRY="config/agent-registry.json"
PORT=11437

if [[ -z "$DEPT" || -z "$TASK" ]]; then
  echo "Usage: ./bin/neo-dispatch.sh <department> \"<task description>\""
  echo ""
  echo "Departments:"
  python3 -c "
import json
reg = json.load(open('$REGISTRY'))
for k, v in reg['departments'].items():
    print(f'  {k:20s} -> {v[\"assignedModel\"]:25s} [{v[\"path\"]}]')
"
  exit 1
fi

if [[ ! -f "$REGISTRY" ]]; then
  echo "Error: $REGISTRY not found."
  exit 1
fi

# Extract model and target path from registry
MODEL=$(python3 -c "import json; reg=json.load(open('$REGISTRY')); print(reg['departments']['$DEPT']['assignedModel'])" 2>/dev/null || true)
TARGET_PATH=$(python3 -c "import json; reg=json.load(open('$REGISTRY')); print(reg['departments']['$DEPT']['path'])" 2>/dev/null || true)

if [[ -z "$MODEL" || -z "$TARGET_PATH" ]]; then
  echo "Error: Unknown department '$DEPT' in $REGISTRY."
  exit 1
fi

# Ensure SSH tunnel is up (Lightning GPU → VPS fallback)
if ! lsof -i :$PORT &>/dev/null || ! curl -s --max-time 3 http://localhost:${PORT}/api/tags &>/dev/null; then
  pkill -f "ssh.*${PORT}.*11434" 2>/dev/null
  sleep 0.5
  # Try Lightning GPU first
  if ssh -o ConnectTimeout=5 -o BatchMode=yes -f -N -L ${PORT}:127.0.0.1:11434 council-gpu 2>/dev/null; then
    sleep 1
    curl -s --max-time 3 http://localhost:${PORT}/api/tags &>/dev/null && echo "[tunnel] Lightning GPU connected" || {
      pkill -f "ssh.*${PORT}.*council-gpu" 2>/dev/null
      echo "[tunnel] Lightning offline — falling back to VPS..."
      ssh -o ConnectTimeout=5 -f -N -L ${PORT}:127.0.0.1:11434 n8n-vps
      sleep 1
    }
  else
    echo "[tunnel] Lightning unreachable — falling back to VPS..."
    ssh -o ConnectTimeout=5 -f -N -L ${PORT}:127.0.0.1:11434 n8n-vps
    sleep 1
  fi
fi

if ! curl -s --max-time 5 http://localhost:${PORT}/api/tags &>/dev/null; then
  echo "Error: No remote Ollama reachable on :${PORT}."
  exit 1
fi

# Detect if requested model is available, fallback to best available
AVAILABLE=$(curl -s http://localhost:${PORT}/api/tags | python3 -c "import sys,json; print(' '.join(m['name'] for m in json.load(sys.stdin)['models']))" 2>/dev/null)
if ! echo "$AVAILABLE" | grep -q "$MODEL"; then
  FALLBACK=$(echo "$AVAILABLE" | tr ' ' '\n' | grep -E "coder|qwen|glm" | head -1)
  if [[ -n "$FALLBACK" ]]; then
    echo "[model] ${MODEL} not available — using ${FALLBACK}"
    MODEL="$FALLBACK"
  fi
fi

echo ""
echo "=== NEO DISPATCH =========================================="
echo "  Department:  ${DEPT}"
echo "  Model:       ${MODEL}"
echo "  Scope:       ${TARGET_PATH}"
echo "  Task:        ${TASK}"
echo "==========================================================="
echo ""

# Collect target files (JS, TS, JSON — exclude node_modules, lock files)
FILES=$(find "$TARGET_PATH" -type f \( -name "*.js" -o -name "*.ts" -o -name "*.json" \) \
  ! -path "*/node_modules/*" ! -path "*/.aider*" ! -name "package-lock.json" \
  | head -n 8)

if [[ -z "$FILES" ]]; then
  echo "Warning: No source files found in ${TARGET_PATH}."
  exit 1
fi

# Execute non-interactive worker pass via Aider over the L40S tunnel
aider \
  --openai-api-base http://localhost:${PORT}/v1 \
  --openai-api-key ollama \
  --model "openai/${MODEL}" \
  --no-show-model-warnings \
  --yes-always \
  --no-auto-commits \
  --map-tokens 512 \
  --message "You are the specialist agent for ${DEPT} located in ${TARGET_PATH}. Under NEO's strict directive: Complete the following task with ZERO stubs or placeholders: ${TASK}" \
  $FILES

echo ""
echo "=== Worker pass complete. Atomic audit: ==================="
git diff --stat "$TARGET_PATH"
echo ""
git status --short "$TARGET_PATH"
