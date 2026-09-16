# From Reviewed Plan To Git Handoff

Implement one reviewed plan on its plan branch, publish a verified draft change
request, and review the exact committed revision until it is ready for human
review.

## Inputs

Require an approved `plans/<slug>.md`, implementation ownership, plan branch,
dependency-parent branch, and pinned parent SHA. The caller must create and
check out the plan branch before this route starts.

## Route

1. Load `AGENTS.md`, the plan, and required repository standards.
2. Select the host mapping through `orchestration-runtime.md`.
3. Dispatch the initial implementation.
4. Use `staged-diff-scope.md` for selective staging and self-review. Block any
   file with both staged and unstaged edits.
5. Use `git-branch-commit-push.md` to commit the approved candidate tree.
6. Use `verification-runner.md` to verify that commit in a clean detached
   worktree. Fix failures through new commits and verify each new SHA.
7. Push the verified commit, then use `change-request-lifecycle.md` and the
   selected forge adapter to create the draft CR against the dependency parent.
8. Build the neutral commit-pinned review pack.
9. Run reviewer preflight for the selected non-host providers.
10. Run `code-review-loop.md`. Every accepted fix becomes a new verified and
    pushed commit on the draft CR.
11. Confirm the latest clean-reviewed SHA equals local `HEAD`, upstream, CR
    source, and latest verified SHA; confirm the CR target head still equals the
    pinned parent SHA.
12. Use the same provider adapter to mark the CR ready and request review.
13. Produce the concise final handoff.

## Stop Conditions

Stop for insufficient ownership, ambiguous scope, staged/unstaged overlap,
failed verification, reviewer failure, unresolved material findings, an
unclassified or failed restack, revision mismatch, or a CR target or effective
squash mismatch.

## Output

Report the plan, branch and pinned base, changed files, candidate and final SHAs,
verification, review passes, ledger, draft-to-ready CR status, artefact paths,
and either a blocker or `Ready for human review`.
