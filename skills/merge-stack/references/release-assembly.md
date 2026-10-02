# Release Assembly

Use `mode: release` and provider `bitbucket-cloud`. The strategy defaults to
`merge-commit`; squash requires an explicit `strategy: squash` override. Read `release-preparation.md`,
`provider-contract.md`, and `run-journal.md`. Require an authenticated Bitbucket
adapter and Git supporting `merge-tree --write-tree`.

This mode accepts a mixture of independent roots and stacked chains from the
preparation record. It launches no code review loops, edits no feature code,
and does not invoke build or review skills. User merge confirmation is required
as specified in the record; applicable Bitbucket checks and approvals still
apply. Do not require extra independent review, protected integration branches,
or strict GitHub/GitLab policies that Bitbucket has not configured.

## Preflight

Fetch the base, integration, and all sources in an isolated clean checkout.
Verify full input SHAs, the pinned base's ancestry, recorded PR identities,
source retention, and selected-strategy availability. Validate the recorded mixed
order directly against ancestry; do not feed it to the standard linear
layout classifier. Stop for hidden scope or unexpected ref movement.

On resume, call `scripts/reconcile_run.sh`. Confirm each completed merge using
its recorded `merge_method`, source and pre-merge target SHA before recording
success. Skip only proven completions; never repeat an unknown merge.

## Each PR

1. Require every selected predecessor to have a confirmed merge into
   integration. Retarget this PR to integration with `retarget_change.sh` when
   necessary. Refresh its diff and configured checks after retargeting.
2. Preserve its original head by default. Ordinary merge commits retain ancestor
   commits, so do not rebase merely because a predecessor landed. Verify the
   feature delta and resulting merge; earlier integration resolutions can still
   conflict with later branches. Stop on a conflict, failed check, or unexpected
   delta. Report the owning branch and completed prefix without editing runtime
   code, dependency locks, patches, or tests. A necessary source repair/restack
   belongs to a separately authorized repair; it invalidates the old head's
   verification and merge authorization. Never launch review loops implicitly.
   With an explicit squash override, remove the already-squashed prefix when
   restacking successors using `rebase_stack_branch.sh` and the old parent pin.
   Verify the resulting diff and head, update the preparation record, and obtain
   authorization for any new head before merging. Existing head authorization
   does not cover a rebase. No review loops run in this mode.
3. Fetch and pin integration's current SHA; require it to equal the last
   confirmed result or the original starting SHA. Check the exact source:

   ```bash
   scripts/wait_for_change_checks.sh bitbucket-cloud origin <id> <head> <strategy>
   ```

   Inspect configured expected CI as well as provider merge checks. Set
   `BITBUCKET_REQUIRED_STATUS_KEYS` to any required named statuses identified
   by the repository or release record. Missing or skipped expected checks are
   not success. With no applicable CI, record `not-required` truthfully.
4. Merge against those pinned inputs. The journal must already contain the
   user's authorization for this ID, head, and integration destination:

   ```bash
   scripts/merge_stack_change.sh bitbucket-cloud origin \
     <id> <head> <integration> <current-integration-sha> null <journal> <strategy>
   scripts/confirm_merge.sh bitbucket-cloud origin \
     <id> <head> <integration> <pre-merge-integration-sha> <journal> <strategy>
   ```

   The `null` successor is deliberate: the mixed dependency record, not the
   squash runner's single-successor gate, governs retargeting. Preserve all
   source branches. For merge commits, confirm both parents and the reproduced
   merge tree. For squash, confirm the replacement tree after updating the source
   onto the current target. Confirm source retention for both strategies.
   Bitbucket cannot receive caller-pinned head/base conditions;
   post-merge verification detects races but cannot undo them. Stop after any
   mismatch and report it; never auto-revert or continue the release.
5. Record the landed commit and PR state in preparation, then continue with the
   next eligible change. Do not update build lifecycle completion fields.

## Handoff

Return the candidate commit/tree, all PR and landed SHAs, preserved sources,
journal, checks, and any unmerged prefix or blocker. Leave feature plans in
their existing stage. The coordinator handles staging and the final PR.
