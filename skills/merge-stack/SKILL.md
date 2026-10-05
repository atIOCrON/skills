---
name: merge-stack
description: Merge approved stacks with ordinary merge commits by default; use an explicit squash override. Supports GitHub, GitLab, and Bitbucket release assembly.
disable-model-invocation: true
metadata:
  layer: runner
---


Read `references/operational-records.md` before creating or updating plan metadata,
builds, releases or deployments. Its schema-v2 JSON contract is authoritative
for operational records. Write and validate canonical JSON alongside each state
change; do not leave the browser report to reconstruct state from Markdown.
Use `scripts/validate_operational_records.py <record> --project-root <original-project>`
for each owned record before handoff. Whole-project audit findings are separate.
Keep historical extensions and existing authorization, verification and review
gates; they do not authorize schema aliases or inferred reporting values.
# Merge Stack

Default to `strategy: merge-commit`: preserve commits and create a merge commit
for each change. Squash only when the user explicitly selects
`strategy: squash`; never fall back to squash when merge commits are disabled.
Treat an explicit legacy `mode: squash` as that override.

For Bitbucket, or explicit `mode: release`, read
`references/release-assembly.md` instead of the standard workflow below.
It accepts mixed stacks, requires user merge authorization, and launches no
code review loops. The standard workflow supports GitHub and GitLab with
either strategy.

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
`build-branch-stack`, including moves and legacy migration. Read
`references/release-manifest.md` and validate the canonical manifest before
using it. Read `references/post-merge-cleanup.md`
only after every change merges.

## Inputs and Preflight

Accept branch names, change-request URLs, or provider IDs. Also accept provider,
remote, base, layout, strategy, cleanup, and journal overrides. Chained inputs
may be in any order. Independent base-targeted inputs require an explicit order.

For a stack built by `build-branch-stack`, load its manifest and map each source
branch to one feature before merging. Migrate encountered legacy plan folders
using the layout rules and refresh manifest paths. Require unmerged features
under `plans/slices/review/` or `plans/slices/in_release/`; verify the latter
against its recorded candidate membership. Allow confirmed final merges under
`plans/slices/merged/` or `plans/slices/fulfilled/` when resuming. Stop on a missing
or ambiguous mapping or a destination collision. For parented slices, require approved parent and child
metadata and an approved map; accept active parents in `backlog`, `to_do`,
`in_progress`, `review`, or `in_release`, and verified `merged` or `fulfilled` parents on resume.
Reject draft or superseded inputs. Reconcile affected parent progress before merging
using the complete approved maps, not just this release batch.
For each unmerged feature, confirm that its human or external acceptance checks
passed or an authorized decision explicitly accepted each limitation. Record
`none applicable` if there are no such checks. Pending acceptance blocks a new
merge and the move to `fulfilled/`; an already confirmed final merge belongs in
`merged/` while acceptance remains outstanding.

```bash
provider=<gitlab|github|auto>
strategy=${strategy:-merge-commit}
remote=${remote:-origin}
base="$(scripts/resolve_base_branch.sh "$remote" "${base:-}")"
scripts/provider.sh "$provider" "$remote" auth-check
git fetch --prune "$remote"
```

`auto` recognizes GitLab.com, GitHub.com, and Bitbucket Cloud. Bitbucket uses
release mode. Require an explicit provider for self-hosted or custom forges.
Stop if authentication, the selected strategy, or provider metadata is unavailable.

Use `chained` for functional chains or explicit linear placement proven by Git
ancestry/targets; use `base-targeted` for independent roots. Input order proves
no functional dependency; do not combine independent roots into a chain.
For active builds, obtain a handoff before source rewrites or shared-target
merges. Return repairs and landed/plan state to the coordinator, who owns shared
restacks, canonical moves, and manifest writes. Otherwise this workflow owns them.

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
SHA, mergeability, selected-strategy support, and landed SHA. Stop unless
approval covers the head, checks cover the head, the repository prevents stale approval, and
the final target is protected. Also require a concise revert plan for each
change. Stop unless the request is open, same-repository, and supports the
selected strategy.
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

1. Journal intent and fetch `$remote`. With merge commits, retain source heads;
   rebase only for a demonstrated conflict, changed ancestor, or repository
   policy requiring an updated source. A landed predecessor alone is not a
   reason to rebase.

   With an explicit squash override, rebase stale sources onto the current
   base. For a chained layout, remove the squashed prefix when rebasing later
   branches:

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
   If a rewrite changes behavior, effective output, or invalidates a review
   mapping, stop for a separately authorized build/review task. Carry a capped
   human disposition only through a proven unchanged-behavior mapping with
   unchanged finding risk. This skill launches no code review loops.
   Exact-head forge approval and checks still apply when repository policy
   requires them.

