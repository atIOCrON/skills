#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 4 ]; then
  echo "usage: validate_successor_change.sh <provider> <remote> <source-branch> <expected-id-or-null>" >&2
  exit 2
fi

provider="$1"
remote="$2"
source_branch="$3"
expected_id="$4"
script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"

changes="$("$script_dir/provider.sh" "$provider" "$remote" list-by-target "$source_branch")" || {
  echo "error: cannot list open changes targeting $source_branch" >&2
  exit 4
}
count="$(printf '%s' "$changes" | jq -r 'length')"

if [ "$count" -gt 1 ]; then
  echo "error: multiple open changes target $source_branch:" >&2
  printf '%s' "$changes" | jq -r '.[] | "  id=\(.id) source=\(.source_branch)"' >&2
  exit 5
fi

if [ "$expected_id" = null ]; then
  [ "$count" -eq 0 ] || {
    echo "error: expected no successor targeting $source_branch; found $(printf '%s' "$changes" | jq -r '.[0].id')" >&2
    exit 6
  }
  echo "successor_count=0"
  echo "successor_id=null"
  exit 0
fi

[ "$count" -eq 1 ] || {
  echo "error: expected successor $expected_id targeting $source_branch; found none" >&2
  exit 6
}
actual_id="$(printf '%s' "$changes" | jq -r '.[0].id')"
[ "$actual_id" = "$expected_id" ] || {
  echo "error: expected successor $expected_id targeting $source_branch; found $actual_id" >&2
  exit 6
}

echo "successor_count=1"
echo "successor_id=$actual_id"
