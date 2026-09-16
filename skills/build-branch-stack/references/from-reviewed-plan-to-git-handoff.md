# From Reviewed Plan To Git Handoff

Implement one reviewed plan, push each verified revision, and review the exact
pushed commit until clean. Do not create a change request.

## Inputs

Require an approved `<feature_dir>/<slug>.md` in `in_progress/`, implementation
ownership, plan branch, dependency-parent branch, and pinned parent SHA. The
caller creates or validates and checks out the plan branch first.

## Route

1. Load the plan, `AGENTS.md` where present, and applicable repository
   standards and contracts.
2. Select the host mapping through `orchestration-runtime.md`. Have the initial
   implementation worker assess any adopted branch tip against the plan and
   complete remaining implementation.
3. For new edits, use `staged-diff-scope.md` for selective staging and
   self-review. Block staged/unstaged overlap on candidate files.
4. Use `git-branch-commit.md` to commit an approved new candidate tree. If
   the adopted tip already satisfies the plan, use that commit as candidate.
5. Use `verification-runner.md` to verify the exact commit in a clean detached
   worktree. Fix failures through new commits and verify each new SHA.
6. Use `git-sync-branch.md` to create or update the remote branch at the
   verified SHA.
7. Keep the feature in `in_progress/`. Build the neutral commit-pinned review
   pack and run reviewer preflight for the selected non-host providers.
8. Run `code-review-loop.md`. Verify, push, and review every accepted fix
   commit.
9. Require the local branch tip, upstream, remote, latest verified SHA, and
   latest clean-reviewed SHA to match. Require the parent head to equal its
   pinned SHA and remain an ancestor. Produce the branch handoff evidence.

Stop for insufficient ownership, ambiguous scope, staged/unstaged overlap,
failed verification or review, unresolved findings, failed push, parent
movement, revision mismatch, or unpreserved artefacts.

Report the plan, branch and pinned parent, changed files, candidate and final
SHAs, upstream SHA, verification, review passes, ledger, artefact paths, and
either a blocker or `Reviewed and pushed`.
