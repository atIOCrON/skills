---
name: gitlab-merge-stack
description: Sequentially merge a stack of already-reviewed GitLab merge requests into the base target branch (default develop), inferring stack order from branch ancestry and commit counts, then rebasing and force-pushing each next branch onto the freshly updated base target branch before merging it. Handles both base-targeted stacks and true stacked MR chains, retargeting successor MRs as the stack merges.
compatibility: Requires git, glab, and jq with GitLab authentication
metadata:
  layer: runner
---

# GitLab Merge Stack

Use when the user provides already-reviewed stacked GitLab branches or merge
requests to merge into the base target branch one at a time. The base target
branch defaults to `develop` unless the user names another.

Stacked-MR terms (base target branch, stack parent branch, MR target branch,
layouts) are defined in
`.agents/skills/orchestration-conventions/references/stacked_mrs.md`.

## Inputs

- Branch names, MR URLs, or MR IIDs for the reviewed stack. The user does not
  need to provide them in merge order.
- Base target branch if not `develop`.
- Optional non-default merge mode; otherwise use the MR or project default and do not force squash/rebase settings.

## Preflight

A child process cannot change this shell's PATH, so begin every shell invocation
that runs `glab` with `eval "$(.agents/skills/gitlab-merge-stack/scripts/ensure_glab.sh)"`;
the script resolves `glab` and `jq` for non-interactive shells. Then run:

```bash
eval "$(.agents/skills/gitlab-merge-stack/scripts/ensure_glab.sh)"
original_worktree="$PWD"
original_branch="$(git branch --show-current)"
git status --short
printf 'Original branch: %s\n' "$original_branch"
git fetch --prune origin
glab auth status
```

Stop if `ensure_glab.sh` reports an error or GitLab auth is unavailable.

Unrelated local modifications are allowed. If the worktree is dirty, use a
temporary clean worktree instead of stashing, reverting, or asking for cleanup:

```bash
tmp_worktree="../$(basename "$PWD")-merge-stack-$(date +%Y%m%d%H%M%S)"
git worktree add "$tmp_worktree" origin/<base-target-branch>
cd "$tmp_worktree"
git fetch --prune origin
```

If the current worktree is clean, use it directly. Run the merge workflow only
from a clean worktree, leave unrelated dirty work untouched in the original
checkout, and stop if creating the temporary worktree fails.

## Resolve Stack

For every input, resolve and record: source branch, MR IID and URL, MR target
branch, MR state, latest pipeline/check status, head SHA, and whether GitLab
shows approvals/review requirements are satisfied. Use `glab mr view` and
`glab api` as needed. Stop if any item is missing an open MR, appears
unreviewed/unapproved, has a failed pipeline, or is already merged out of
order.

Detect the MR target layout from the recorded MR metadata:

- base-targeted stack: every MR targets the base target branch;
- true stacked MR chain: the first MR targets the base target branch and each
  later MR targets the previous source branch, in verified ancestry order.

Report the detected layout before merging. Stop if the MRs mix layouts, or if
the MR targets describe a dependency chain that disagrees with the verified
branch ancestry.

Determine the merge order from Git, not from the user-supplied order:

```bash
.agents/skills/gitlab-merge-stack/scripts/resolve_stack_order.sh <base-target-branch> <source-branch>...
```

The script fetches, counts commits per branch relative to the base target
branch, verifies strictly increasing counts and the ancestry chain, and prints
the ordered branch list with counts. It exits non-zero with a diagnostic when
the order is ambiguous (duplicated counts, broken ancestry); stop on that
failure.
If the inferred order differs from the user's list, use the inferred order and
report that correction before proceeding.

Treat successful pipeline/check status as required by default for this repo.
Confirm the project setting when possible (`glab api` field
`only_allow_merge_if_pipeline_succeeds`), but never treat a missing/false
setting as permission to merge red or pending checks; skip green-check
enforcement only when the user explicitly asks and acknowledges the risk.

## Workflow

For each source branch in order:

1. Refresh remote state with `git fetch --prune origin`. Stop if
   `origin/<base-target-branch>` cannot be fetched or resolved.

2. Prepare the current branch against the latest base target branch. For the
   first branch, merge directly if GitLab reports it mergeable against the
   current base target branch and its checks are green; if it is stale or not
   mergeable, rebase it the same way as every later branch:

   ```bash
   .agents/skills/gitlab-merge-stack/scripts/rebase_stack_branch.sh <base-target-branch> <source-branch>
   ```

   The script detaches at the remote SHA, rebases onto the base target branch,
   pushes with an explicit `--force-with-lease=refs/heads/<branch>:<old-sha>`
   lease, and prints `old_remote_sha` and `rebased_head_sha`; record both for
   local cleanup (for branches merged without rebasing, record the same value
   as both).

   Conflict policy: on a rebase conflict the script runs `git rebase --abort`,
   prints the conflicting files, and exits with its dedicated conflict exit
   code. Stop and report the conflicting files; conflicts are resolved only
   when the user explicitly asks in that run.

