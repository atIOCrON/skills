#!/usr/bin/env bash
# Poll a merge request's pipeline status for the given head SHA via glab,
# every 30 seconds for at most 20 minutes.
# Exit codes: 0 = success, 2 = usage, 3 = glab/jq unavailable,
# 4 = pipeline failed, 5 = pipeline canceled, 6 = pipeline unexpectedly
# skipped, 7 = timeout.
set -euo pipefail

if [ "$#" -ne 2 ]; then
  echo "usage: wait_for_mr_pipeline.sh <mr-iid-or-url> <head-sha>" >&2
  exit 2
fi

mr="$1"
head_sha="$2"
interval=30
max_wait=1200

if ! command -v glab >/dev/null 2>&1; then
  if [ -x /opt/homebrew/bin/brew ]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
  fi
fi
if ! command -v glab >/dev/null 2>&1; then
  echo "error: glab not found on PATH" >&2
  exit 3
fi
if ! command -v jq >/dev/null 2>&1; then
  echo "error: jq not found on PATH" >&2
  exit 3
fi

elapsed=0
status=""
while :; do
  if ! view="$(glab mr view "$mr" --output json)"; then
    view=""
  fi
  if [ -z "$view" ]; then
    mr_sha=""
    status=""
    echo "waiting: glab query failed; retrying"
  else
    mr_sha="$(printf '%s' "$view" | jq -r '.sha // empty')"
    status="$(printf '%s' "$view" | jq -r '.head_pipeline.status // .pipeline.status // empty')"
  fi

  if [ -z "$view" ]; then
    : # already reported the failed query above
  elif [ "$mr_sha" != "$head_sha" ]; then
    echo "waiting: MR head is ${mr_sha:-unknown}, expected $head_sha (GitLab not refreshed yet)"
  elif [ -z "$status" ]; then
    echo "waiting: no pipeline reported yet for $head_sha"
  else
    echo "pipeline status: $status (elapsed ${elapsed}s)"
    case "$status" in
      success)
        exit 0
        ;;
      failed)
        echo "error: pipeline failed for $head_sha" >&2
        exit 4
        ;;
      canceled|cancelled)
        echo "error: pipeline canceled for $head_sha" >&2
        exit 5
        ;;
      skipped)
        echo "error: pipeline unexpectedly skipped for $head_sha" >&2
        exit 6
        ;;
    esac
  fi

  if [ "$elapsed" -ge "$max_wait" ]; then
    echo "error: timeout after ${max_wait}s; last observed status: ${status:-none}" >&2
    exit 7
  fi
  sleep "$interval"
  elapsed=$((elapsed + interval))
done
