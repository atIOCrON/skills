#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 4 || ! "$4" =~ ^[0-9]+$ ]]; then
  echo "usage: strict_patch_replay.sh <tree> <patch-file> <log-file> <strip-level>" >&2
  exit 2
fi

tree="$1"
patch_file="$2"
log_file="$3"
strip_level="$4"
[[ -d "$tree" && -f "$patch_file" ]] || { echo "missing tree or patch" >&2; exit 2; }
mkdir -p "$(dirname "$log_file")"

if command -v gpatch >/dev/null 2>&1; then
  patch_cmd=gpatch
elif patch --version 2>/dev/null | grep -q 'GNU patch'; then
  patch_cmd=patch
else
  echo "GNU patch is required: macOS patch can hide line offsets" >&2
  exit 2
fi

status=0
LC_ALL=C "$patch_cmd" --directory "$tree" --strip "$strip_level" --fuzz=0 \
  --batch --forward --input "$patch_file" > "$log_file" 2>&1 || status=$?
if [[ $status -ne 0 ]]; then
  echo "patch failed (exit $status); see $log_file" >&2
  exit "$status"
fi
if LC_ALL=C grep -Eiq '(^|[^[:alpha:]])(fuzz|offset)([^[:alpha:]]|$)' "$log_file"; then
  echo "patch reported fuzz or offset; see $log_file" >&2
  exit 1
fi
