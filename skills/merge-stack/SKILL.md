---
name: merge-stack
description: Safely squash-merge an approved dependency chain or ordered independent batch on GitLab or GitHub.
disable-model-invocation: true
metadata:
  layer: runner
---

# Merge Stack

Merge an already-reviewed linear dependency chain or ordered independent batch.
Discover the base from the remote unless the user supplies it. The remote
defaults to `origin`.

Requires `git`, `jq`, and the authenticated CLI for the selected provider:
`glab` for GitLab or `gh` for GitHub. Same-repository branches only; stop on
fork-based change requests.

## Resources

Read `references/stacked-change-requests.md` before classifying the layout.
Read `references/provider-contract.md` when adding or debugging a provider and
`references/run-journal.md` before mutation. Read
`references/orchestration-plans-layout.md` for a stack built by
`build-branch-stack`. Read `references/release-manifest.md` and validate the
canonical manifest before using it. Read `references/post-merge-cleanup.md`
only after every change merges.

## Inputs and Preflight

Accept branch names, change-request URLs, or provider IDs. Also accept provider,
remote, base, layout, cleanup, and journal overrides. Chained inputs may be in
any order. Independent base-targeted inputs require an explicit order.

For a stack built by `build-branch-stack`, load its manifest and map each source
branch to one feature before merging. Require unmerged features under
`plans/review/`; allow confirmed merged features already under `plans/done/`
when resuming. Stop on a missing or ambiguous mapping or a destination collision.
For each mapped feature, confirm that its human or external acceptance checks
passed or an authorized decision explicitly accepted each limitation. Record
`none applicable` if there are no such checks. Pending acceptance blocks the
merge and the move to `done/`.

```bash
provider=<gitlab|github|auto>
remote=${remote:-origin}
base="$(scripts/resolve_base_branch.sh "$remote" "${base:-}")"
scripts/provider.sh "$provider" "$remote" auth-check
git fetch --prune "$remote"
```

`auto` recognizes GitLab.com and GitHub.com. Require an explicit provider for
self-hosted or custom forges. Stop if authentication, squash merging, or
provider metadata is unavailable.

Use `chained` only when each later change requires its predecessor. Use
`base-targeted` for independent changes. Do not treat input order as dependency
evidence or combine independent roots into one chain.

Create the durable JSON Lines journal defined in `references/run-journal.md`
outside the repository. Before resuming an interrupted run, execute:

```bash
scripts/reconcile_run.sh "$provider" "$remote" <journal>
```

Record proven unjournaled completions before continuing. Stop on `blocker`.

Record the original worktree, branch, and status. Run merges from a clean
worktree. If the checkout is dirty, leave it untouched and create a temporary
worktree at `$remote/$base`. Stop if that fails.

## Resolve the Stack

For each input, run:

```bash
scripts/provider.sh "$provider" "$remote" get-change <input>
```

Record its ID, URL, branches, state, head and base SHAs, approval SHA, checks
SHA, mergeability, squash support, and landed SHA. Stop unless approval covers
the head, checks cover the head, the repository prevents stale approval, and
the final target is protected. Also require a concise revert plan for each
change. Stop unless the request is open, same-repository, and squash-capable.
Unknown fails closed.

Determine order from Git:

```bash
scripts/resolve_stack_order.sh "$remote" "$base" <chained|base-targeted> \
  <source-branch>...
```

For a chained layout, use the inferred order even when it differs from the
supplied order. Stop on ambiguous counts or broken ancestry. For independent
base-targeted changes, preserve the explicit order and verify that no source
branch contains another source branch. Classify one layout:

- base-targeted: every change targets `$base`;
- chained: the first targets `$base`, then each change targets the previous
  source branch.

Stop on mixed targets, hidden dependencies, or disagreement between targets and
Git ancestry. Process independent roots separately. Stop when one change needs
multiple unmerged parents; this runner cannot preserve a DAG join as a linear
stack.

This skill performs direct sequential merges, not merge-queue or merge-train
submission. Require a server policy that rejects stale-base results: GitHub
strict required status checks, or GitLab merged-result pipelines with successful
pipelines required. If the repository requires a queue or train, stop and use
that platform workflow. Never replace required remote CI with a local result.

## Merge Each Change

For each ordered branch:

1. Journal intent and fetch `$remote`. Rebase a stale first branch. Rebase each
   later independent branch onto the current base. For a chained layout, remove
   the integrated prefix while rebasing later branches:

   ```bash
   scripts/rebase_stack_branch.sh "$remote" "$base" <branch> <journal>
   scripts/rebase_stack_branch.sh "$remote" "$base" <branch> <journal> \
     <parent-old-remote-sha>
   ```

   Record both SHAs. The script aborts conflicts. After any rewrite, use
   `git range-diff` and verify the new head. An equal range diff retains prior
   reviews with effective-identity proof. The focused `reviewed_restack` paths
   in `build-branch-stack/references/code-review-loop.md` also apply with their
   required evidence and confirmations. Record old-to-new SHA mappings.
   Unmapped manual resolutions or inequalities, changed effective output, or
   behavior changes require a fresh Claude, Codex, and Cursor pass when below
   the cap. For a capped slice, carry its accepted human disposition through a
   proven unchanged-behavior mapping only while each accepted finding's risk
   remains unchanged. Otherwise return it to the build workflow for remediation
   or a new decision before merging. Keep automated review results truthful.
   Exact-head forge approval and checks still apply when repository policy
   requires them.

