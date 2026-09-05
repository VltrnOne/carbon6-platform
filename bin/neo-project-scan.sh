#!/usr/bin/env bash
set -euo pipefail

# NEO Project Scanner v2 — Evidence-weighted multi-candidate resolution.
# Never stops at first match. Scores all candidates. Stubs never override production.
#
# Usage:
#   neo-project-scan.sh              → Top 10 most recently modified projects
#   neo-project-scan.sh <name>       → Locate, score, and audit best candidate
#   neo-project-scan.sh --all        → List all discovered projects

SEARCH_HUBS=(
  "/Users/Morpheous/vltrndataroom"
  "/Users/Morpheous"
  "/Users/Morpheous/weapons"
)

# Hub priority bonuses (higher = more likely to be production)
hub_bonus() {
  case "$1" in
    */vltrndataroom) echo 25 ;;
    */weapons)       echo 0 ;;
    *)               echo 10 ;;
  esac
}

target="${1:-}"

# --- Score a candidate directory ---
score_candidate() {
  local dir="$1"
  local hub="$2"
  local score=0
  local evidence=""

  # Git repo
  if [[ -d "$dir/.git" ]]; then
    score=$((score + 50))
    evidence="${evidence}git(+50) "
  fi

  # Project manifests
  for manifest in package.json Cargo.toml pyproject.toml requirements.txt go.mod Gemfile composer.json; do
    if [[ -f "$dir/$manifest" ]]; then
      score=$((score + 30))
      evidence="${evidence}${manifest}(+30) "
      break
    fi
  done
  # Hardhat special case
  for hh in hardhat.config.js hardhat.config.ts; do
    if [[ -f "$dir/$hh" ]]; then
      [[ "$evidence" != *"+30"* ]] && score=$((score + 30)) && evidence="${evidence}${hh}(+30) "
      break
    fi
  done

  # Documentation
  local has_docs=false
  for doc in README.md ARCHITECTURE.md docs; do
    if [[ -e "$dir/$doc" ]]; then
      has_docs=true
      break
    fi
  done
  if $has_docs; then
    score=$((score + 20))
    evidence="${evidence}docs(+20) "
  fi

  # File count > 5
  local fcount=$(find "$dir" -maxdepth 1 -type f 2>/dev/null | wc -l | tr -d ' ')
  if [[ "$fcount" -gt 5 ]]; then
    score=$((score + 10))
    evidence="${evidence}files:${fcount}(+10) "
  fi

  # Hub priority bonus
  local bonus=$(hub_bonus "$hub")
  if [[ "$bonus" -gt 0 ]]; then
    score=$((score + bonus))
    evidence="${evidence}hub(+${bonus}) "
  fi

  echo "${score}|${dir}|${hub}|${evidence}"
}

