#!/usr/bin/env bash
# Resolve the merge order of a stacked-branch set relative to the base target
# branch from commit counts and ancestry. Prints the ordered branch list as
# "<count> <branch>" lines, ascending.
# Exit codes: 2 = usage, 3 = unresolvable ref, 4 = duplicated commit counts,
# 5 = broken ancestry chain.
set -euo pipefail

if [ "$#" -lt 4 ]; then
  echo "usage: resolve_stack_order.sh <remote> <base-branch> <chained|base-targeted> <source-branch>..." >&2
  exit 2
fi

remote="$1"
target="$2"
layout="$3"
shift 3
case "$layout" in chained|base-targeted) ;; *) echo "error: invalid layout: $layout" >&2; exit 2 ;; esac

git fetch --prune "$remote"

if ! git rev-parse --verify --quiet "$remote/$target" >/dev/null; then
  echo "error: cannot resolve $remote/$target" >&2
  exit 3
fi

pairs=""
branches=""
for branch in "$@"; do
  if ! git rev-parse --verify --quiet "$remote/$branch" >/dev/null; then
    echo "error: cannot resolve $remote/$branch" >&2
    exit 3
  fi
  count="$(git rev-list --count "$remote/$target..$remote/$branch")"
  pairs="${pairs}${count} ${branch}
"
  branches="${branches}${branch}
"
done

if [ "$layout" = base-targeted ]; then
  base_sha="$(git rev-parse "$remote/$target")"
  while read -r left; do
    [ -n "$left" ] || continue
    git merge-base --is-ancestor "$remote/$target" "$remote/$left" || {
      echo "error: $left does not descend from $remote/$target" >&2
      exit 5
    }
    while read -r right; do
      [ -n "$right" ] && [ "$left" != "$right" ] || continue
      if git merge-base --is-ancestor "$remote/$left" "$remote/$right"; then
        echo "error: hidden dependency - $left is an ancestor of $right" >&2
        exit 5
      fi
      shared_sha="$(git merge-base "$remote/$left" "$remote/$right")"
      if [ "$shared_sha" != "$base_sha" ]; then
        echo "error: hidden shared dependency - $left and $right diverge after $remote/$target" >&2
        exit 5
      fi
    done <<EOF
$branches
EOF
  done <<EOF
$branches
EOF
  index=0
  while read -r branch; do
    [ -n "$branch" ] || continue
    index=$((index + 1))
    printf '%s %s\n' "$index" "$branch"
  done <<EOF
$branches
EOF
  exit 0
fi

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
    if ! git merge-base --is-ancestor "$remote/$prev" "$remote/$branch"; then
      echo "error: broken ancestry - $remote/$prev is not an ancestor of $remote/$branch:" >&2
      printf '%s\n' "$ordered" >&2
      exit 5
    fi
  fi
  prev="$branch"
done <<EOF
$ordered
EOF

printf '%s\n' "$ordered"
