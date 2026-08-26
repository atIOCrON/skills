#!/usr/bin/env bash
# Rebase one stack branch onto the latest base target branch and force-push it
# with an explicit SHA lease. Prints old_remote_sha and rebased_head_sha on
# success. On rebase conflict, aborts the rebase, prints the conflicting
# files, and exits with the dedicated conflict exit code.
# Exit codes: 2 = usage, 3 = unresolvable ref, 4 = push rejected,
# 10 = rebase conflict (rebase aborted, worktree left clean).
set -euo pipefail

if [ "$#" -ne 2 ]; then
  echo "usage: rebase_stack_branch.sh <base-target-branch> <source-branch>" >&2
  exit 2
fi

target="$1"
branch="$2"

git fetch --prune origin

if ! git rev-parse --verify --quiet "origin/$target" >/dev/null; then
  echo "error: cannot resolve origin/$target" >&2
  exit 3
fi
if ! old_remote_sha="$(git rev-parse --verify --quiet "origin/$branch")"; then
  echo "error: cannot resolve origin/$branch" >&2
  exit 3
fi

git switch --detach "$old_remote_sha"

if ! git rebase "origin/$target"; then
  echo "error: rebase conflict rebasing $branch onto $target; conflicting files:" >&2
  git diff --name-only --diff-filter=U >&2
  git rebase --abort
  exit 10
fi

rebased_head_sha="$(git rev-parse HEAD)"

if ! git push \
  --force-with-lease="refs/heads/$branch:$old_remote_sha" \
  origin "HEAD:refs/heads/$branch"; then
  echo "error: force-with-lease push rejected for $branch (remote moved?)" >&2
  exit 4
fi

echo "old_remote_sha=$old_remote_sha"
echo "rebased_head_sha=$rebased_head_sha"
