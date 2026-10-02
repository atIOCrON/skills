#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 4 ] || [ "$#" -gt 5 ]; then
  echo "usage: wait_for_change_checks.sh <provider> <remote> <change-id> <head-sha> [squash|merge-commit]" >&2
  exit 2
fi

provider="$1"
remote="$2"
change_id="$3"
head_sha="$4"
method="${5:-merge-commit}"
case "$method" in squash|merge-commit) ;; *) echo "error: unsupported merge method" >&2; exit 2 ;; esac
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
        not-required)
          if printf '%s' "$view" | jq -e '.provider == "bitbucket-cloud" and .policy_status == "passed"' >/dev/null; then
            exit 0
          fi
          if [ "$method" = merge-commit ]; then
            echo "error: repository merge requirements are not satisfied" >&2; exit 5;
          fi
          ;;
        passed)
          [ "$checks_head" = "$head_sha" ] || {
            echo "error: passing checks apply to ${checks_head:-unknown}, not $head_sha" >&2
            exit 5
          }
          exit 0
          ;;
        failed) echo "error: checks failed for $head_sha" >&2; exit 4 ;;
        unknown|missing)
          if [ "$method" = merge-commit ]; then
            echo "error: required check evidence is missing or unknown" >&2; exit 5;
          fi
          ;;
      esac
    else
      if [ "$method" = merge-commit ]; then
        echo "error: release source head moved" >&2; exit 5;
      fi
      echo "waiting: change head is ${observed_head:-unknown}, expected $head_sha"
    fi
  else
    if [ "$method" = merge-commit ]; then
      echo "error: cannot query release checks" >&2; exit 5;
    fi
    echo "waiting: provider query failed"
  fi

  if [ "$elapsed" -ge "$max_wait" ]; then
    echo "error: checks did not pass within ${max_wait}s" >&2
    exit 7
  fi
  sleep "$interval"
  elapsed=$((elapsed + interval))
done
