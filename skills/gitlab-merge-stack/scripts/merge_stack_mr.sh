#!/usr/bin/env bash
# Merge a stack MR using the safe source-branch-removal behavior selected by
# the validated successor state.
# Exit codes: 0 = merged, 2 = usage, 3 = glab/jq unavailable,
# 4 = invalid arguments, 5 = removal flag unsafe, 6 = merge failed,
# 7 = GitLab API update/query failed.
set -euo pipefail

if [ "$#" -ne 3 ]; then
  echo "usage: merge_stack_mr.sh <mr-iid> <current-head-sha> <successor-iid-or-null>" >&2
  exit 2
fi

mr_iid="$1"
current_head_sha="$2"
successor_iid="$3"
script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"

if ! eval "$("$script_dir/ensure_glab.sh")"; then
  exit 3
fi

case "$mr_iid" in
  ''|*[!0-9]*)
    echo "error: current MR IID must be numeric" >&2
    exit 4
    ;;
esac

case "$successor_iid" in
  null)
    if ! glab mr merge "$mr_iid" --sha "$current_head_sha" --remove-source-branch --yes; then
      echo "error: failed to merge MR $mr_iid with source branch removal" >&2
      exit 6
    fi
    echo "merge_mode=remove-source-branch"
    exit 0
    ;;
  ''|*[!0-9]*)
    echo "error: successor IID must be numeric or null" >&2
    exit 4
    ;;
esac

if ! glab api -X PUT "projects/:id/merge_requests/$mr_iid" \
  -F remove_source_branch=false >/dev/null; then
  echo "error: failed to clear source branch removal for MR $mr_iid" >&2
  exit 7
fi

if ! mr_json="$(glab api "projects/:id/merge_requests/$mr_iid")"; then
  echo "error: failed to refresh MR $mr_iid after clearing source branch removal" >&2
  exit 7
fi

if ! printf '%s\n' "$mr_json" |
  jq -e '(.should_remove_source_branch != true) and (.force_remove_source_branch != true)' >/dev/null; then
  echo "error: GitLab still reports source branch removal may occur for MR $mr_iid" >&2
  exit 5
fi

if ! glab mr merge "$mr_iid" --sha "$current_head_sha" --yes; then
  echo "error: failed to merge MR $mr_iid while preserving source branch for successor MR $successor_iid" >&2
  exit 6
fi

echo "merge_mode=preserve-source-branch"
echo "successor_iid=$successor_iid"
