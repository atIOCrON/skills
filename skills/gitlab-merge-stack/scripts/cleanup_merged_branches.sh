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
  while read -r branch old_remote_sha rebased_head_sha landed_sha extra || [ -n "${branch:-}" ]; do
    [ -n "$branch" ] || continue
    if [ -n "${extra:-}" ] || [ -z "${old_remote_sha:-}" ] || [ -z "${rebased_head_sha:-}" ]; then
      echo "skipped: $branch (malformed cleanup record)"
      continue
    fi
    # Legacy triple records represent non-squash merges, where the rebased
    # branch head itself was the landed commit.
    landed_sha="${landed_sha:-$rebased_head_sha}"
    if ! git show-ref --verify --quiet "refs/heads/$branch"; then
      echo "skipped: $branch (no local branch)"
      continue
    fi
    local_sha="$(git rev-parse "refs/heads/$branch")"
    if [ "$local_sha" != "$old_remote_sha" ]; then
      echo "skipped: $branch (local SHA $local_sha differs from recorded old_remote_sha $old_remote_sha)"
      continue
    fi
    if ! git cat-file -e "${rebased_head_sha}^{commit}" 2>/dev/null ||
      ! git cat-file -e "${landed_sha}^{commit}" 2>/dev/null; then
      echo "skipped: $branch (recorded rebased or landed commit is unavailable)"
      continue
    fi
    if [ "$rebased_head_sha" != "$landed_sha" ] &&
      ! git diff --quiet "${rebased_head_sha}^{tree}" "${landed_sha}^{tree}"; then
      echo "skipped: $branch (rebased head and landed squash commit have different trees)"
      continue
    fi
    if ! git merge-base --is-ancestor "$landed_sha" "refs/heads/$target"; then
      echo "skipped: $branch (landed commit $landed_sha not merged into $target)"
      continue
    fi
    if ! git branch -f "$branch" "$landed_sha"; then
      echo "skipped: $branch (could not advance stale local branch ref)"
      continue
    fi
    echo "advanced: $branch -> $landed_sha"
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
