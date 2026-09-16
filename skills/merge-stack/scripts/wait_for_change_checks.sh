#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 4 ]; then
  echo "usage: wait_for_change_checks.sh <provider> <remote> <change-id> <head-sha>" >&2
  exit 2
fi

provider="$1"
remote="$2"
change_id="$3"
head_sha="$4"
interval="${MERGE_STACK_POLL_INTERVAL:-30}"
max_wait="${MERGE_STACK_MAX_WAIT:-1200}"
script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"

case "$head_sha" in ''|*[!0-9a-fA-F]*) echo "error: head SHA must be hexadecimal" >&2; exit 2 ;; esac
case "$interval:$max_wait" in *[!0-9:]*) echo "error: polling values must be non-negative integers" >&2; exit 2 ;; esac

elapsed=0
while :; do
  if view="$("$script_dir/provider.sh" "$provider" "$remote" get-change "$change_id" 2>/dev/null)"; then
    observed_head="$(printf '%s' "$view" | jq -r '.head_sha // empty')"
    checks="$(printf '%s' "$view" | jq -r '.checks_status // "unknown"')"
    checks_head="$(printf '%s' "$view" | jq -r '.checks_head_sha // empty')"
    if [ "$observed_head" = "$head_sha" ]; then
      echo "checks_status=$checks elapsed=${elapsed}s"
      case "$checks" in
        passed)
          [ "$checks_head" = "$head_sha" ] || {
            echo "error: passing checks apply to ${checks_head:-unknown}, not $head_sha" >&2
            exit 5
          }
          exit 0
          ;;
        failed) echo "error: checks failed for $head_sha" >&2; exit 4 ;;
      esac
    else
      echo "waiting: change head is ${observed_head:-unknown}, expected $head_sha"
    fi
  else
    echo "waiting: provider query failed"
  fi

  if [ "$elapsed" -ge "$max_wait" ]; then
    echo "error: checks did not pass within ${max_wait}s" >&2
    exit 7
  fi
  sleep "$interval"
  elapsed=$((elapsed + interval))
done
