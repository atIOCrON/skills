---
name: gitlab-merge-stack
description: Sequentially merge a stack of already-reviewed GitLab merge requests into the base target branch, rebasing and retargeting successors as needed. Bundles its terminology, cleanup instructions, and executable helpers.
metadata:
  layer: runner
---

# GitLab Merge Stack

Use when the user provides already-reviewed stacked GitLab branches or merge
requests to merge into the base target branch one at a time. The base target
branch defaults to `develop` unless the user names another.

Requires `git`, `glab`, and `jq`, with GitLab authentication configured.

## Bundled Resources

Supporting terminology and cleanup instructions are under `references/`, and
executable helpers are under `scripts/`. They are bundled resources, not
separately installed skills.

Read `references/orchestration-stacked-mrs.md` before classifying the stack
layout. Read `references/gitlab-post-merge-cleanup.md` only after the complete
stack merges successfully and local cleanup begins. Use the helper scripts at
the workflow steps that name them; do not load every resource at activation.

Stacked-MR terms (base target branch, stack parent branch, MR target branch,
layouts) are defined in
`references/orchestration-stacked-mrs.md`.

## Inputs

- Branch names, MR URLs, or MR IIDs for the reviewed stack. The user does not
  need to provide them in merge order.
- Base target branch if not `develop`.

This workflow requires effective squash-on-merge for every MR. The project
setting should require squash, and each MR must report `squash_on_merge=true`.

## Preflight

A child process cannot change this shell's PATH, so begin every shell invocation
that runs `glab` with `eval "$(scripts/ensure_glab.sh)"`;
the script resolves `glab` and `jq` for non-interactive shells. Then run:

```bash
eval "$(scripts/ensure_glab.sh)"
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
branch, MR state, latest pipeline/check status, initial head SHA, effective
`squash_on_merge` value, and whether GitLab shows approvals/review requirements
are satisfied. Use `glab mr view` and `glab api` as needed. Stop if any item is
missing an open MR, has effective squash-on-merge disabled, appears
unreviewed/unapproved, has a failed pipeline, or is already merged out of
order, except for a pipeline failure caused only by exhausted CI minutes or
quota; handle that case as described below.

Detect the MR target layout from the recorded MR metadata:

- base-targeted stack: every MR targets the base target branch;
- true stacked MR chain: the first MR targets the base target branch and each
  later MR targets the previous source branch, in verified ancestry order.

Report the detected layout before merging. Stop if the MRs mix layouts, or if
the MR targets describe a dependency chain that disagrees with the verified
branch ancestry.

Determine the merge order from Git, not from the user-supplied order:

```bash
scripts/resolve_stack_order.sh <base-target-branch> <source-branch>...
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

If a pipeline fails only because CI minutes or quota are exhausted (for
example, `ci_quota_exceeded`), run every affected required job locally on the
exact MR head SHA. Proceed only if all pass; record the commands and results.

## Workflow

For each source branch in order:

1. Refresh remote state with `git fetch --prune origin`. Stop if
   `origin/<base-target-branch>` cannot be fetched or resolved.

2. Prepare the current branch against the latest base target branch. For the
   first branch, merge directly if GitLab reports it mergeable against the
   current base target branch and its checks are green; if it is stale or not
   mergeable, rebase it without a stack-parent argument:

   ```bash
   scripts/rebase_stack_branch.sh <base-target-branch> <source-branch>
   ```

   Rebase every later branch while explicitly removing the already-integrated
   stack prefix. Pass the preceding branch's recorded `old_remote_sha`, which
   must be an ancestor of the current branch:

   ```bash
   scripts/rebase_stack_branch.sh \
     <base-target-branch> \
     <source-branch> \
     <preceding-branch-old-remote-sha>
   ```

   The script detaches at the remote SHA and rebases onto the base target
   branch. With the stack-parent argument it uses `rebase --onto` so commits
   already represented by an earlier squash commit are not replayed. It pushes
   with an explicit `--force-with-lease=refs/heads/<branch>:<old-sha>` lease and
   prints `old_remote_sha` and `rebased_head_sha`; record both for local cleanup
   (for branches merged without rebasing, record the same value as both).

   Conflict policy: on a rebase conflict the script runs `git rebase --abort`,
   prints the conflicting files, and exits with its dedicated conflict exit
   code. Stop and report the conflicting files; conflicts are resolved only
   when the user explicitly asks in that run.

3. Wait for the MR pipeline on the new head SHA:

   ```bash
   scripts/wait_for_mr_pipeline.sh <iid-or-url> <rebased-head-sha>
   ```

   Wait policy: poll every 30 seconds, stop after 20 minutes. Stop if the
   script reports failure, cancellation, an unexpected skip, or a timeout, or
   if the MR is not mergeable. For a quota-only failure, run local CI as
   specified above instead of stopping.

