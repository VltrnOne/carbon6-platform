#!/usr/bin/env bash
set -euo pipefail

# NEO Dispatch — Dual-GPU departmental task router with async validation.
# GPU 0 (:11437) generates code, GPU 1 (:11438) validates before commit.

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

DEPT="${1:-}"
TASK="${2:-}"
REGISTRY="config/agent-registry.json"
VALIDATE="${NEO_VALIDATE:-true}"  # set NEO_VALIDATE=false to skip

if [[ -z "$DEPT" || -z "$TASK" ]]; then
  echo "Usage: ./bin/neo-dispatch.sh <department> \"<task description>\""
  echo "       NEO_VALIDATE=false ./bin/neo-dispatch.sh ...  (skip GPU 1 validation)"
  echo ""
  echo "Departments:"
  python3 -c "
import json
reg = json.load(open('$REGISTRY'))
for k, v in reg['departments'].items():
    port = v.get('port', 11437)
    print(f'  {k:20s} -> {v[\"assignedModel\"]:25s} :{port} [{v[\"path\"]}]')
"
  exit 1
fi

[[ ! -f "$REGISTRY" ]] && echo "Error: $REGISTRY not found." && exit 1

# Extract department config
MODEL=$(python3 -c "import json; reg=json.load(open('$REGISTRY')); print(reg['departments']['$DEPT']['assignedModel'])" 2>/dev/null || true)
TARGET_PATH=$(python3 -c "import json; reg=json.load(open('$REGISTRY')); print(reg['departments']['$DEPT']['path'])" 2>/dev/null || true)
DEPT_PORT=$(python3 -c "import json; reg=json.load(open('$REGISTRY')); print(reg['departments']['$DEPT'].get('port', 11437))" 2>/dev/null || echo "11437")

[[ -z "$MODEL" || -z "$TARGET_PATH" ]] && echo "Error: Unknown department '$DEPT'." && exit 1

# --- Tunnel check ---
for p in 11437 11438; do
  if ! lsof -i :$p &>/dev/null || ! curl -s --max-time 3 http://localhost:${p}/api/tags &>/dev/null; then
    pkill -f "ssh.*vast-gpu" 2>/dev/null
    sleep 0.5
    echo "[tunnel] Establishing dual tunnel to Vast.ai..."
    ssh -o ConnectTimeout=10 -o ServerAliveInterval=10 -o TCPKeepAlive=yes -f -N \
      -L 11437:127.0.0.1:11434 -L 11438:127.0.0.1:11435 vast-gpu 2>/dev/null
    sleep 1
    break
  fi
done

curl -s --max-time 5 http://localhost:${DEPT_PORT}/api/tags &>/dev/null || { echo "Error: GPU not reachable on :${DEPT_PORT}."; exit 1; }

# --- Collect target files ---
FILES=$(find "$TARGET_PATH" -type f \( -name "*.js" -o -name "*.ts" -o -name "*.json" \) \
  ! -path "*/node_modules/*" ! -path "*/.aider*" ! -name "package-lock.json" \
  | head -n 8)

[[ -z "$FILES" ]] && echo "Warning: No source files in ${TARGET_PATH}." && exit 1

echo ""
echo "=== NEO DISPATCH =========================================="
echo "  Phase:       GENERATE (GPU 0 → :${DEPT_PORT})"
echo "  Department:  ${DEPT}"
echo "  Model:       ${MODEL}"
echo "  Scope:       ${TARGET_PATH}"
echo "  Task:        ${TASK}"
echo "==========================================================="
echo ""

# --- PHASE 1: Generate (primary GPU) ---
aider \
  --openai-api-base http://localhost:${DEPT_PORT}/v1 \
  --openai-api-key ollama \
  --model "openai/${MODEL}" \
  --no-show-model-warnings --yes-always --no-auto-commits \
  --map-tokens 512 \
  --message "You are the specialist agent for ${DEPT} located in ${TARGET_PATH}. Under NEO's strict directive: Complete the following task with ZERO stubs or placeholders: ${TASK}" \
  $FILES

echo ""
echo "=== Generation complete. Checking diff... ==================="
DIFF=$(git diff --stat "$TARGET_PATH")
echo "$DIFF"

# --- PHASE 2: Validate (GPU 1 auditor) ---
if [[ "$VALIDATE" == "true" && -n "$DIFF" ]]; then
  echo ""
  echo "=== VALIDATION PASS (GPU 1 → :11438) ======================"

  # Get the actual diff content for the auditor to review
  DIFF_CONTENT=$(git diff "$TARGET_PATH" | head -200)

  # Ask the auditor model to check for issues
  AUDIT_RESULT=$(curl -s --max-time 60 http://localhost:11438/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d "$(python3 -c "
import json, sys
diff = sys.stdin.read()
payload = {
  'model': 'glm4:9b',
  'messages': [{'role': 'user', 'content': 'You are a code auditor. Review this diff for: 1) Syntax errors (missing braces, unclosed strings) 2) Placeholder/stub code (TODO, FIXME, dummy, mock) 3) Dangling imports or references. Reply PASS if clean, or list specific issues.\n\nDiff:\n' + diff}],
  'max_tokens': 200
}
print(json.dumps(payload))
" <<< "$DIFF_CONTENT")" 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin)['choices'][0]['message']['content'])" 2>/dev/null)

  echo "  Auditor: $AUDIT_RESULT"

  if echo "$AUDIT_RESULT" | grep -qi "PASS"; then
    echo "  ✓ Validation PASSED"
  else
    echo "  ⚠ Validation flagged issues — review before committing"
  fi
fi

echo ""
echo "=== Final state ============================================"
git status --short "$TARGET_PATH"
