#!/usr/bin/env bash
# Validate that at most one open successor MR targets a source branch, and
# that it matches the expected successor IID. Prints successor_count and
# successor_iid for the caller to record.
# Exit codes: 0 = valid, 2 = usage, 3 = glab/jq unavailable,
# 4 = GitLab query failed, 5 = multiple successors, 6 = unexpected successor,
# 7 = invalid expected IID.
set -euo pipefail

if [ "$#" -ne 2 ]; then
  echo "usage: validate_successor_mr.sh <source-branch> <expected-successor-iid-or-null>" >&2
  exit 2
fi

source_branch="$1"
expected_iid="$2"
script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"

if ! eval "$("$script_dir/ensure_glab.sh")"; then
  exit 3
fi

case "$expected_iid" in
  null)
    ;;
  ''|*[!0-9]*)
    echo "error: expected successor IID must be numeric or null" >&2
    exit 7
    ;;
esac

if ! successor_json="$(glab mr list --target-branch "$source_branch" --output json)"; then
  echo "error: failed to query open MRs targeting $source_branch" >&2
  exit 4
fi

successor_count="$(printf '%s\n' "$successor_json" | jq -r 'length')"

if [ "$successor_count" -gt 1 ]; then
  echo "error: multiple open MRs target $source_branch:" >&2
  printf '%s\n' "$successor_json" | jq -r '.[] | "  iid=\(.iid) source=\(.source_branch // .sourceBranch // "unknown")"' >&2
  exit 5
fi

if [ "$expected_iid" = "null" ]; then
  if [ "$successor_count" -ne 0 ]; then
    actual_iid="$(printf '%s\n' "$successor_json" | jq -r '.[0].iid')"
    echo "error: expected no successor MR targeting $source_branch, found IID $actual_iid" >&2
    exit 6
  fi
  echo "successor_count=0"
  echo "successor_iid=null"
  exit 0
fi

if [ "$successor_count" -ne 1 ]; then
  echo "error: expected successor MR IID $expected_iid targeting $source_branch, found none" >&2
  exit 6
fi

actual_iid="$(printf '%s\n' "$successor_json" | jq -r '.[0].iid')"
if [ "$actual_iid" != "$expected_iid" ]; then
  echo "error: expected successor MR IID $expected_iid targeting $source_branch, found IID $actual_iid" >&2
  exit 6
fi

echo "successor_count=1"
echo "successor_iid=$actual_iid"
