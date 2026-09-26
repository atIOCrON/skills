# Code Review Loop

Review successive verified and pushed commits until valid review evidence
covers the exact plan-branch tip.

## Inputs

Require the repository, host mapping, vertical-slice plan and slug, parent
specification, slice map, design checkpoint, implementation scope,
dependency-parent branch and pinned base SHA, plan branch, candidate commit,
neutral pack, reviewer preflight status, verification evidence, and a completed
trim result on the current tip or a valid restack mapping. Trim passes do not
count toward this loop's discovery-pass limit or satisfy its review gate.

The cross-pass material concern ledger is
`<feature_dir>/<plan_slug>.reviews/code-review-triage-ledger.md`.

## Pass Policy

Each numbered pass is a fresh three-reviewer discovery review of
`<base-sha>...<review-sha>`. Targeted closure rounds do not count as passes.
One completed fresh pass plus terminal closure is sufficient when the reviewed
commit has not changed. After a material fix, close the originating findings,
then run a fresh pass on the new commit.
In a bounded wave, run every eligible numbered pass concurrently across
branches. Eligibility requires that branch's prior findings handled and its
current tip verified and pushed; ancestor reviews need not be clean. A
descendant may continue passes against its immutable pinned parent after that
parent moves. Record the movement and keep the descendant provisional until
the wave-boundary restack, verification, and review mapping or fresh pass.

Run at most five completed discovery passes for one plan. A pass counts when
all three reviewers have produced validated outputs and triage is recorded.
Targeted closure, same-session format or completion repair, transport retry,
valid restack or test-only mappings, and an incomplete reviewer launch do
not count. Preserve the count across task resumptions, implementation shapes,
and architecture epochs.

Assess each validated response when it arrives. Independently confirmed
material findings may start provisional edits in a separate implementation
checkout while other reviewers run. Keep the reviewed SHA, branch tip, neutral
pack, and reviewer checkout unchanged apart from expected review artefacts.
Focused checks may run in the implementation checkout; do not commit or push
provisional edits.
The pass remains incomplete until all three outputs are validated, reconciled,
and recorded in one triage. If later feedback contradicts the fix or triggers
architecture reassessment, revise or discard the provisional work.

Before deciding the post-fix review action, record a risk classification.
Treat changed production behavior, interfaces, lifecycle ownership, dependency
inputs, generated or effective output, or invalidated verification as material.
Only explanatory or evidence changes with unchanged commit and tree identities
qualify for ordinary targeted closure without fresh discovery. Treat
uncertainty as material.

One narrow exception applies when a completed discovery pass is otherwise
clean and its sole accepted finding needs only a test-only remediation. The new
commit may complete review without another discovery pass when all of these
conditions hold:

- the delta changes only test code or test-owned data;
- production, runtime, build, package, configuration, dependency, shared-fixture,
  generated-output, interface, behavior, ownership, and effective-result
  identities are unchanged;
- the new SHA passes exact-candidate verification, including direct execution
  of every added or changed test; unaffected checks may use deterministic reuse;
- every other ledger entry is terminal; and
- each reviewer who originated the accepted finding confirms closure in the
  original session against the old and new SHAs.

Record `test_only_closure` mappings from all three prior review SHAs to the new
SHA. A test path alone does not prove eligibility. Any uncertainty, additional
accepted finding, failed or invalidated verification, non-test delta, or
closure concern requires a fresh three-reviewer pass.

**Prospective-language invariant:** Starting a fresh pass does not establish
that it will be the final pass. Material findings may require fixes, targeted
closure, and another fresh pass. In plans, progress updates, prompts, and
handoffs, use the numbered pass only. Do not predict that it is the final review
cycle.

Correct: “Pass 5 is running against the verified SHA.”\
Correct: “If pass 5 is clean, the branch may satisfy review completion.”\
Incorrect: “The final pass is running.”\
Incorrect: “This is the last review cycle.”\
Retrospectively correct: “Pass 5 was the last required pass; review is complete.”

