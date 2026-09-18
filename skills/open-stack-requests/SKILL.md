---
name: open-stack-requests
description: Create or refresh draft change requests as verified branches stabilize, then mark them ready after frozen-release checks pass.
disable-model-invocation: true
metadata:
  layer: runner
---

# Open Stack Requests

Create or refresh change requests (CRs) from the canonical release manifest.
Use draft mode as each branch stabilizes; use ready mode after release gates
pass. Do not implement plans or push branches.

## Inputs

Require the canonical release manifest, its plan and evidence paths, local and
remote branches, pinned parent SHAs, verified tips, review evidence from all
three providers or their equal-range-diff mappings, and intended base branch.
Infer the forge from `origin` only when unambiguous. Read
`references/change-request-lifecycle.md`,
`references/orchestration-change-requests.md`,
`references/orchestration-plans-layout.md`, and the selected provider
adapter. Read `references/change-request-description.md` when writing CR text.
Read `references/release-manifest.md` and validate the manifest first.

Choose one mode:

- `draft`: require a verified, pushed branch, passed branch-level agent checks,
  and clean reviews from Claude, Codex, and Cursor. Its plan may be in
  `plans/in_progress/` or `plans/review/`. The full candidate need not be frozen
  or integrated.
- `ready`: require the plan under `plans/review/`, a frozen manifest, final
  stack checks, and applicable forge checks on the exact source SHA.

Exclude confirmed merged branches under `plans/done/`. After a repair run,
reload the canonical manifest; plan paths may have moved during repair.

## Workflow

1. Fetch the base, dependency parents, and source branches. Require each
   parent head to equal its pinned SHA. Require each local, upstream, and
   remote source tip to equal its verified SHA. Require clean reviews from all
   three providers on that SHA or recorded mappings for all three, and require
   the pinned parent to be its ancestor. In ready mode, require final stack checks and artefacts to
   cover those exact SHAs. If any
   check failed or SHA changed, return affected ready CRs and descendants to
   draft before sending their branches to `build-branch-stack` for restack,
   verification, and review. An unexpected source change also needs the
   user's scope decision. Do not publish stale work.
2. Reconcile open CRs before creating anything. Reuse one matching draft CR
   from an earlier attempt after verifying its source, target, and author.
   Stop for a missing or changed remote branch, duplicate CR, or wrong target.
3. Create or refresh one draft CR per selected branch with the manifest target.
   Regenerate its title, description, and target from the manifest rather than
   stale spreadsheet or CR text. Verify source and target SHAs, draft state,
   effective squash support, and source retention through the provider adapter.
   Independent branches target the base. Write the CR URL and state back to the
   manifest and validate it. End here in draft mode.
4. In ready mode, query the provider for applicable branch-push and CR checks
   on each exact source SHA. Wait for every configured or policy-required check to pass.
   If none apply, record `none applicable`; a skipped or absent expected
   pipeline cannot count as a pass. If a check requires a code fix, return
   affected CRs and ready descendants to draft, then send their branches for
   verification, review, and final stack checks. Resume at step 1, then
   refresh the CRs.
5. Refetch parents and CRs. Require local, upstream, verified, and CR source
   SHAs to match; require all three direct clean reviews or their mappings;
   and require each target head to equal its pinned parent.
   Mark CRs ready and request qualified independent reviewers only after all
   applicable checks pass. On movement, return affected ready CRs to draft
   and stop for the branch workflow to restore a valid stack.

Never push branches, merge CRs, delete branches, or change repository-wide
settings. Preserve unrelated dirty work. Stop for failed checks, unresolved findings, missing
artefacts, revision drift, wrong targets, or unavailable squash support.

## Handoff

Report the mode, manifest path, each branch, parent and pinned SHA, final SHA,
verification and review evidence, CR target and URL, checks, draft or ready
status, squash evidence, and any blocker. Confirm nothing was merged.
