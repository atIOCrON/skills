# Code Review Loop

Review successive verified and pushed commits until one clean pass covers the
exact plan-branch tip.

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

**Prospective-language invariant:** Starting a fresh pass does not establish
that it will be the final pass. Material findings may require fixes, targeted
closure, and another fresh pass. In plans, progress updates, prompts, and
handoffs, use the numbered pass only. Do not predict that it is the final review
cycle.

Correct: “Pass 6 is running against the verified SHA.”\
Correct: “If pass 6 is clean, the branch may satisfy review completion.”\
Incorrect: “The final pass is running.”\
Incorrect: “This is the last review cycle.”\
Retrospectively correct: “Pass 6 was the last required pass; review is complete.”

A conflict-free restack does not require another discovery review when
`git range-diff` is equal and deterministic patch checks show the logical
change is unchanged. Verify the new commit, record the old-to-new SHA mapping,
refresh the pack, and retain all three prior clean reviews. Any manual resolution,
unequal range diff, changed generated output, or intentional behavior change
requires a fresh three-reviewer pass. Do not treat a generated lockfile
conflict by itself as a behavioral change when deterministic regeneration
proves equality.

When only explanatory or verification evidence changes, confirm the pinned
base, commit, and tree SHAs are unchanged. Refresh the pack's evidence and
deterministic checks, then ask only the originating reviewer in its original
session to assess its finding. Record its closure and update the ledger; mark
the same SHA clean-reviewed only after all findings are terminal. Do not run
another discovery pass solely for added evidence. A code change, restack,
parent change, failed verification, or new contradiction still blocks closure
and follows the normal review path.

For each pass:

1. Confirm the review commit equals the local branch tip, upstream, fetched
   remote tip, and latest verified SHA. Confirm the dependency-parent head
   still equals the pinned base SHA and remains an ancestor.
2. Refresh `code-review-pack` for the base and review SHAs.
3. Create `<feature_dir>/<plan_slug>.reviews/code-review-pass<N>/`.
4. Run `multi-review-pass-runner` with `code-review.md` and
   `code-review-loop-code-review-invocation.md`. Start all three reviewers fresh
   and require exhaustive review after the first blocker.
5. Triage all outputs once. Batch accepted blocker and should-fix findings
   for the original implementation worker; do not routinely fix nits. Before
   dispatch, ask whether removing or simplifying new machinery is the smaller
   resolution.
6. If one branch-introduced coordinator, state machine, retry system, or
   lifecycle interception caused newly discovered material failures in this and
   the immediately preceding fresh pass, stop the fix loop. Mark the ledger as
   `architecture-review-required` and return to the design checkpoint for
   simplification, splitting, upgrade, upstream correction, or a different
   extension mechanism.
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
9. Repeat fixes and targeted closure until those findings close or need a
   user decision. Use targeted closure for a rejected material finding when
   triage is uncertain, evidence conflicts, new evidence addresses it, or the
   user requests it.
10. Resolve recurring escalations with the user before another fresh pass.

## Completion

Return `Reviewed and pushed` only when:

- at least one fresh pass from all three reviewers covered the logical change,
  directly on the current SHA or through recorded equal-range-diff restack
  mappings, and no material finding or contradiction remains unresolved after
  any targeted closure;
- all ledger entries are terminal and required closure is complete;
- the same SHA is the local branch tip, upstream, fetched remote tip, and latest
  verified commit, with either direct clean reviews from all three reviewers or
  recorded equal-range-diff mappings from all three clean-reviewed logical
  changes; and
- the dependency-parent head equals the pinned base SHA and remains an
  ancestor.

Any fix commit, manual restack resolution, unequal range diff, behavior change,
or unexplained SHA mismatch invalidates completion and requires verification
plus a fresh pass. An equal-range-diff mechanical restack needs verification
and recorded identity evidence, not another discovery review. An unexpected
remote source change blocks until the user accepts its scope.

Report pass outcomes and SHAs, closure rounds, fixes, verification, rejected
or deferred findings, artefact paths, ledger counts, identity checks, skill
feedback, and either a blocker or `Reviewed and pushed`.