A conflict-free restack retains prior clean reviews when `git range-diff` is
equal and deterministic checks prove the logical change and effective behavior
under the new parent are unchanged. Verify the new tip, record old-to-new SHA
mappings, and refresh the pack. For an unequal range diff, use `reviewed_restack`
only through one of these focused paths:

**Inherited test context.** Require all of these:

- Each old child commit maps to one new commit in the same order, with matching
  stable patch IDs and byte-identical added and deleted lines in each path.
  No child hunk, file ownership, or commit is added, dropped, or manually
  resolved.
- Every range-diff inequality is explained by inherited test context or commit
  metadata. Inspect the complete old and new tests, not just their changed
  lines. The parent change is separately verified and reviewed; deterministic
  checks prove unchanged production and effective behavior under that parent.
- Verify the exact new tip and directly run every affected test. Give all three
  original reviewers the old and new ranges, parent delta, unequal hunks, full
  affected tests, and verification evidence. Each must confirm in its original
  session that its clean conclusion still applies under the new context.

**Generated metadata conflict.** A manual resolution may retain prior clean
reviews only when every resolved hunk changes generated metadata, such as a
`composer.lock` root content hash, and all of these hold:

- Inspect every resolved hunk and both complete commit ranges. Reproduce the
  new metadata byte-for-byte from the combined inputs. Confirm unchanged locked
  packages, dependency graph, and patch order; require byte-identical child
  source, tests, configuration, and non-metadata generated output.
- Prove unchanged effective behavior under the new parent. Its own changes must
  be separately verified and reviewed or validly mapped; until then, retain
  only provisional descendant status.
- Verify the exact new tip and directly run affected integration tests. Give one
  independent reviewer the old/new ranges, resolved hunks, parent delta,
  identity proof, and test results. Record its focused conclusion on the
  resolution and parent interaction. A concern blocks the mapping.

Record the chosen path, confirmations, identity proof, and intermediate SHA
mappings from all three directly reviewed tips in the pack. This focused review
does not count as a discovery pass. Matching patch IDs or passing tests alone
never establish the mapping. Unexplained inequality, changed child behavior or
effective output, failed check, missing proof, or reviewer concern requires a
fresh three-reviewer pass.
If the pass cap was reached before this mapping, retain the cap event and pass
count in the ledger; mark the manifest clean only after all mapping gates pass.

When only explanatory or verification evidence changes, confirm the pinned
base, commit, and tree SHAs are unchanged. Refresh the pack's evidence and
deterministic checks, then ask only the originating reviewer in its original
session to assess its finding. Record its closure and update the ledger; mark
the same SHA clean-reviewed only after all findings are terminal. Do not run
another discovery pass solely for added evidence. A code change, restack,
parent change, failed verification, or new contradiction still blocks ordinary
evidence-only closure. A code change follows the normal review path unless it
meets the test-only exception above.

For each pass:

1. Confirm the review commit equals the local branch tip, upstream, fetched
   remote tip, and latest verified SHA. Require the pinned base to remain an
   ancestor. Record any dependency-parent head movement; it makes a wave
   descendant provisional but does not block a pass on the pinned diff.
2. Refresh `code-review-pack` for the base and review SHAs.
3. Create `<feature_dir>/<plan_slug>.reviews/code-review-pass<N>/`.
4. Run `multi-review-pass-runner` with `code-review.md` and
   `code-review-loop-code-review-invocation.md`. Start all three reviewers fresh
   and require exhaustive review after the first blocker. Validate each output
   before triage. Repair malformed or incomplete output in the originating
   session; do not replace a completed reviewer merely because its response
   violated the schema.
5. As each output validates, assess its evidence class, pinned SHA, supported
   path, failure family, and prior ledger history. Reject static hypotheses.
   Before provisional dispatch, check the architecture and fix-cycle rules and
   whether removing or simplifying new machinery is the smaller resolution.
   After all three outputs validate and the runner's mutation check passes,
   triage them together. Batch accepted blocker and should-fix findings for the
   original worker, including any needed changes to provisional edits. Do not
   routinely fix nits. Skill feedback and closure observations cannot trigger
   a fix, ledger entry, or another pass.
