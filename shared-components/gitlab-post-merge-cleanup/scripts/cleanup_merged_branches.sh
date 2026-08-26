#!/usr/bin/env bash
# Restore the local checkout after merges land: switch to the target branch,
# fast-forward it, prune remote-tracking refs, then safely advance and
# safe-delete merged local branches with per-branch outcome reporting.
# Never force-deletes, stashes, or reverts.
# Exit codes: 2 = usage or supplied record file not found, 3 = cannot switch
# to or fast-forward the target branch.
set -euo pipefail

if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
  echo "usage: cleanup_merged_branches.sh <target-branch> [record-file]" >&2
  exit 2
fi

target="$1"
record_file="${2:-}"

if [ -n "$record_file" ] && [ ! -f "$record_file" ]; then
  echo "error: record file not found: $record_file" >&2
  exit 2
fi

if ! git switch "$target"; then
  echo "error: cannot switch to $target; local modifications may be in the way." >&2
  echo "current branch: $(git branch --show-current)" >&2
  git status --short >&2
  exit 3
fi

if ! git pull --ff-only origin "$target"; then
  echo "error: cannot fast-forward $target from origin" >&2
  exit 3
fi

git fetch --prune origin

delete_branch() {
  if git branch -d "$1"; then
    echo "deleted: $1"
  else
    echo "skipped: $1 (safe delete refused: not fully merged, checked out in another worktree, or local-only commits)"
  fi
}

if [ -n "$record_file" ]; then
  while read -r branch old_remote_sha rebased_head_sha || [ -n "$branch" ]; do
    [ -n "$branch" ] || continue
    if ! git show-ref --verify --quiet "refs/heads/$branch"; then
      echo "skipped: $branch (no local branch)"
      continue
    fi
    local_sha="$(git rev-parse "refs/heads/$branch")"
    if [ "$local_sha" != "$old_remote_sha" ]; then
      echo "skipped: $branch (local SHA $local_sha differs from recorded old_remote_sha $old_remote_sha)"
      continue
    fi
    if ! git merge-base --is-ancestor "$rebased_head_sha" "refs/heads/$target"; then
      echo "skipped: $branch (rebased head $rebased_head_sha not merged into $target)"
      continue
    fi
    if ! git branch -f "$branch" "$rebased_head_sha"; then
      echo "skipped: $branch (could not advance stale local branch ref)"
      continue
    fi
    echo "advanced: $branch -> $rebased_head_sha"
    delete_branch "$branch"
  done < "$record_file"
else
  for branch in $(git for-each-ref --format='%(refname:short)' refs/heads/); do
    [ "$branch" = "$target" ] && continue
    branch_sha="$(git rev-parse "refs/heads/$branch")"
    if git merge-base --is-ancestor "$branch_sha" "refs/heads/$target"; then
      delete_branch "$branch"
    fi
  done
fi
