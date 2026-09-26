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

Require the canonical manifest, plan and evidence paths, branches, pinned
parent SHAs, verified tips, and intended base branch. Ready mode also needs
current-tip reviews or an accepted capped disposition.
Infer the forge from `origin` only when unambiguous. Read
`references/change-request-lifecycle.md`,
`references/orchestration-change-requests.md`,
`references/orchestration-plans-layout.md`, and the selected provider
adapter. Read `references/change-request-description.md` when writing CR text.
Read `references/release-manifest.md` and validate the manifest first.

Choose one mode:

- `draft`: require a verified, pushed branch, passed branch-level agent checks,
  and a pinned parent that is an ancestor. Its plan may be in
  `plans/in_progress/` or `plans/review/`; ancestor reviews and the full
  candidate may still be pending.
- `ready`: require the plan under `plans/review/`, a frozen manifest, final
  stack checks, current-tip trim and reviews or accepted capped disposition,
  qualified pinned ancestors, and forge checks on the exact source SHA.

Exclude confirmed merged branches under `plans/done/`. After a repair run,
reload the canonical manifest; plan paths may have moved during repair.

## Workflow

1. Fetch the base, parents, and source branches. Require local, upstream, and
   remote source tips to equal the verified SHA, and the pinned parent to be
   its ancestor. In ready mode, require each parent head at its pin, every
   required ancestor's review gate, proportionate trim, clean reviews or an
   accepted capped disposition on each current tip, and final stack checks
   and artefacts on those SHAs. If any
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
   SHAs to match; require automation-clean reviews or an accepted capped
   disposition on each exact tip;
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
