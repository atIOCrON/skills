# Code Review Loop

Review successive verified commits until one clean pass covers the exact pushed
revision in the draft change request.

## Inputs

Require the repository, host mapping, plan and slug, implementation scope,
dependency-parent branch and pinned base SHA, plan branch, current candidate commit,
draft CR, neutral pack, reviewer preflight status, and verification evidence for
the candidate SHA.

The cross-pass material concern ledger is
`plans/<plan_slug>.reviews/code-review-triage-ledger.md`.

## Pass Policy

Each numbered pass is a fresh selected-reviewer discovery review of
`<base-sha>...<review-sha>`. Targeted closure rounds do not count as passes. One
clean fresh pass is sufficient. After a material fix, close the originating
findings, then run a fresh pass on the new commit.

For each pass:

1. Confirm the review commit equals local `HEAD`, upstream, the draft CR source
   SHA, and the latest verified SHA. Confirm the CR target head still equals the
   pinned base SHA and remains an ancestor.
2. Refresh `code-review-pack` for the base and review SHAs.
3. Create `plans/<plan_slug>.reviews/code-review-pass<N>/`.
4. Run `multi-review-pass-runner` with `code-review.md` and
   `code-review-loop-code-review-invocation.md`. Start all reviewers fresh and
   require exhaustive review after the first blocker.
5. Triage all outputs once. Batch accepted blocker and should-fix findings for
   the original implementation worker; do not routinely fix nits.
6. For accepted fixes, resume that worker, then:
   - prepare an exact tree through `staged-diff-scope`;
   - create a new commit through `git-branch-commit-push`;
   - verify the new SHA through `verification-runner` in a clean worktree;
   - push it without force;
   - refresh the draft CR description for the new SHA;
   - refresh the neutral pack.
7. Resume each originating reviewer once with its findings, original and current
   review SHAs, applied changes, and verification evidence. Apply proposed ledger
   transitions through the orchestrator; never share another reviewer's findings.
8. Repeat fixes and targeted closure until those findings close or require a
   user decision.
9. Use targeted closure for a rejected material finding only when triage is
   uncertain, evidence conflicts, or the user requests it.
10. Resolve recurring escalations with the user before another fresh pass.

## Completion

Return `Ready for CR review` only when:

- at least one fresh pass ran and the newest has no accepted material finding
  or contradiction;
- all ledger entries are terminal and required closure is complete;
- the same SHA is local `HEAD`, upstream, CR source, latest verified commit, and
  latest clean-reviewed commit;
- the CR target head equals the pinned base SHA and remains an ancestor; and
- the CR remains draft with the correct dependency-parent target.

Any fix commit, restack, target change, or SHA mismatch invalidates completion
and requires verification plus a fresh pass. An unexpected source change blocks
until the user accepts its scope; then return the CR to draft before review.

## Output

Report pass outcomes and SHAs, closure rounds, fixes, verification, rejected or
deferred findings, artefact paths, ledger counts, identity checks, skill
feedback, and either a blocker or `Ready for CR review`.
