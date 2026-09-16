#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 3 ]; then
  echo "usage: journal_event.sh <absolute-journal-path> <event> <json-object>" >&2
  exit 2
fi

journal="$1"
event="$2"
data="$3"
case "$journal" in /*) ;; *) echo "error: journal path must be absolute" >&2; exit 2 ;; esac
[ -d "$(dirname "$journal")" ] || {
  echo "error: journal directory does not exist" >&2
  exit 3
}

repo="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [ -n "$repo" ]; then
  case "$journal" in "$repo"/*) echo "error: journal must be outside the repository" >&2; exit 3 ;; esac
fi

line="$(printf '%s' "$data" | jq -ce --arg event "$event" --arg time "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  'if type == "object" then . + {event: $event, time: $time} else error("expected object") end')" || {
  echo "error: journal data must be a JSON object" >&2
  exit 3
}
printf '%s\n' "$line" >> "$journal"
