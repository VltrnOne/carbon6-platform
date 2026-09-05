#!/usr/bin/env bash
set -euo pipefail

# NEO INIT — Initialize any project for cross-agent coordination.
# Creates a universal handoff layer that Claude, Codex, NEO, Cursor, and Aider can all read.
#
# Usage:
#   neo-init.sh <project_path>           → Initialize a project
#   neo-init.sh <project_path> --sync    → Re-sync state from git/brain
#
# What it creates:
#   .neo/state.md       — Universal handoff document (THE source of truth)
#   .neo/history.jsonl  — Append-only session log
#   CLAUDE.md           — Claude Code reads this (includes .neo/state.md)
#   QWEN.md             — NEO/oh-my-cli reads this (includes .neo/state.md)
#   CODEX.md            — Codex reads this (includes .neo/state.md)
#   .cursorrules        — Cursor reads this (includes .neo/state.md)

PROJECT_PATH="${1:-.}"
SYNC_MODE="${2:-}"
SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ALIAS_FILE="$SCRIPT_DIR/config/project-aliases.json"
BRAIN_QUERY="$SCRIPT_DIR/bin/neo-brain-query.sh"

# Resolve to absolute path
PROJECT_PATH=$(cd "$PROJECT_PATH" 2>/dev/null && pwd || echo "$PROJECT_PATH")
PROJECT_NAME=$(basename "$PROJECT_PATH")

if [[ ! -d "$PROJECT_PATH" ]]; then
  echo "Error: $PROJECT_PATH does not exist."
  exit 1
fi

echo "=== NEO INIT: $PROJECT_NAME ==="
echo "Path: $PROJECT_PATH"
echo ""

# --- 1. Create .neo directory ---
mkdir -p "$PROJECT_PATH/.neo"

# --- 2. Detect project state ---
BRANCH=""
LAST_COMMITS=""
DIRTY_COUNT=0
IS_GIT=false
if [[ -d "$PROJECT_PATH/.git" ]]; then
  IS_GIT=true
  BRANCH=$(git -C "$PROJECT_PATH" branch --show-current 2>/dev/null || echo "detached")
  LAST_COMMITS=$(git -C "$PROJECT_PATH" log --oneline -5 2>/dev/null || echo "none")
  DIRTY_COUNT=$(git -C "$PROJECT_PATH" status --porcelain 2>/dev/null | wc -l | tr -d ' ')
fi

# Detect stack
STACK=""
[[ -f "$PROJECT_PATH/package.json" ]] && STACK="Node.js"
[[ -f "$PROJECT_PATH/requirements.txt" || -f "$PROJECT_PATH/pyproject.toml" ]] && STACK="${STACK:+$STACK, }Python"
[[ -f "$PROJECT_PATH/Cargo.toml" ]] && STACK="${STACK:+$STACK, }Rust"
[[ -f "$PROJECT_PATH/hardhat.config.js" || -f "$PROJECT_PATH/hardhat.config.ts" ]] && STACK="${STACK:+$STACK, }Solidity"
[[ -f "$PROJECT_PATH/next.config.js" || -f "$PROJECT_PATH/next.config.mjs" ]] && STACK="${STACK:+$STACK, }Next.js"
[[ -f "$PROJECT_PATH/docker-compose.yml" ]] && STACK="${STACK:+$STACK, }Docker"
[[ -z "$STACK" ]] && STACK="Unknown"

# Get brain context
BRAIN_CONTEXT=""
if [[ -x "$BRAIN_QUERY" ]]; then
  BRAIN_CONTEXT=$("$BRAIN_QUERY" "$PROJECT_NAME" 2>/dev/null | grep -A1 "^\[" | head -10 || true)
fi

# --- 3. Write .neo/state.md (the universal handoff) ---
if [[ ! -f "$PROJECT_PATH/.neo/state.md" || "$SYNC_MODE" == "--sync" ]]; then
  cat > "$PROJECT_PATH/.neo/state.md" << STATE
# Project State: $PROJECT_NAME

## Location
$PROJECT_PATH

## Stack
$STACK

## Git
$(if $IS_GIT; then echo "Branch: $BRANCH"; echo "Dirty files: $DIRTY_COUNT"; echo ""; echo "Recent commits:"; echo "$LAST_COMMITS"; else echo "Not a git repository"; fi)

## Current Status
<!-- Update this section when you finish a session. ANY agent can read this. -->
Initialized $(date "+%Y-%m-%d %H:%M")

## Decisions Made
<!-- Record architectural decisions here so the next agent doesn't re-derive them. -->

## In Progress
<!-- What's being worked on right now. -->