4. Merge the MR. First identify the expected successor from the detected layout
   and ordered stack metadata. For a true stacked MR chain, use the next stack
   MR's IID when the current branch is not the final item; otherwise use the
   literal `null`. For a base-targeted stack, always use `null` because no stack
   MR should target the current source branch.

   ```bash
   scripts/validate_successor_mr.sh <source-branch> <expected-successor-iid-or-null>
   ```

   The script exits non-zero if the refresh returns multiple open MRs, an
   unexpected MR, any MR other than the expected successor for the current
   source branch, or no MR when the current branch is a non-final item in a true
   stacked chain. Record the printed `successor_iid` value, then merge:

   ```bash
   scripts/merge_stack_mr.sh <iid> <current-head-sha> <successor-iid-or-null>
   ```

   The merge script refreshes the MR and rejects a stale head or effective
   `squash_on_merge` value other than `true`, then merges with `--squash`. It
   uses `--remove-source-branch` only when `successor_iid` is `null`. If an
   expected successor still targets this source branch, it clears and verifies
   GitLab's source-branch-removal setting before merging without
   `--remove-source-branch`. If the script reports that GitLab may still remove
   the source branch, stop; that blocks safe true-stacked merging while a
   successor targets it. Merge only after the MR head pipeline succeeds or
   quota-exhaustion local CI passes.

5. Confirm the merge landed:

   ```bash
   scripts/confirm_squash_merge.sh \
     <iid> \
     <merged-head-sha> \
     <base-target-branch>
   ```

   Record the printed `squash_commit_sha` as `landed_sha` and the printed
   `target_head_sha` as the resulting base target SHA. Stop if the MR did not
   merge from the reviewed head with effective squash enabled, if GitLab did
   not report a squash commit, if that commit is absent from
   `origin/<base-target-branch>`, or if source branch removal behaves
   unexpectedly. Do not test the pre-squash MR head for ancestry: a squash
   merge intentionally creates a different commit SHA.

6. True stacked MR chain only — if the expected successor MR still targets the
   just-merged source branch, retarget that successor MR to the base target
   branch before attempting to merge it. Skip this step when any of the
   following holds: the stack is base-targeted; the validated successor check
   returned `successor_iid=null`; or the final branch has merged. Use the IID
   from the validated step-4 refresh as `<successor-iid>`:

   ```bash
   eval "$(scripts/ensure_glab.sh)"
   glab mr update <successor-iid> --target-branch <base-target-branch>
   ```

   Then delete the just-merged source branch only through the guarded deletion
   script:

   ```bash
   scripts/delete_branch_if_unreferenced.sh <merged-source-branch>
   ```

   The script rechecks GitLab before deleting and exits non-zero if any open MR
   still targets the branch or if GitLab blocks the deletion. Report that branch
   for manual cleanup instead of forcing it. A retarget or force-push restarts
   checks: in the successor's iteration, rebase it with the just-merged branch's
   recorded `old_remote_sha`, then wait for fresh results on its new head SHA;
   never rely on green checks produced against the previous target branch.

Repeat the refresh, rebase, wait, merge, confirm, and retarget cycle for the
next branch.

## Local Cleanup

After the stack finishes successfully:

1. Write the recorded per-branch SHA values to a record file in the
   artefact/working directory, one whitespace-separated
   `branch old_remote_sha rebased_head_sha landed_sha` record per line.
2. Return to the original worktree (`cd "$original_worktree"`). If a temporary
   worktree was used and is clean, remove it (`git worktree remove
   "$tmp_worktree"`, then `git worktree prune`) — this stays here because this
   workflow created it. Keep any worktree holding conflict state to inspect.
3. Read and follow `references/gitlab-post-merge-cleanup.md`, passing the base
   target branch and the record file to `scripts/cleanup_merged_branches.sh`.

## Rules

- Preserve unrelated dirty work by using a clean temporary worktree for merge
  operations. Do not stash, revert, or stage it except for the temporary stash
  explicitly allowed by the final-cleanup procedure.
- Infer and verify stack order from remote branch ancestry and commit counts;
  never merge branches out of the verified stack order.
- Use `--force-with-lease` with explicit remote SHA leases, never plain
  `--force`; keep temporary worktrees local-only and never push remote
  temporary branches.
- Record original, rebased, and landed squash SHAs for each branch so
  post-merge cleanup can safely handle stale local branch refs left behind by
  detached-worktree rebases and squash merges.
- Require effective squash-on-merge for every MR; do not merge when
  `squash_on_merge` is false or when GitLab does not return a landed squash
  commit.
- Require successful GitLab checks, or equivalent local checks when CI quota is
  exhausted; otherwise require explicit user acknowledgement to bypass them.
- Never delete a remote source branch that is still the target of an open MR;
  retarget the successor first and defer deletion until GitLab confirms no
  open MR targets the branch.
- Stop and report blockers for conflicts, failed checks, missing approvals,
  stale MR metadata that does not refresh, merge failures, or base target branch
  updates that cannot fast-forward.

## Final Response

Return the detected MR target layout and the ordered stack with branch name,
MR URL/IID, MR target branch, retarget status, rebase status, pushed head
SHA, effective squash setting, pipeline/check result, squash commit SHA, merge
result, resulting
`origin/<base-target-branch>` SHA, local cleanup status, temporary worktree
cleanup status, and any branches that were not attempted because of a blocker.
