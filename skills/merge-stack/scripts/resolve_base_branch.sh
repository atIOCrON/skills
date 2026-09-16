#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
  echo "usage: resolve_base_branch.sh <remote> [base-branch]" >&2
  exit 2
fi

remote="$1"
override="${2:-}"
git remote get-url "$remote" >/dev/null 2>&1 || {
  echo "error: unknown remote: $remote" >&2
  exit 3
}

if [ -n "$override" ]; then
  git check-ref-format --branch "$override" >/dev/null || exit 3
  printf '%s\n' "$override"
  exit 0
fi

branch="$(git ls-remote --symref "$remote" HEAD 2>/dev/null | awk '$1 == "ref:" {sub("refs/heads/", "", $2); print $2; exit}')"
if [ -n "$branch" ]; then
  printf '%s\n' "$branch"
  exit 0
fi

branch="$(git symbolic-ref --quiet --short "refs/remotes/$remote/HEAD" 2>/dev/null || true)"
[ -n "$branch" ] || {
  echo "error: cannot discover the default branch for $remote; pass it explicitly" >&2
  exit 3
}
printf '%s\n' "${branch#"$remote/"}"
