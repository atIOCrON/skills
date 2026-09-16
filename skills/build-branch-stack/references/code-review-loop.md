# Code Review Loop

Review successive verified and pushed commits until one clean pass covers the
exact plan-branch tip.

## Inputs

Require the repository, host mapping, plan and slug, implementation scope,
dependency-parent branch and pinned base SHA, plan branch, candidate commit,
neutral pack, reviewer preflight status, and verification evidence.

The cross-pass material concern ledger is
`plans/<plan_slug>.reviews/code-review-triage-ledger.md`.

## Pass Policy

Each numbered pass is a fresh selected-reviewer discovery review of
`<base-sha>...<review-sha>`. Targeted closure rounds do not count as passes.
One clean fresh pass is sufficient. After a material fix, close the originating
findings, then run a fresh pass on the new commit.

For each pass:

1. Confirm the review commit equals the local branch tip, upstream, fetched
   remote tip, and latest verified SHA. Confirm the dependency-parent head
   still equals the pinned base SHA and remains an ancestor.
2. Refresh `code-review-pack` for the base and review SHAs.
3. Create `plans/<plan_slug>.reviews/code-review-pass<N>/`.
4. Run `multi-review-pass-runner` with `code-review.md` and
   `code-review-loop-code-review-invocation.md`. Start all reviewers fresh and
   require exhaustive review after the first blocker.
5. Triage all outputs once. Batch accepted blocker and should-fix findings
   for the original implementation worker; do not routinely fix nits.
6. For accepted fixes, resume that worker, then:
   - prepare an exact tree through `staged-diff-scope`;
   - create a new commit through `git-branch-commit`;
   - verify the new SHA through `verification-runner` in a clean worktree;
   - push it through `git-sync-branch` and check remote SHA equality;
   - refresh the neutral pack.
7. Resume each originating reviewer once with its findings, original and
   current review SHAs, applied changes, and verification evidence. Apply
   proposed ledger transitions through the orchestrator; never share another
   reviewer's findings.
8. Repeat fixes and targeted closure until those findings close or need a
   user decision. Use targeted closure for a rejected material finding only
   when triage is uncertain, evidence conflicts, or the user requests it.
9. Resolve recurring escalations with the user before another fresh pass.

## Completion

Return `Reviewed and pushed` only when:

- at least one fresh pass ran and the newest has no accepted material finding
  or contradiction;
- all ledger entries are terminal and required closure is complete;
- the same SHA is the local branch tip, upstream, fetched remote tip, latest
  verified commit, and latest clean-reviewed commit; and
- the dependency-parent head equals the pinned base SHA and remains an
  ancestor.

Any fix commit, restack, parent change, or SHA mismatch invalidates completion
and requires verification plus a fresh pass. An unexpected remote source
change blocks until the user accepts its scope.

Report pass outcomes and SHAs, closure rounds, fixes, verification, rejected
or deferred findings, artefact paths, ledger counts, identity checks, skill
feedback, and either a blocker or `Reviewed and pushed`.