6. If one failure family or branch-introduced coordinator, state machine, retry
   system, lifecycle interception, or verification model caused newly
   discovered material failures in any two fresh passes recorded in the ledger,
   stop incremental fixes and mark the ledger `architecture-review-required`.
   Changing implementation shape or epoch does not reset this count. Group
   failures by invariant; compare removal, simplification, native ownership,
   upgrade, narrow dependency correction, and prerequisite splitting; then
   select the smallest viable design. Amend the plan and design checkpoint,
   start a new architecture epoch, and continue. Require the user only when
   every viable option crosses the calling skill's authority boundary.
7. For accepted fixes, keep the feature in `in_progress/` and resume that
   worker, then:
   - prepare an exact tree through `staged-diff-scope`;
   - create a new commit through `git-branch-commit`;
   - verify the new SHA through `verification-runner` in a clean worktree;
   - push it through `git-sync-branch` and check remote SHA equality;
   - refresh the neutral pack at the current feature path.
8. Resume each originating reviewer once with its findings, original and
   current review SHAs, applied changes, and verification evidence. Apply
   proposed ledger transitions through the orchestrator; never share another
   reviewer's findings. Use artefact paths from the feature's current stage.
9. Repeat fixes and targeted closure until those findings close or reach an
   architecture or authority boundary. Use targeted closure for a rejected
   material finding when triage is uncertain, evidence conflicts, new evidence
   addresses it, or the user requests it.
10. After closure, record eligible test-only mappings or start the next fresh
    pass. Another pass is not authorized merely because a reviewer proposed an
    edge case. After two accepted fix cycles in one failure family, prohibit a
    third local variation and make the autonomous continuation decision defined
    by the ledger protocol. Continue only for a confirmed material defect and a
    viable, non-repeated disposition. Ask the user only when every viable option
    crosses the calling skill's authority boundary. After processing pass 5,
    commit, verify, and push its accepted in-scope remediation under the normal
    rules and complete targeted closure. If the resulting tip still requires a
    fresh discovery pass, do not start pass 6. Record the review-cap marker,
    return `Review cap reached`, and let the caller continue other eligible
    plans.

## Completion

Return `Reviewed and pushed` only when:

- at least one fresh pass from all three reviewers covered the logical change,
  directly on the current SHA or through recorded valid restack or
  test-only-closure mappings, and no material finding or contradiction remains
  unresolved after targeted closure;
- all ledger entries are terminal and required closure is complete;
- the same SHA is the local branch tip, upstream, fetched remote tip, and latest
  verified commit, with either direct clean reviews from all three reviewers or
  valid mappings from all three clean-reviewed logical changes; and
- the pinned base remains an ancestor.

If the parent head has moved, return `Reviewed provisionally` rather than
`Reviewed and pushed`. Restack at the wave boundary and verify the new tip;
keep an already completed slice in `review/`. Map prior reviews or run a fresh pass
when below the cap. For a capped branch, carry an accepted human disposition
through a recorded valid restack mapping only when effective behavior and the
accepted unresolved findings' risk remain unchanged. Keep the original
decision SHA and map it to the new verified tip; do not repeat the human decision.

Any ineligible fix commit, manual resolution outside the generated-metadata
path, unexplained range-diff inequality, behavior change, or unexplained SHA
mismatch invalidates completion and requires verification plus a fresh pass
when below the cap. At the cap, remediate or seek a new human decision only if
the old acceptance cannot be proven applicable to the new verified tip. Never
mark automated reviews clean on the strength of human acceptance.
Valid restack and eligible test-only mappings need verification and recorded
evidence, not another discovery review. An unexpected remote source change
blocks until the user accepts its scope.

Report pass outcomes and SHAs, closure rounds, fixes, verification, rejected
or deferred findings, artefact paths, ledger counts, identity checks, skill
feedback, and one of `Reviewed and pushed`, `Reviewed provisionally`,
`Review cap reached`, or a blocker.
