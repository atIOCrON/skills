#!/usr/bin/env bash
# Resolve the merge order of a stacked-branch set relative to the base target
# branch from commit counts and ancestry. Prints the ordered branch list as
# "<count> <branch>" lines, ascending.
# Exit codes: 2 = usage, 3 = unresolvable ref, 4 = duplicated commit counts,
# 5 = broken ancestry chain.
set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "usage: resolve_stack_order.sh <base-target-branch> <source-branch>..." >&2
  exit 2
fi

target="$1"
shift

git fetch --prune origin

if ! git rev-parse --verify --quiet "origin/$target" >/dev/null; then
  echo "error: cannot resolve origin/$target" >&2
  exit 3
fi

pairs=""
for branch in "$@"; do
  if ! git rev-parse --verify --quiet "origin/$branch" >/dev/null; then
    echo "error: cannot resolve origin/$branch" >&2
    exit 3
  fi
  count="$(git rev-list --count "origin/$target..origin/$branch")"
  pairs="${pairs}${count} ${branch}
"
done

ordered="$(printf '%s' "$pairs" | sort -n)"

dup="$(printf '%s\n' "$ordered" | awk '{print $1}' | uniq -d)"
if [ -n "$dup" ]; then
  echo "error: ambiguous stack order - duplicated commit counts:" >&2
  printf '%s\n' "$ordered" >&2
  exit 4
fi

prev=""
while read -r count branch; do
  if [ -n "$prev" ]; then
    if ! git merge-base --is-ancestor "origin/$prev" "origin/$branch"; then
      echo "error: broken ancestry - origin/$prev is not an ancestor of origin/$branch:" >&2
      printf '%s\n' "$ordered" >&2
      exit 5
    fi
  fi
  prev="$branch"
done <<EOF
$ordered
EOF

printf '%s\n' "$ordered"
