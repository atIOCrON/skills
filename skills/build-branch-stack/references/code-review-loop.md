# Code Review Loop

Review immutable pinned parent-to-tip diffs until current-tip evidence qualifies
or the five-pass cap is exhausted. The persistent implementation owner runs the
loop; coordinator owns canonical state, moves and publication.

## Inputs and pass rules

Require approved slice/parent/map/checkpoint/ownership, repo/host, parent branch/
base and candidate pins, neutral pack/preflight, exact verification and current or
mapped proportionate trim. Prepared authoring reviews stay schedule.work; acceptance
resets no counts. Ledger: `<feature_dir>/<plan_slug>.reviews/code-review-triage-ledger.md`.

Discovery = fresh parallel Claude/Codex/Cursor on `<base-sha>...<review-sha>`, counted
only after three substantive pinned outputs, preserved findings, mutation check and
one triage under multi-review-pass-runner. At least one discovery plus terminal
closure suffices on unchanged commit. Limit five completed passes across resumes/
designs/epochs; closure/clarification/repair/retry/mappings/incomplete launches add
none. Return operational receipts/counts together, retaining disqualifications;
only historical records use v1 tools. Number passes, never predict final/last/closing.

Eligible verified pushed tips with handled prior findings/valid trim review
concurrently across branches up to capacity, even with moving/unreviewed ancestors.
Keep immutable review refs/pack/checkouts. Confirmed findings may start isolated
provisional edits/focused checks after convergence assessment, no commit/push until
all three reconcile; preserve assessments and discard unsupported edits.

## Review action

Record risk: changed production/interface/ownership/dependency/generated/effective
behavior or invalidated checks is material, as is uncertainty. Material/unmapped
changes need closure and fresh discovery below cap. Evidence-only closure requires
unchanged base/commit/tree, refreshed proof/hash/checks and originating-session
assessment; failed verification/contradiction or an existing code defect prevents
that shortcut. Other exceptions require every condition below.

### Test-only exception

Require all of these: the completed discovery is otherwise clean with exactly
one accepted finding; delta is only test code/test-owned data; production,
runtime/build/package/config/dependency/shared-fixture/generated/interface/
behavior/ownership/effective identities are unchanged; exact new tip verifies,
including direct execution of every changed/added test (unaffected checks may
reuse proof); every other ledger entry is terminal; every originating reviewer
confirms closure in its original session against old/new SHAs. Record mappings
from all three prior reviewed SHAs to new tip. A test path alone is no proof;
extra accepted findings, uncertainty, invalid/failed verification, non-test delta
or closure concern require fresh discovery.

### Restack mappings

Equal `git range-diff` alone is insufficient: prove unchanged logical change and
effective behavior under the new parent with deterministic checks, verify exact
new tip, record old/new mappings and refresh pack.

For unequal diffs, choose one focused path:

- **Inherited test context:** one-to-one same-order child commits, matching stable
  patch IDs and byte-identical added/deleted lines in every path; no added,
  dropped, reowned or manually resolved child hunk/commit. Explain every inequality
  by inherited test context or metadata; inspect complete old/new tests. Parent
  change is separately verified/reviewed and effective production behavior stays
  unchanged. Directly run affected tests on exact new tip. All three original
  reviewers, in original sessions, receive old/new ranges, parent delta,
  unequal hunks, full affected tests and checks; each confirms continued coverage.
- **Generated metadata conflict:** every resolved hunk is generated metadata
  (for example lockfile root hash). Inspect full ranges/hunks and reproduce it
  byte-for-byte from combined inputs; locked packages, dependency graph, patch
  order, child source/tests/config and non-metadata output remain unchanged.
  Prove effective behavior under separately verified/reviewed or mapped parent;
  descendants stay provisional meanwhile. Verify exact tip and directly run
  affected integration tests. One independent reviewer receives ranges, hunks,
  parent delta, identities and results, and confirms resolution/interaction.

Record path, proof, confirmations and intermediate mappings from all three
directly reviewed tips in the pack. Focused confirmations add no discovery pass.
Patch IDs/tests alone never establish equivalence. Unexplained inequality,
changed behavior/output, failed check, missing proof or reviewer concern prevents
mapping. Manual resolutions outside the generated-metadata path require discovery.
If the cap was already reached, retain its event/count; mark clean only when all
mapping gates establish clean coverage.

## Execute each pass

1. Confirm local/upstream/fetched-remote/reviewed/verified equality and base ancestry;
   parent movement records provisional status. Refresh code-review-pack; create
   `<feature_dir>/<plan_slug>.reviews/code-review-pass<N>/`.
2. Run multi-review-pass-runner with code-review and
   code-review-loop-code-review-invocation. Exhaust defects after first blocker;
   preserve/normalize locally, clarify only substance/scope/identity after saved
   evidence, never restart for formatting.
3. Assess supported pinned proof/families/prior ledger; reject hypotheses without
   deleting reported findings. Apply review-convergence and ledger thresholds before
   further edits (two-pass architecture ratchet, two-cycle continuation, persistent
   counts). Consider deletion/simplification first. After three substantive outputs/
   mutation check, triage once and batch accepted material fixes to existing owner,
   reconciling provisional work. Nits/skill feedback/closure observations authorize
   no routine fix, ledger entry or pass.
4. Coordinator returns implementation-needing slices in_progress. Owner selectively
   stages/new-commits, cleanly verifies and publishes through coordinator/lease,
   confirms remote and refreshes current-path pack. Follow staged-diff-scope,
   git-branch-commit, verification-runner and git-sync-branch.
5. Resume originating reviewers with only their own IDs/old-current SHAs/changes/
   checks under code-review-closure and code-review-loop-closure-invocation; owner
   applies proposed ledger transitions. Rejected material findings need closure for
   uncertainty/conflicting/new evidence or user request. Repeat until terminal or
   architecture/authority boundary; no cross-reviewer findings. Human input only if
   every viable continuation crosses caller authority.
6. Record eligible mappings or next warranted discovery, never merely for proposed
   edge cases. After pass 5 complete accepted fixes/checks/push/closure; remaining
   discovery need records cap marker/Review cap reached, no pass 6. Continue other work.

## Completion and handoff

`Reviewed and pushed` requires all ledger entries terminal, no unresolved material
finding/contradiction, required closure, at least one three-reviewer discovery
covering the logical change directly or by valid mappings, exact verified/local/
upstream/fetched-remote equality, and pinned-base ancestry. Pending placement or
moved parent returns `Reviewed provisionally`; settle restack, verify/map or
review below cap. Routine restacks retain `review` stage. Rewritten `in_release`
sources invalidate pinned membership; reconcile under plans layout before release.

Capped human acceptance carries through a proven restack only with unchanged
effective behavior and accepted finding risk. Keep original decision SHA and
valid mapping to verified new tip; no repeated decision when applicable. Otherwise
remediate or seek a new decision. Human acceptance never makes automated reviews
clean. Unexpected remote source movement blocks until the user accepts its scope.

Return pass/closure outcomes and SHAs, fixes/checks, rejected/deferred findings,
artefact paths, ledger counts, identity checks, skill feedback and exactly one of
`Reviewed and pushed`, `Reviewed provisionally`, `Review cap reached`, or a blocker.
