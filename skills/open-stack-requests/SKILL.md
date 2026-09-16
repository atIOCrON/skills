---
name: open-stack-requests
description: Open draft GitLab, GitHub, or Bitbucket Cloud change requests for a verified remote branch stack, then mark them ready after applicable checks pass.
disable-model-invocation: true
metadata:
  layer: runner
---

# Open Stack Requests

Turn the verified remote branches from `build-branch-stack` into change
requests (CRs). Do not implement plans, push branches, or treat an old review
as valid for a new commit.

## Inputs

Require the stack manifest, its plan and evidence paths, local and remote
branches, pinned parent SHAs, verified and clean-reviewed tip SHAs, and
intended base branch. Infer the forge from `origin` only when unambiguous. Read
`references/change-request-lifecycle.md`,
`references/orchestration-change-requests.md`,
`references/orchestration-plans-layout.md`, and the selected provider
adapter. Read `references/change-request-description.md` when writing CR text.
Require each branch being published to have a manifest plan path under
`plans/review/`. Exclude confirmed merged branches under `plans/done/`. After a
repair run, reload the manifest from the path reported by `build-branch-stack`;
its feature directory may have moved during repair.

## Workflow

1. Fetch the base, dependency parents, and source branches. Require each
   parent head to equal its pinned SHA. Require each local, upstream, and
   remote source tip to equal its verified and clean-reviewed SHA, and require
   the pinned parent to be its ancestor. Require final stack checks and
   artefacts to cover those exact SHAs. If any
   check failed or SHA changed, return affected ready CRs and descendants to
   draft before sending their branches to `build-branch-stack` for restack,
   verification, and review. An unexpected source change also needs the
   user's scope decision. Do not publish stale work.
2. Reconcile open CRs before creating anything. Reuse one matching draft CR
   from an earlier attempt after verifying its source, target, and author.
   Stop for a missing or changed remote branch, duplicate CR, or wrong target.
3. Create or refresh one draft CR per selected branch with the explicit
   dependency parent as target. Verify source and target SHAs, draft state,
   effective squash support, and source retention through the provider
   adapter. Independent branches target the base.
4. Query the provider for applicable branch-push and CR checks on each exact
   source SHA. Wait for every configured or policy-required check to pass.
   If none apply, record `none applicable`; a skipped or absent expected
   pipeline cannot count as a pass. If a check requires a code fix, return
   affected CRs and ready descendants to draft, then send their branches for
   verification, review, and final stack checks. Resume at step 1, then
   refresh the CRs.
5. Refetch parents and CRs. Require local, upstream, verified, reviewed, and
   CR source SHAs to match, and each target head to equal its pinned parent.
   Mark CRs ready and request qualified independent reviewers only after all
   applicable checks pass. On movement, return affected ready CRs to draft
   and stop for the branch workflow to restore a valid stack.

Never push branches, merge CRs, delete branches, or change repository-wide
settings. Preserve unrelated dirty work. Stop for failed checks, unresolved findings, missing
artefacts, revision drift, wrong targets, or unavailable squash support.

## Handoff

Report each branch, parent and pinned SHA, final SHA, verification and review
evidence, CR target and URL, checks, ready status, squash evidence, and any
blocker. Confirm nothing was merged.
