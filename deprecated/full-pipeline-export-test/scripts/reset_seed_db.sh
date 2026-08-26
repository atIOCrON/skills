#!/usr/bin/env bash
# Reset data/database.db from the newest Cameron Sino full-scrape seed
# database. Prints the chosen seed filename.
# Exit codes: 3 = no matching seed database found.
set -euo pipefail

seed_db="$(ls -t data/database\ full\ data\ download\ with\ only\ scraped\ table_cim_*.db 2>/dev/null | head -1 || true)"

if [ -z "$seed_db" ]; then
  echo "error: no seed database matching 'data/database full data download with only scraped table_cim_*.db'" >&2
  exit 3
fi

rm -f data/database.db
cp "$seed_db" data/database.db
echo "seed database copied: $seed_db"
