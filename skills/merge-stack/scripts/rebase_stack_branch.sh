#!/usr/bin/env bash
# Rebase one stack branch onto the latest base target branch and force-push it
# with an explicit SHA lease. Prints old_remote_sha and rebased_head_sha on
# success. On rebase conflict, aborts the rebase, prints the conflicting
# files, and exits with the dedicated conflict exit code.
# When an integrated dependency-parent SHA is supplied, omit that squashed
# prefix explicitly instead of relying on patch-equivalence detection.
# Exit codes: 2 = usage, 3 = unresolvable ref, 4 = push rejected,
# 5 = dependency parent is not in the source history, 6 = patch set changed,
# 10 = rebase conflict (rebase aborted, worktree left clean).
set -euo pipefail

if [ "$#" -lt 4 ] || [ "$#" -gt 5 ]; then
  echo "usage: rebase_stack_branch.sh <remote> <base-branch> <source-branch> <journal> [integrated-parent-sha]" >&2
  exit 2
fi

remote="$1"
target="$2"
branch="$3"
journal="$4"
integrated_parent_sha="${5:-}"
script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"

git fetch --prune "$remote"

if ! git rev-parse --verify --quiet "$remote/$target" >/dev/null; then
  echo "error: cannot resolve $remote/$target" >&2
  exit 3
fi
if ! old_remote_sha="$(git rev-parse --verify --quiet "$remote/$branch")"; then
  echo "error: cannot resolve $remote/$branch" >&2
  exit 3
fi
if [ -n "$integrated_parent_sha" ]; then
  if ! integrated_parent_sha="$(git rev-parse --verify --quiet "${integrated_parent_sha}^{commit}")"; then
    echo "error: cannot resolve integrated dependency-parent SHA: $5" >&2
    exit 3
  fi
  if ! git merge-base --is-ancestor "$integrated_parent_sha" "$old_remote_sha"; then
    echo "error: integrated dependency parent $integrated_parent_sha is not an ancestor of $remote/$branch ($old_remote_sha)" >&2
    exit 5
  fi
fi

if [ -n "$integrated_parent_sha" ]; then
  old_base_sha="$integrated_parent_sha"
else
  old_base_sha="$(git merge-base "$old_remote_sha" "$remote/$target")"
fi
backup_ref="refs/merge-stack-backups/$old_remote_sha"
"$script_dir/journal_event.sh" "$journal" rebase-planned \
  "$(jq -nc --arg branch "$branch" --arg old "$old_remote_sha" --arg base "$(git rev-parse "$remote/$target")" \
    '{branch:$branch,old_remote_sha:$old,expected_base_sha:$base}')"
git update-ref "$backup_ref" "$old_remote_sha"
git switch --detach "$old_remote_sha"

if [ -n "$integrated_parent_sha" ]; then
  rebase_command=(git rebase --onto "$remote/$target" "$integrated_parent_sha")
else
  rebase_command=(git rebase "$remote/$target")
fi

if ! "${rebase_command[@]}"; then
  echo "error: rebase conflict rebasing $branch onto $target; conflicting files:" >&2
  git diff --name-only --diff-filter=U >&2
  git rebase --abort
  exit 10
fi

rebased_head_sha="$(git rev-parse HEAD)"

old_patch_ids="$(mktemp)"
new_patch_ids="$(mktemp)"
trap 'rm -f "$old_patch_ids" "$new_patch_ids"' EXIT
patch_ids() {
  local range="$1" output="$2" commit
  : > "$output"
  while read -r commit; do
    [ -n "$commit" ] || continue
    git show --pretty=email --no-ext-diff --binary "$commit" |
      git patch-id --stable | awk '{print $1}' >> "$output"
  done < <(git rev-list --reverse "$range")
}
patch_ids "$old_base_sha..$old_remote_sha" "$old_patch_ids"
patch_ids "$remote/$target..$rebased_head_sha" "$new_patch_ids"
if ! cmp -s "$old_patch_ids" "$new_patch_ids"; then
  echo "error: rebase changed the patch set for $branch" >&2
  git range-diff "$old_base_sha..$old_remote_sha" "$remote/$target..$rebased_head_sha" >&2 || true
  exit 6
fi

"$script_dir/journal_event.sh" "$journal" rebase-verified \
  "$(jq -nc --arg branch "$branch" --arg old "$old_remote_sha" --arg head "$rebased_head_sha" \
    '{branch:$branch,old_remote_sha:$old,rebased_head_sha:$head,patch_set:"equivalent"}')"
"$script_dir/journal_event.sh" "$journal" force-push-planned \
  "$(jq -nc --arg branch "$branch" --arg old "$old_remote_sha" --arg head "$rebased_head_sha" \
    '{branch:$branch,lease_sha:$old,rebased_head_sha:$head}')"

if ! git push \
  --force-with-lease="refs/heads/$branch:$old_remote_sha" \
  "$remote" "HEAD:refs/heads/$branch"; then
  echo "error: force-with-lease push rejected for $branch (remote moved?)" >&2
  exit 4
fi

"$script_dir/journal_event.sh" "$journal" force-pushed \
  "$(jq -nc --arg branch "$branch" --arg old "$old_remote_sha" --arg head "$rebased_head_sha" \
    '{branch:$branch,old_remote_sha:$old,rebased_head_sha:$head}')"

echo "old_remote_sha=$old_remote_sha"
echo "rebased_head_sha=$rebased_head_sha"
echo "backup_ref=$backup_ref"
if [ -n "$integrated_parent_sha" ]; then
  echo "integrated_stack_parent_sha=$integrated_parent_sha"
fi
