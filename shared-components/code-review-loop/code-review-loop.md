# Code Review Loop

Review successive verified and pushed commits until the required clean review
set covers the exact plan-branch tip.

## Inputs

Require the repository, host mapping, vertical-slice plan and slug, parent
specification, slice map, design checkpoint, implementation scope,
dependency-parent branch and pinned base SHA, plan branch, candidate commit,
neutral pack, reviewer preflight status, verification evidence, and review
contract: `standard` or `composer_split`.

The cross-pass material concern ledger is
`<feature_dir>/<plan_slug>.reviews/code-review-triage-ledger.md`.

## Pass Policy

Each numbered pass is a fresh three-reviewer discovery review of
`<base-sha>...<review-sha>`. Targeted closure rounds do not count as passes.
For `standard`, use one code-review phase. For `composer_split`, complete the
behavior phase before starting patch mechanics. One clean fresh pass plus
terminal closure is sufficient within each required phase when its approved
identity has not changed.

Before deciding the post-fix review action, record a risk classification.
Treat changed production behavior, interfaces, lifecycle ownership, dependency
inputs, generated or effective output, or invalidated verification as material.
Only explanatory or evidence changes with unchanged commit and tree identities
qualify for targeted closure without fresh discovery. Treat uncertainty as
material.

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

A restack does not require another discovery review when equal `git range-diff`
or capability-defined semantic identity proves the logical child change and
effective result are unchanged. Semantic identity compares parent-relative
changes, owned source and patch blobs, generated or dependency-derived outputs,
and focused behavior. Verify the new commit, record the old-to-new SHA mapping,
refresh the pack, and retain every required review. Manual resolution, unequal
range diff, or regenerated output does not invalidate reviews by itself; an
unexplained difference or behavior change does.

When only explanatory or verification evidence changes, confirm the pinned
base, commit, and tree SHAs are unchanged. Refresh the pack's evidence and
deterministic checks, then ask only the originating reviewer in its original
session to assess its finding. Record its closure and update the ledger; mark
the same SHA clean-reviewed only after all findings are terminal. Do not run
another discovery pass solely for added evidence. A code change, restack,
parent change, failed verification, or new contradiction still blocks closure
and follows the normal review path.

For each standard pass:

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

## Composer Split Review

Use this deterministic route for every Composer vendor patch:

1. Create `behavior-review-pass<N>/` and run all three fresh reviewers with
   `code-review-behavior.md` and
   `code-review-loop-behavior-invocation.md`. Give them the baseline-to-effective
   code diff and relevant runtime context. Patch-delivery mechanics are out of
   scope.
2. Triage, batch, fix, close, verify, and push as above. After every behavioral
   code change, regenerate and commit the owned patch, replay only the affected
   package from its validated prefix, and prove byte-identical effective output
   before starting the next behavior pass.
3. After a clean behavior pass and terminal closure, create
   `patch-mechanics-review-pass<N>/` and run all three fresh reviewers with
   `code-review-patch-mechanics.md` and
   `code-review-loop-patch-mechanics-invocation.md`.
4. For a mechanics-only fix, commit, run strict package replay, and compare the
   effective tree with the behavior-approved identity. If unchanged, retain the
   behavior approvals and run a fresh mechanics pass. If changed, invalidate
   both sets and return to behavior review.
5. A mechanics reviewer may report a newly established behavioral blocker, but
   it returns to behavior triage; the mechanics pass does not expand into a
   semantic rescan.

Use one ledger with a `phase` column. Number passes independently by phase.
Closure resumes the originating reviewer and preserves that finding's phase.

## Completion

Return `Reviewed and pushed` only when:

- the `standard` contract has one clean code-review pass from all three
  reviewers, or `composer_split` has both one clean behavior pass and one clean
  patch-mechanics pass from all three reviewers, directly on the current SHA or
  through valid identity mappings;
- all ledger entries are terminal and required closure is complete;
- the same SHA is the local branch tip, upstream, fetched remote tip, and latest
  verified commit, with every required review entry direct or mapped from its
  clean-reviewed logical change; and
- the dependency-parent head equals the pinned base SHA and remains an
  ancestor.

Any behavior change, unexplained restack difference, or unexplained SHA mismatch
invalidates behavior approval and requires verification plus a fresh behavior
or standard pass. In `composer_split`, a mechanics-only fix with byte-identical
effective output invalidates only mechanics approval. A semantically identical
restack needs verification and recorded identity evidence, not discovery
review. An unexpected remote source change blocks until the user accepts its
scope.

Report pass outcomes and SHAs, closure rounds, fixes, verification, rejected
or deferred findings, artefact paths, ledger counts, identity checks, per-pass
reviewer and orchestration timings, skill feedback, and either a blocker or
`Reviewed and pushed`.