## Next Action
<!-- The literal first thing the next session should do. -->

## Blockers
<!-- What's stuck and why. -->
STATE
  echo "✓ Created .neo/state.md"
else
  echo "• .neo/state.md exists (use --sync to overwrite)"
fi

# --- 4. Write agent instruction files ---
# Each agent gets a thin file that points to .neo/state.md

# CLAUDE.md (Claude Code)
if [[ ! -f "$PROJECT_PATH/CLAUDE.md" ]]; then
  cat > "$PROJECT_PATH/CLAUDE.md" << 'CLAUDE'
# Project Instructions

Read `.neo/state.md` FIRST — it contains the current project state, decisions, and next action from the last agent session (could have been Codex, NEO, Cursor, or Claude).

## Cross-Agent Protocol
- Before starting work: read `.neo/state.md` for context
- Before ending work: UPDATE `.neo/state.md` with what you did, decisions made, and the next action
- This file is the handoff layer between all agents working on this project
CLAUDE
  echo "✓ Created CLAUDE.md"
fi

# QWEN.md (NEO / oh-my-cli)
if [[ ! -f "$PROJECT_PATH/QWEN.md" ]]; then
  cat > "$PROJECT_PATH/QWEN.md" << 'QWEN'
You are NEO working on this project.
Read `.neo/state.md` FIRST for current state, decisions, and next action.
Before ending: UPDATE `.neo/state.md` with what you did and the next step.
QWEN
  echo "✓ Created QWEN.md"
fi

# CODEX.md (OpenAI Codex)
if [[ ! -f "$PROJECT_PATH/CODEX.md" ]]; then
  cat > "$PROJECT_PATH/CODEX.md" << 'CODEX'
# Project Instructions

Read `.neo/state.md` for current project state, decisions, and next action.
This file is maintained across agent sessions (Claude, NEO, Codex, Cursor).
Before ending your session: update `.neo/state.md` with what you did.
CODEX
  echo "✓ Created CODEX.md"
fi

# .cursorrules (Cursor)
if [[ ! -f "$PROJECT_PATH/.cursorrules" ]]; then
  cat > "$PROJECT_PATH/.cursorrules" << 'CURSOR'
Read .neo/state.md for current project state and cross-agent handoff context.
Update .neo/state.md when you finish working.
CURSOR
  echo "✓ Created .cursorrules"
fi

# --- 5. Initialize session log ---
if [[ ! -f "$PROJECT_PATH/.neo/history.jsonl" ]]; then
  echo "{\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"agent\":\"neo-init\",\"action\":\"initialized\",\"stack\":\"$STACK\"}" > "$PROJECT_PATH/.neo/history.jsonl"
  echo "✓ Created .neo/history.jsonl"
fi

# --- 6. Register alias if not already registered ---
if [[ -f "$ALIAS_FILE" ]]; then
  name_lower=$(echo "$PROJECT_NAME" | tr '[:upper:]' '[:lower:]')
  exists=$(python3 -c "import json; d=json.load(open('$ALIAS_FILE')); print('yes' if '$name_lower' in d else 'no')" 2>/dev/null || echo "no")
  if [[ "$exists" == "no" ]]; then
    # Add to alias registry
    python3 -c "
import json
d = json.load(open('$ALIAS_FILE'))
d['$name_lower'] = '$PROJECT_NAME'
json.dump(d, open('$ALIAS_FILE', 'w'), indent=2)
print('✓ Registered alias: $name_lower → $PROJECT_NAME')
" 2>/dev/null || echo "• Could not register alias"
  fi
fi

# --- 7. Add .neo to .gitignore if git repo ---
if $IS_GIT; then
  if ! grep -q "^\.neo/" "$PROJECT_PATH/.gitignore" 2>/dev/null; then
    echo "" >> "$PROJECT_PATH/.gitignore"
    echo "# NEO cross-agent state (local, not committed)" >> "$PROJECT_PATH/.gitignore"
    echo ".neo/" >> "$PROJECT_PATH/.gitignore"
    echo "✓ Added .neo/ to .gitignore"
  fi
fi

echo ""
echo "=== INIT COMPLETE ==="
echo ""
echo "Cross-agent handoff is ready. Any agent can now:"
echo "  1. Read .neo/state.md for context"
echo "  2. Do work"
echo "  3. Update .neo/state.md before ending"
echo ""
echo "Agents that auto-read instructions:"
echo "  Claude Code  → CLAUDE.md"
echo "  NEO          → QWEN.md"
echo "  Codex        → CODEX.md"
echo "  Cursor       → .cursorrules"
echo "  Aider        → .aider.conf.yml"