2. Wait for checks on the exact head:

   ```bash
   scripts/wait_for_change_checks.sh "$provider" "$remote" <id> <head-sha>
   ```

3. Validate the expected successor. Use its ID for a non-final chained item;
   otherwise use `null`:

   ```bash
   scripts/validate_successor_change.sh \
     "$provider" "$remote" <source-branch> <expected-id-or-null>
   ```

4. Refresh state and squash-merge the exact approved and checked head against
   the recorded target and base:

   For a mapped feature, require the acceptance evidence or authorized
   limitation decision to apply to this exact head. After a rebase, refresh
   that evidence or record why the prior result still applies. Stop if its
   applicability cannot be established.

   ```bash
     scripts/merge_stack_change.sh \
     "$provider" "$remote" <id> <head-sha> <target> <base-sha> \
     <successor-id-or-null> <journal>
   ```

   The script rechecks source and base SHAs, target, exact-head approval and
   checks, mergeability, squash, and branch preservation immediately before
   merging. Journal intent first and the confirmed landed SHA afterward.

5. Confirm the landed squash commit:

   ```bash
   scripts/confirm_squash_merge.sh \
     "$provider" "$remote" <id> <head-sha> "$base" <expected-base-sha> \
     <journal>
   ```

   Record `landed_sha` and `target_head_sha`. Do not test the pre-squash head for
   ancestry; squash creates a different commit.

6. For a chained stack, retarget the validated successor:

   ```bash
   scripts/retarget_change.sh "$provider" "$remote" <successor-id> "$base" \
     <journal>
   ```

   Preserve the merged source branch by default. If the user opted into remote
   deletion, delete it only through:

   ```bash
   scripts/delete_branch_if_unreferenced.sh \
     "$provider" "$remote" <merged-source-branch> <expected-source-sha> \
     <journal>
   ```

   Use the same opt-in guarded deletion for final and base-targeted items. A
   retarget or force-push invalidates earlier checks and may reset approvals;
   recheck both during the successor's iteration.

## Cleanup

The merge succeeds independently of cleanup. The default is `local-if-clean`:
after all changes have merged, clean up local branches and update the original
checkout if it is clean at cleanup time. If it is dirty, skip local cleanup and
leave it untouched. Preserve remote branches and stashes; remote
deletion is a separate opt-in action described above. Allow an explicit `none`
override. For local cleanup, keep the journal updated and write one record per
branch:

```text
branch old_remote_sha rebased_head_sha landed_sha
```

Remove only a clean temporary worktree created by this workflow. Run local
cleanup by default when the original checkout is clean, unless the user selects
`none`. This skill never creates or applies stashes.

Read `references/post-merge-cleanup.md` before either local mode. Run only from
the clean original checkout:

```bash
scripts/cleanup_merged_branches.sh "$remote" "$base" <record-file>
```

After merge attempts and any applicable cleanup, move each confirmed merged
feature with completed or explicitly accepted acceptance checks from
`plans/review/` to `plans/done/`, including after a partial run.
Leave unmerged features in `review/`. Refresh the manifest's plan and artefact
paths, including its own path if moved, and verify them. If a move or manifest
update fails, report the confirmed merges and remaining stage work; do not undo
a merge.

After those moves, reconcile each affected parent specification. Require an
`approved` specification and `approved` slice map, then locate every mapped
slice slug exactly once across the stage directories. Change the specification
status to `fulfilled` only when every mapped slice is in `done/`; that stage
already proves merge and completed or explicitly accepted acceptance. Leave it
`approved` when any slice remains elsewhere. Stop the status update on a stale
map, missing or duplicate slug, or inconsistent acceptance ownership, but do
not undo confirmed merges. Do not infer a parent specification for legacy
plans. Report every specification status change or reason it remained open.

## Invariants

- Preserve unrelated work; never stash, revert, or stage it during merging.
- Use explicit `--force-with-lease` SHAs, never plain `--force`.
- Require squash, approval, exact-head checks, and passing CI; unknown is not
  success.
- Require an unchanged target and base SHA until a direct merge completes.
- Journal every irreversible action before and after it; resume by reconciliation.
- On partial failure, stop and report the landed commits and safe reverse-order
  revert plan. Never auto-revert.
- Never delete a branch targeted by an open change request.
- Stop on conflicts, stale metadata, lost approval, failed checks, unsafe source
  deletion, merge failure, or a target branch that cannot fast-forward.

## Report

Return provider, remote, base, layout and dependency evidence, ordered changes,
targets, approval/check SHAs, rebases, landed SHAs, journal path, resulting base
SHA, feature stages, specification statuses, remote-deletion and local-cleanup
status, and unattempted branches.
