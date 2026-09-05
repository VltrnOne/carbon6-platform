#!/usr/bin/env bash
set -euo pipefail

# NEO Project Scanner — discovers, locates, and audits projects across the filesystem.
# Usage:
#   neo-project-scan.sh              → Top 10 most recently modified projects
#   neo-project-scan.sh <name>       → Locate and audit a specific project
#   neo-project-scan.sh --all        → List all discovered projects

SEARCH_DIRS=(
  "/Users/Morpheous"
  "/Users/Morpheous/vltrndataroom"
  "/Users/Morpheous/weapons"
)
MAX_DEPTH=2

target="${1:-}"

# --- Locate a specific project by name ---
locate_project() {
  local name="$1"
  local found=""
  # Fast: check known directories first (case-insensitive)
  for hub in "${SEARCH_DIRS[@]}"; do
    match=$(ls -1 "$hub" 2>/dev/null | grep -i "^${name}$" | head -1)
    if [[ -n "$match" ]]; then
      found="$hub/$match"
      break
    fi
  done
  # Broader: partial match
  if [[ -z "$found" ]]; then
    for hub in "${SEARCH_DIRS[@]}"; do
      match=$(ls -1 "$hub" 2>/dev/null | grep -i "$name" | head -1)
      if [[ -n "$match" ]]; then
        found="$hub/$match"
        break
      fi
    done
  fi
  # Spotlight fallback
  if [[ -z "$found" ]]; then
    found=$(mdfind "kMDItemFSName == '*${name}*' && kMDItemContentType == 'public.folder'" 2>/dev/null | grep -i "$name" | head -1)
  fi
  echo "$found"
}

# --- Audit a project directory ---
audit_project() {
  local dir="$1"
  local name=$(basename "$dir")
  echo "=== PROJECT: $name ==="
  echo "Path: $dir"

  # Git state
  if [[ -d "$dir/.git" ]]; then
    echo ""
    echo "--- Git State ---"
    echo "Branch: $(git -C "$dir" branch --show-current 2>/dev/null || echo 'detached')"
    local status=$(git -C "$dir" status --porcelain 2>/dev/null | wc -l | tr -d ' ')
    if [[ "$status" == "0" ]]; then
      echo "Status: Clean"
    else
      echo "Status: DIRTY ($status modified files)"
      git -C "$dir" status --short 2>/dev/null | head -5
      [[ "$status" -gt 5 ]] && echo "  ... and $((status - 5)) more"
    fi
    echo ""
    echo "--- Last 3 Commits ---"
    git -C "$dir" log --oneline -3 2>/dev/null || echo "  (no commits)"
  else
    echo "Git: Not a git repository"
  fi

  # Stack detection
  echo ""
  echo "--- Stack ---"
  [[ -f "$dir/package.json" ]] && echo "Node.js: $(python3 -c "import json; d=json.load(open('$dir/package.json')); print(d.get('name','?'), 'v'+d.get('version','?'))" 2>/dev/null)"
  [[ -f "$dir/requirements.txt" ]] && echo "Python: requirements.txt present"
  [[ -f "$dir/pyproject.toml" ]] && echo "Python: pyproject.toml present"
  [[ -f "$dir/Cargo.toml" ]] && echo "Rust: Cargo.toml present"
  [[ -f "$dir/hardhat.config.js" || -f "$dir/hardhat.config.ts" ]] && echo "Solidity: Hardhat project"
  [[ -f "$dir/next.config.js" || -f "$dir/next.config.ts" || -f "$dir/next.config.mjs" ]] && echo "Next.js project"
  [[ -f "$dir/docker-compose.yml" || -f "$dir/Dockerfile" ]] && echo "Docker: containerized"

  # README excerpt
  local readme=""
  for f in README.md readme.md README.txt; do
    [[ -f "$dir/$f" ]] && readme="$dir/$f" && break
  done
  if [[ -n "$readme" ]]; then
    echo ""
    echo "--- README (first 8 lines) ---"
    head -8 "$readme"
  fi

  echo ""
}

# --- Top N most recently modified projects ---
top_projects() {
  local n="${1:-10}"
  local projects=()
  for hub in "${SEARCH_DIRS[@]}"; do
    while IFS= read -r dir; do
      [[ -d "$dir" ]] || continue
      local name=$(basename "$dir")
      # Skip hidden dirs and node_modules
      [[ "$name" == .* || "$name" == "node_modules" ]] && continue
      # Get modification time
      local mtime=$(stat -f "%m" "$dir" 2>/dev/null || stat -c "%Y" "$dir" 2>/dev/null || echo "0")
      projects+=("$mtime|$dir")
    done < <(find "$hub" -maxdepth 1 -type d 2>/dev/null)
  done

  echo "=== TOP $n RECENTLY MODIFIED PROJECTS ==="
  echo ""
  printf '%s\n' "${projects[@]}" | sort -t'|' -k1 -rn | head -"$n" | while IFS='|' read -r mtime dir; do
    local name=$(basename "$dir")
    local date=$(date -r "$mtime" "+%Y-%m-%d %H:%M" 2>/dev/null || echo "unknown")
    local git_status=""
    if [[ -d "$dir/.git" ]]; then
      local branch=$(git -C "$dir" branch --show-current 2>/dev/null || echo "?")
      local dirty=$(git -C "$dir" status --porcelain 2>/dev/null | wc -l | tr -d ' ')
      [[ "$dirty" == "0" ]] && git_status="[$branch, clean]" || git_status="[$branch, $dirty dirty]"
    else
      git_status="[no git]"
    fi
    printf "  %-30s %-20s %s\n" "$name" "$date" "$git_status"
  done
  echo ""
}

# --- Main ---
if [[ -z "$target" || "$target" == "--top" ]]; then
  top_projects 10
elif [[ "$target" == "--all" ]]; then
  top_projects 50
else
  path=$(locate_project "$target")
  if [[ -z "$path" || ! -d "$path" ]]; then
    echo "Error: Project '$target' not found in search hubs."
    echo "Searched: ${SEARCH_DIRS[*]}"
    exit 1
  fi
  audit_project "$path"
fi