3. Wait for the MR pipeline on the new head SHA:

   ```bash
   .agents/skills/gitlab-merge-stack/scripts/wait_for_mr_pipeline.sh <iid-or-url> <rebased-head-sha>
   ```

   Wait policy: poll every 30 seconds, stop after 20 minutes. Stop if the
   script reports failure, cancellation, an unexpected skip, or a timeout, or
   if the MR is not mergeable.

4. Merge the MR. First identify the expected successor from the detected layout
   and ordered stack metadata. For a true stacked MR chain, use the next stack
   MR's IID when the current branch is not the final item; otherwise use the
   literal `null`. For a base-targeted stack, always use `null` because no stack
   MR should target the current source branch.

   ```bash
   .agents/skills/gitlab-merge-stack/scripts/validate_successor_mr.sh <source-branch> <expected-successor-iid-or-null>
   ```

   The script exits non-zero if the refresh returns multiple open MRs, an
   unexpected MR, any MR other than the expected successor for the current
   source branch, or no MR when the current branch is a non-final item in a true
   stacked chain. Record the printed `successor_iid` value, then merge:

   ```bash
   .agents/skills/gitlab-merge-stack/scripts/merge_stack_mr.sh <iid> <current-head-sha> <successor-iid-or-null>
   ```

   The merge script uses `--remove-source-branch` only when `successor_iid` is
   `null`. If an expected successor still targets this source branch, it clears
   and verifies GitLab's source-branch-removal setting before merging without
   `--remove-source-branch`. If the script reports that GitLab may still remove
   the source branch, stop; that blocks safe true-stacked merging while a
   successor targets it. Because this repo requires green checks, merge only
   after the MR head pipeline is successful.

5. Confirm the merge landed:

   ```bash
   git fetch --prune origin
   git merge-base --is-ancestor <merged-head-sha> origin/<base-target-branch>
   ```

   Stop if `origin/<base-target-branch>` does not contain the merged head SHA,
   if the MR did not close/merge, or if the source branch removal behaves
   unexpectedly.

6. True stacked MR chain only — if the expected successor MR still targets the
   just-merged source branch, retarget that successor MR to the base target
   branch before attempting to merge it. Skip this step when any of the
   following holds: the stack is base-targeted; the validated successor check
   returned `successor_iid=null`; or the final branch has merged. Use the IID
   from the validated step-4 refresh as `<successor-iid>`:

   ```bash
   eval "$(.agents/skills/gitlab-merge-stack/scripts/ensure_glab.sh)"
   glab mr update <successor-iid> --target-branch <base-target-branch>
   ```

   Then delete the just-merged source branch only through the guarded deletion
   script:

   ```bash
   .agents/skills/gitlab-merge-stack/scripts/delete_branch_if_unreferenced.sh <merged-source-branch>
   ```

   The script rechecks GitLab before deleting and exits non-zero if any open MR
   still targets the branch or if GitLab blocks the deletion. Report that branch
   for manual cleanup instead of forcing it. A retarget or force-push restarts
   checks: rerun steps 2-3 for the successor and wait for fresh results on its
   new head SHA; never rely on green checks produced against the previous target
   branch.

Repeat the refresh, rebase, wait, merge, confirm, and retarget cycle for the
next branch.

## Local Cleanup

After the stack finishes successfully:

1. Write the recorded per-branch SHA triples to a record file in the
   artefact/working directory, one whitespace-separated
   `branch old_remote_sha rebased_head_sha` triple per line.
2. Return to the original worktree (`cd "$original_worktree"`). If a temporary
   worktree was used and is clean, remove it (`git worktree remove
   "$tmp_worktree"`, then `git worktree prune`) — this stays here because this
   skill created it. Keep any worktree holding conflict state to inspect.
3. Invoke `.agents/skills/gitlab-post-merge-cleanup/SKILL.md` with the base
   target branch and the record file.

## Rules

- Preserve unrelated dirty work by using a clean temporary worktree when needed;
  never stash, revert, or stage unrelated user changes.
- Infer and verify stack order from remote branch ancestry and commit counts;
  never merge branches out of the verified stack order.
- Use `--force-with-lease` with explicit remote SHA leases, never plain
  `--force`; keep temporary worktrees local-only and never push remote
  temporary branches.
- Record original and rebased head SHAs for each branch so post-merge cleanup
  can safely handle stale local branch refs left behind by detached-worktree
  rebases.
- Require successful GitLab checks by default; do not skip them unless the user
  explicitly asks and acknowledges the risk.
- Never delete a remote source branch that is still the target of an open MR;
  retarget the successor first and defer deletion until GitLab confirms no
  open MR targets the branch.
- Stop and report blockers for conflicts, failed checks, missing approvals,
  stale MR metadata that does not refresh, merge failures, or base target branch
  updates that cannot fast-forward.

## Final Response

Return the detected MR target layout and the ordered stack with branch name,
MR URL/IID, MR target branch, retarget status, rebase status, pushed head
SHA, pipeline/check result, merge result, resulting
`origin/<base-target-branch>` SHA, local cleanup status, temporary worktree
cleanup status, and any branches that were not attempted because of a blocker.
