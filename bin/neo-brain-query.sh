#!/usr/bin/env bash
set -euo pipefail

# NEO Brain Query — cross-references a project against the Obsidian Brain index
# and vault markdown notes to surface decisions, doctrine, and context.
# Usage: neo-brain-query.sh <project_name>

PROJECT="${1:-}"
BRAIN_INDEX="/Users/Morpheous/weapons/brain3/data/brain.json"
VAULT="/Users/Morpheous/Library/Mobile Documents/com~apple~CloudDocs/Documents/Obsidian Vault"

if [[ -z "$PROJECT" ]]; then
  echo "Usage: neo-brain-query.sh <project_name>"
  echo "Queries the Obsidian Brain (1,447 nodes) for project-related doctrine and decisions."
  exit 1
fi

echo "=== BRAIN QUERY: $PROJECT ==="
echo ""

# 1. Search brain.json for matching nodes
echo "--- Brain Index Matches ---"
if [[ -f "$BRAIN_INDEX" ]]; then
  python3 -c "
import json, sys, re

project = sys.argv[1].lower()
brain = json.load(open(sys.argv[2]))

# Find nodes whose id or path matches
matches = []
for node in brain.get('nodes', []):
    nid = node.get('id', '').lower()
    path = node.get('path', '').lower()
    tags = [t.lower() for t in node.get('tags', [])]
    if project in nid or project in path or any(project in t for t in tags):
        matches.append(node)

if not matches:
    print(f'  No direct matches for \"{project}\" in brain index.')
    # Fuzzy: check edges for related nodes
    related_ids = set()
    for edge in brain.get('edges', []):
        src = edge.get('source', '').lower()
        tgt = edge.get('target', '').lower()
        if project in src:
            related_ids.add(edge.get('target', ''))
        elif project in tgt:
            related_ids.add(edge.get('source', ''))
    if related_ids:
        print(f'  Related nodes via edges: {len(related_ids)} found')
        for rid in list(related_ids)[:10]:
            print(f'    → {rid}')
else:
    print(f'  Found {len(matches)} brain nodes:')
    for m in matches[:15]:
        tags_str = ', '.join(m.get('tags', [])[:5])
        wc = m.get('wc', 0)
        print(f'    [{m[\"id\"]}] ({wc} words) tags: {tags_str}')
        print(f'      path: {m.get(\"path\", \"?\")}')
" "$PROJECT" "$BRAIN_INDEX" 2>/dev/null || echo "  Error querying brain index."
else
  echo "  Brain index not found at $BRAIN_INDEX"
fi

echo ""

# 2. Search Obsidian vault for matching markdown notes
echo "--- Vault Notes (Spotlight) ---"
if [[ -d "$VAULT" ]]; then
  results=$(mdfind -onlyin "$VAULT" "$PROJECT" 2>/dev/null | head -10)
  if [[ -n "$results" ]]; then
    count=$(echo "$results" | wc -l | tr -d ' ')
    echo "  Found $count notes mentioning '$PROJECT':"
    echo "$results" | while read -r note; do
      name=$(basename "$note" .md)
      echo "    → $name"
    done
  else
    echo "  No vault notes found for '$PROJECT'."
  fi
else
  echo "  Vault not found at $VAULT"
fi

echo ""

# 3. Extract key context from top matching notes
echo "--- Doctrine Excerpts ---"
if [[ -n "${results:-}" ]]; then
  # Read first 3 matching notes, extract key lines
  echo "$results" | head -3 | while read -r note; do
    if [[ -f "$note" ]]; then
      name=$(basename "$note" .md)
      echo "  [$name]"
      # Extract headings and key lines (decisions, TODO, blockers)
      grep -E "^#|TODO|DECISION|BLOCKER|MILESTONE|NEXT|IMPORTANT|CRITICAL|STATUS" "$note" 2>/dev/null | head -8 | sed 's/^/    /'
      echo ""
    fi
  done
fi

echo "=== END BRAIN QUERY ==="