2. Wait for checks on the exact head:

   ```bash
   scripts/wait_for_change_checks.sh "$provider" "$remote" <id> <head-sha> "$strategy"
   ```

3. Validate the expected successor. Use its ID for a non-final chained item;
   otherwise use `null`:

   ```bash
   scripts/validate_successor_change.sh \
     "$provider" "$remote" <source-branch> <expected-id-or-null>
   ```

4. Refresh state and merge the exact approved and checked head using the
   selected strategy against the recorded target and base:

   For a mapped feature, require the acceptance evidence or authorized
   limitation decision to apply to this exact head. After a rebase, refresh
   that evidence or record why the prior result still applies. Stop if its
   applicability cannot be established.

   ```bash
     scripts/merge_stack_change.sh \
     "$provider" "$remote" <id> <head-sha> <target> <base-sha> \
     <successor-id-or-null> <journal> "$strategy"
   ```

   The script rechecks source and base SHAs, target, exact-head approval and
   checks, mergeability, selected strategy, and branch preservation immediately
   before merging. Journal intent first and the confirmed landed SHA afterward.

5. Confirm the landed commit using the same strategy:

   ```bash
   scripts/confirm_merge.sh \
     "$provider" "$remote" <id> <head-sha> "$base" <expected-base-sha> \
     <journal> "$strategy"
   ```

   Record `landed_sha` and `target_head_sha`. For merge commits, verify both
   pinned parents and the combined tree. For squash, verify the replacement
   tree; the original source head is not an ancestor of the squash commit.

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

After merge attempts and any applicable cleanup, reconcile each confirmed final
merge, including partial runs and resumes. Move slices from `review/` or
`in_release/` to
`plans/slices/merged/` while required acceptance remains outstanding, or directly
to `plans/slices/fulfilled/` when it passed or was explicitly accepted. Move
`merged/` slices to `fulfilled/` once acceptance is satisfied. Record final
destination, landed commit, merge evidence, and outstanding acceptance.
Keep unmerged features in `in_release/` while covered by a qualifying assembled
candidate; otherwise use `review/` under the shared membership rules. Refresh the manifest's plan and artefact
paths, including its own path if moved, and verify them. If a move or manifest
update fails, report the confirmed merges and remaining stage work; do not undo
a merge.
For an active coordinator, return confirmed merge/stage results instead of
performing shared moves or manifest writes. Preserve its worktrees/refs until
reconciliation; cleanup of its resources requires a handoff.

Set moved children's `Slice Status` to match their folder; preserve approval.
Reconcile parents under the shared complete-map and acceptance rules. Move
parents with their maps to `plans/specs/merged/<spec_slug>/` when every active
child is merged or fulfilled but required acceptance remains outstanding, or
to `plans/specs/fulfilled/<spec_slug>/` when all fulfillment gates pass.
Otherwise derive `in_release`, `review`, `in_progress`, `to_do`, or `backlog`. Preserve parent
approval, repair references, and verify paths.

Report child/parent transitions, reconciliation blockers, incomplete repairs,
and reasons parents remain open without undoing merges. Verify fulfilled
parents on resume; do not infer standalone legacy parents. Release assembly
retains its separate final-merge boundary.

## Invariants

- Preserve unrelated work; never stash, revert, or stage it during merging.
- Use explicit `--force-with-lease` SHAs, never plain `--force`.
- Require the selected strategy, approval, exact-head checks, and passing CI;
  unknown is not success.
- Require an unchanged target and base SHA until a direct merge completes.
- Journal every irreversible action before and after it; resume by reconciliation.
- On partial failure, stop and report the landed commits and safe reverse-order
  revert plan. Never auto-revert.
- Never delete a branch targeted by an open change request.
- Stop on conflicts, stale metadata, lost approval, failed checks, unsafe source
  deletion, merge failure, or a target branch that cannot fast-forward.

## Report

Return provider, remote, base, strategy, layout and dependency evidence, ordered
changes, targets, approval/check SHAs, rebases, landed SHAs, journal path, resulting base
SHA, feature stages, specification statuses, remote-deletion and local-cleanup
status, and unattempted branches.