# --- Find ALL candidates for a name across all hubs ---
find_candidates() {
  local name="$1"
  local candidates=()

  for hub in "${SEARCH_HUBS[@]}"; do
    [[ ! -d "$hub" ]] && continue
    # Exact match (case-insensitive)
    while IFS= read -r match; do
      [[ -d "$hub/$match" ]] && candidates+=("$(score_candidate "$hub/$match" "$hub")")
    done < <(ls -1 "$hub" 2>/dev/null | grep -i "^${name}$")

    # Prefix match (case-insensitive) — excludes exact matches already found
    while IFS= read -r match; do
      local full="$hub/$match"
      [[ -d "$full" ]] || continue
      # Skip if already found as exact
      local already=false
      for c in "${candidates[@]}"; do
        [[ "$c" == *"|$full|"* ]] && already=true && break
      done
      $already || candidates+=("$(score_candidate "$full" "$hub")")
    done < <(ls -1 "$hub" 2>/dev/null | grep -i "^${name}" | grep -iv "^${name}$")

    # Substring match — only if no exact/prefix hits yet
    if [[ ${#candidates[@]} -eq 0 ]]; then
      while IFS= read -r match; do
        [[ -d "$hub/$match" ]] && candidates+=("$(score_candidate "$hub/$match" "$hub")")
      done < <(ls -1 "$hub" 2>/dev/null | grep -i "$name")
    fi
  done

  # Sort by score descending
  printf '%s\n' "${candidates[@]}" | sort -t'|' -k1 -rn
}

# --- Full audit of a directory ---
audit_project() {
  local dir="$1"
  local score="${2:-?}"
  local evidence="${3:-}"
  local name=$(basename "$dir")

  echo "Path: $dir"
  echo "Score: $score  Evidence: $evidence"
  echo ""

  # Git state
  if [[ -d "$dir/.git" ]]; then
    echo "--- Git State ---"
    echo "Branch: $(git -C "$dir" branch --show-current 2>/dev/null || echo 'detached')"
    local dirty=$(git -C "$dir" status --porcelain 2>/dev/null | wc -l | tr -d ' ')
    [[ "$dirty" == "0" ]] && echo "Status: Clean" || echo "Status: DIRTY ($dirty modified files)"
    echo ""
    echo "--- Last 5 Commits ---"
    git -C "$dir" log --oneline -5 2>/dev/null || echo "  (no commits)"
  else
    echo "--- Not a Git Repo ---"
    echo "File manifest:"
    ls -1 "$dir" 2>/dev/null | head -15
    local total=$(ls -1 "$dir" 2>/dev/null | wc -l | tr -d ' ')
    [[ "$total" -gt 15 ]] && echo "  ... ($total total entries)"
  fi

  # Stack detection
  echo ""
  echo "--- Stack ---"
  [[ -f "$dir/package.json" ]] && python3 -c "import json; d=json.load(open('$dir/package.json')); print(f'Node: {d.get(\"name\",\"?\")} v{d.get(\"version\",\"?\")}')" 2>/dev/null
  [[ -f "$dir/requirements.txt" ]] && echo "Python: requirements.txt"
  [[ -f "$dir/pyproject.toml" ]] && echo "Python: pyproject.toml"
  [[ -f "$dir/Cargo.toml" ]] && echo "Rust: Cargo.toml"
  [[ -f "$dir/hardhat.config.js" || -f "$dir/hardhat.config.ts" ]] && echo "Solidity: Hardhat"
  [[ -f "$dir/next.config.js" || -f "$dir/next.config.ts" || -f "$dir/next.config.mjs" ]] && echo "Next.js"
  [[ -f "$dir/docker-compose.yml" || -f "$dir/Dockerfile" ]] && echo "Docker: containerized"

  # README excerpt
  for f in README.md readme.md README.txt; do
    if [[ -f "$dir/$f" ]]; then
      echo ""
      echo "--- README (first 8 lines) ---"
      head -8 "$dir/$f"
      break
    fi
  done
  echo ""
}

# --- Top N most recently modified projects ---
top_projects() {
  local n="${1:-10}"
  local projects=()
  for hub in "${SEARCH_HUBS[@]}"; do
    [[ ! -d "$hub" ]] && continue
    while IFS= read -r dir; do
      [[ -d "$dir" ]] || continue
      local name=$(basename "$dir")
      [[ "$name" == .* || "$name" == "node_modules" ]] && continue
      local mtime=$(stat -f "%m" "$dir" 2>/dev/null || echo "0")
      local git_info="[no git]"
      if [[ -d "$dir/.git" ]]; then
        local branch=$(git -C "$dir" branch --show-current 2>/dev/null || echo "?")
        local dirty=$(git -C "$dir" status --porcelain 2>/dev/null | wc -l | tr -d ' ')
        [[ "$dirty" == "0" ]] && git_info="[$branch, clean]" || git_info="[$branch, $dirty dirty]"
      fi
      local date=$(date -r "$mtime" "+%Y-%m-%d %H:%M" 2>/dev/null || echo "?")
      projects+=("$mtime|$name|$date|$git_info|$hub")
    done < <(find "$hub" -maxdepth 1 -type d 2>/dev/null)
  done

  echo "=== TOP $n RECENTLY MODIFIED PROJECTS ==="
  echo ""
  printf '%s\n' "${projects[@]}" | sort -t'|' -k1 -rn | awk -F'|' '!seen[$2]++' | head -"$n" | while IFS='|' read -r _ name date git_info hub; do
    local hub_label=$(basename "$hub")
    printf "  %-28s %-18s %-28s %s\n" "$name" "$date" "$git_info" "($hub_label)"
  done
  echo ""
}

# --- Main ---
if [[ -z "$target" || "$target" == "--top" ]]; then
  top_projects 10
elif [[ "$target" == "--all" ]]; then
  top_projects 50
else
  candidates=$(find_candidates "$target")
  if [[ -z "$candidates" ]]; then
    echo "Error: No candidates found for '$target'."
    echo "Searched: ${SEARCH_HUBS[*]}"
    exit 1
  fi

  count=$(echo "$candidates" | wc -l | tr -d ' ')
  primary=$(echo "$candidates" | head -1)
  p_score=$(echo "$primary" | cut -d'|' -f1)
  p_path=$(echo "$primary" | cut -d'|' -f2)
  p_evidence=$(echo "$primary" | cut -d'|' -f4)

  echo "=== PROJECT: $(basename "$p_path") ==="
  echo "Candidates found: $count"
  echo ""
  echo "--- ACTIVE_ROOT (highest score) ---"
  audit_project "$p_path" "$p_score" "$p_evidence"

  if [[ "$count" -gt 1 ]]; then
    echo "--- ALTERNATIVE_CANDIDATES ---"
    echo "$candidates" | tail -n +2 | while IFS='|' read -r score path hub evidence; do
      printf "  Score %-4s %-50s %s\n" "$score" "$path" "$evidence"
    done
    echo ""
  fi
fi
