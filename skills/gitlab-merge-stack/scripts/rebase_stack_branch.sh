#!/usr/bin/env bash
# Rebase one stack branch onto the latest base target branch and force-push it
# with an explicit SHA lease. Prints old_remote_sha and rebased_head_sha on
# success. On rebase conflict, aborts the rebase, prints the conflicting
# files, and exits with the dedicated conflict exit code.
# When an integrated stack-parent SHA is supplied, omit that already-squashed
# prefix explicitly instead of relying on patch-equivalence detection.
# Exit codes: 2 = usage, 3 = unresolvable ref, 4 = push rejected,
# 5 = stack parent is not in the source history,
# 10 = rebase conflict (rebase aborted, worktree left clean).
set -euo pipefail

if [ "$#" -lt 2 ] || [ "$#" -gt 3 ]; then
  echo "usage: rebase_stack_branch.sh <base-target-branch> <source-branch> [integrated-stack-parent-sha]" >&2
  exit 2
fi

target="$1"
branch="$2"
integrated_parent_sha="${3:-}"

git fetch --prune origin

if ! git rev-parse --verify --quiet "origin/$target" >/dev/null; then
  echo "error: cannot resolve origin/$target" >&2
  exit 3
fi
if ! old_remote_sha="$(git rev-parse --verify --quiet "origin/$branch")"; then
  echo "error: cannot resolve origin/$branch" >&2
  exit 3
fi
if [ -n "$integrated_parent_sha" ]; then
  if ! integrated_parent_sha="$(git rev-parse --verify --quiet "${integrated_parent_sha}^{commit}")"; then
    echo "error: cannot resolve integrated stack-parent SHA: $3" >&2
    exit 3
  fi
  if ! git merge-base --is-ancestor "$integrated_parent_sha" "$old_remote_sha"; then
    echo "error: integrated stack-parent $integrated_parent_sha is not an ancestor of origin/$branch ($old_remote_sha)" >&2
    exit 5
  fi
fi

git switch --detach "$old_remote_sha"

if [ -n "$integrated_parent_sha" ]; then
  rebase_command=(git rebase --onto "origin/$target" "$integrated_parent_sha")
else
  rebase_command=(git rebase "origin/$target")
fi

if ! "${rebase_command[@]}"; then
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
if [ -n "$integrated_parent_sha" ]; then
  echo "integrated_stack_parent_sha=$integrated_parent_sha"
fi
