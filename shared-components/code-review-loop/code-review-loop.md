# Code Review Loop

Review successive verified and pushed commits until valid review evidence
covers the exact plan-branch tip.

## Inputs

Require the repository, host mapping, vertical-slice plan and slug, parent
specification, slice map, design checkpoint, implementation scope,
dependency-parent branch and pinned base SHA, plan branch, candidate commit,
neutral pack, reviewer preflight status, and verification evidence.

The cross-pass material concern ledger is
`<feature_dir>/<plan_slug>.reviews/code-review-triage-ledger.md`.

## Pass Policy

Each numbered pass is a fresh three-reviewer discovery review of
`<base-sha>...<review-sha>`. Targeted closure rounds do not count as passes.
One completed fresh pass plus terminal closure is sufficient when the reviewed
commit has not changed. After a material fix, close the originating findings,
then run a fresh pass on the new commit.

Run at most five completed discovery passes for one plan. A pass counts when
all three reviewers have produced validated outputs and triage is recorded.
Targeted closure, same-session format or completion repair, transport retry,
equal-range-diff or test-only mappings, and an incomplete reviewer launch do
not count. Preserve the count across task resumptions, implementation shapes,
and architecture epochs.

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

A conflict-free restack does not require another discovery review when
`git range-diff` is equal and deterministic identity checks show the logical
change is unchanged. Verify the new commit, record the old-to-new SHA mapping,
refresh the pack, and retain all three prior clean reviews. Any manual resolution,
unequal range diff, changed generated output, or intentional behavior change
requires a fresh three-reviewer pass. Do not treat a generated-artifact
conflict by itself as a behavioral change when deterministic regeneration
proves equality.

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
   remote tip, and latest verified SHA. Confirm the dependency-parent head
   still equals the pinned base SHA and remains an ancestor.
2. Refresh `code-review-pack` for the base and review SHAs.
3. Create `<feature_dir>/<plan_slug>.reviews/code-review-pass<N>/`.
4. Run `multi-review-pass-runner` with `code-review.md` and
   `code-review-loop-code-review-invocation.md`. Start all three reviewers fresh
   and require exhaustive review after the first blocker. Validate each output
   before triage. Repair malformed or incomplete output in the originating
   session; do not replace a completed reviewer merely because its response
   violated the schema.
5. Triage all outputs once. Batch accepted blocker and should-fix findings for
   the original implementation worker only after triage independently confirms
   their evidence class, pinned SHA, supported path, and failure family. Reject
   static hypotheses. Do not routinely fix nits. Before dispatch, ask whether
   removing or simplifying new machinery is the smaller resolution. Skill
   feedback and closure observations cannot trigger a fix, ledger entry, or
   another pass.
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
  directly on the current SHA or through recorded equal-range-diff or
  test-only-closure mappings, and no material finding or contradiction remains
  unresolved after targeted closure;
- all ledger entries are terminal and required closure is complete;
- the same SHA is the local branch tip, upstream, fetched remote tip, and latest
  verified commit, with either direct clean reviews from all three reviewers or
  valid mappings from all three clean-reviewed logical changes; and
- the dependency-parent head equals the pinned base SHA and remains an
  ancestor.

Any ineligible fix commit, manual restack resolution, unequal range diff,
behavior change, or unexplained SHA mismatch invalidates completion and
requires verification plus a fresh pass. Equal-range-diff restacks and eligible
test-only remediations need verification and recorded mappings, not another
discovery review. An unexpected remote source change blocks until the user
accepts its scope.

Report pass outcomes and SHAs, closure rounds, fixes, verification, rejected
or deferred findings, artefact paths, ledger counts, identity checks, skill
feedback, and one of `Reviewed and pushed`, `Review cap reached`, or a blocker.
