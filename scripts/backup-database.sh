#!/bin/bash
# Backup Database
set -e

BACKUP_DIR="$HOME/Carbon6/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DATABASE_URL="${DATABASE_URL:-file:./dev.db}"

mkdir -p "$BACKUP_DIR"

if [[ $DATABASE_URL == postgres* ]]; then
  pg_dump $DATABASE_URL | gzip > "$BACKUP_DIR/carbon6_$DATE.sql.gz"
else
  cp dev.db "$BACKUP_DIR/carbon6_$DATE.db" 2>/dev/null || true
fi

find "$BACKUP_DIR" -mtime +30 -delete
echo "✓ Backup created: carbon6_$DATE"
