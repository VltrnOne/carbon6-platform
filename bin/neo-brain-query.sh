#!/usr/bin/env bash
set -euo pipefail

# NEO Brain Query v2 — Unconditional knowledge grounding.
# Git existence NEVER gates brain retrieval. Queries always run.
# Supports alias/acronym expansion and case-insensitive matching.
#
# Usage: neo-brain-query.sh <project_name>

PROJECT="${1:-}"
BRAIN_INDEX="/Users/Morpheous/weapons/brain3/data/brain.json"
VAULT="/Users/Morpheous/Library/Mobile Documents/com~apple~CloudDocs/Documents/Obsidian Vault"

if [[ -z "$PROJECT" ]]; then
  echo "Usage: neo-brain-query.sh <project_name>"
  echo "Unconditionally queries Obsidian Brain (1,447 nodes) for project doctrine."
  echo "Git existence does NOT gate this query."
  exit 1
fi

echo "=== BRAIN QUERY: $PROJECT ==="
echo ""

# --- 1. Brain Index Query (always runs) ---
echo "--- Brain Index Matches ---"
if [[ -f "$BRAIN_INDEX" ]]; then
  python3 -c "
import json, sys, re

project = sys.argv[1]
project_lower = project.lower()
brain = json.load(open(sys.argv[2]))

# Generate search variants: exact, lowercase, uppercase, common abbreviations
variants = {project_lower, project.upper(), project}
# Split on common separators for substring matching
for sep in ['-', '_', ' ']:
    for part in project.split(sep):
        if len(part) > 2:
            variants.add(part.lower())

# Score nodes by relevance
scored = []
for node in brain.get('nodes', []):
    nid = node.get('id', '')
    nid_lower = nid.lower()
    path = node.get('path', '').lower()
    tags = [t.lower() for t in node.get('tags', [])]
    score = 0

    # Exact match in node id
    if project_lower == nid_lower:
        score += 100
    elif project_lower in nid_lower:
        score += 60
    # Path match
    if project_lower in path:
        score += 40
    # Tag match
    for variant in variants:
        if any(variant in t for t in tags):
            score += 30
            break

    if score > 0:
        scored.append((score, node))

scored.sort(key=lambda x: -x[0])

if not scored:
    print(f'  No direct matches for \"{project}\" in brain index.')
    # Check edges for indirect connections
    related = set()
    for edge in brain.get('edges', []):
        src = edge.get('source', '').lower()
        tgt = edge.get('target', '').lower()
        for v in variants:
            if v in src:
                related.add(edge.get('target', ''))
            elif v in tgt:
                related.add(edge.get('source', ''))
    if related:
        print(f'  Indirect connections via edges: {len(related)}')
        for r in list(related)[:8]:
            print(f'    -> {r}')
else:
    print(f'  Found {len(scored)} brain nodes (ranked by relevance):')
    for s, m in scored[:12]:
        tags_str = ', '.join(m.get('tags', [])[:6])
        wc = m.get('wc', 0)
        print(f'    [{m[\"id\"]}] score={s} ({wc} words)')
        print(f'      tags: {tags_str}')
        print(f'      path: {m.get(\"path\", \"?\")}')
" "$PROJECT" "$BRAIN_INDEX" 2>/dev/null || echo "  Error querying brain index."
else
  echo "  Brain index not found at $BRAIN_INDEX"
fi

echo ""

# --- 2. Obsidian Vault Search (always runs, git-independent) ---
echo "--- Vault Notes (Spotlight) ---"
if [[ -d "$VAULT" ]]; then
  results=$(mdfind -onlyin "$VAULT" "$PROJECT" 2>/dev/null | head -15)
  if [[ -n "$results" ]]; then
    count=$(echo "$results" | wc -l | tr -d ' ')
    echo "  Found $count notes mentioning '$PROJECT':"
    echo "$results" | while read -r note; do
      name=$(basename "$note" .md)
      echo "    -> $name"
    done
  else
    # Try uppercase/lowercase variants
    results=$(mdfind -onlyin "$VAULT" "$(echo "$PROJECT" | tr '[:lower:]' '[:upper:]')" 2>/dev/null | head -10)
    if [[ -n "$results" ]]; then
      count=$(echo "$results" | wc -l | tr -d ' ')
      echo "  Found $count notes (uppercase match):"
      echo "$results" | while read -r note; do
        echo "    -> $(basename "$note" .md)"
      done
    else
      echo "  No vault notes found for '$PROJECT'."
    fi
  fi
else
  echo "  Vault not accessible at $VAULT"
fi

echo ""

# --- 3. Doctrine Extraction (top 3 notes, always runs) ---
echo "--- Doctrine & Decision Excerpts ---"
if [[ -n "${results:-}" ]]; then
  echo "$results" | head -3 | while read -r note; do
    if [[ -f "$note" ]]; then
      name=$(basename "$note" .md)
      echo "  [$name]"
      # Extract headings, decisions, TODOs, status markers, and key context
      grep -E "^#{1,3} |TODO|DECISION|BLOCKER|MILESTONE|NEXT|STATUS|IMPORTANT|CRITICAL|DEPLOYED|RETIRED|ACTIVE|ARCHITECTURE|STACK" "$note" 2>/dev/null | head -10 | sed 's/^/    /'
      # If no structured markers found, show first 5 non-empty lines
      marker_count=$(grep -cE "^#{1,3} |TODO|DECISION|BLOCKER|MILESTONE|NEXT|STATUS" "$note" 2>/dev/null || echo "0")
      if [[ "$marker_count" -eq 0 ]]; then
        echo "    (no structured markers — first lines:)"
        grep -v '^$' "$note" 2>/dev/null | head -5 | sed 's/^/    /'
      fi
      echo ""
    fi
  done
else
  echo "  No notes to extract doctrine from."
  echo "  This project has no recorded brain context."
  echo "  NEO should audit the project directory directly for intent and purpose."
fi

echo ""
echo "=== END BRAIN QUERY ==="
