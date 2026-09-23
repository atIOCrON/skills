# From Reviewed Plan To Git Handoff

Implement one reviewed vertical-slice plan, push each verified revision, and
obtain clean reviews from Claude, Codex, and Cursor. Do not create a change
request.

## Inputs

Require an approved `<feature_dir>/<slug>.md` in `in_progress/`, implementation
ownership, plan branch, dependency-parent branch, and pinned parent SHA. The
caller creates or validates and checks out the plan branch first.

## Route

1. Load the plan, its parent specification and slice map, `AGENTS.md` where
   present, and applicable repository standards and contracts. Reject a parent
   specification as an executable plan. Require the specification and slice map
   to be `approved` and the plan's slice slug and acceptance ownership to match.
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
   pack and preflight the two non-host providers. In a bounded wave, return the
   verified, pushed candidate here so the caller can start first passes across
   the wave concurrently. A provisional descendant cannot be handed off as
   ready or published.
8. Run `code-review-loop.md` when scheduled by the caller. Verify, push, and
   review every accepted fix commit. If it returns `Review cap reached`, preserve
   the committed, verified, pushed work and artefacts. Keep the feature in
   `in_progress/` and return that state without another discovery pass. If an
   ancestor moves, pause later passes until the wave-boundary restack and
   exact-tip verification.
9. Require the local branch tip, upstream, remote, and latest verified SHA to
   match. Require all three clean reviews for that SHA or recorded
   equal-range-diff or test-only-closure mappings from all three clean-reviewed
   logical changes.
   Require the parent head to equal its pinned SHA and remain an ancestor.
   Produce the branch handoff evidence. The caller promotes the feature only
   after every ancestor is clean at its pinned SHA.

Do not promote or parent from a failing candidate. Within a bounded wave, a
verified unreviewed candidate may parent a provisional descendant. For
insufficient ownership, in-scope ambiguity, failed verification or review, or
unresolved findings, preserve evidence, return the feature to `in_progress/`,
amend the design or ownership, and continue with a new immutable candidate. For staged/unstaged
overlap, failed push, parent movement, revision mismatch, or missing artefacts,
do not overwrite work; reconcile the integrity failure or block the affected
chain. Continue independent branches. Require a human decision only at the
authority boundary defined by the calling skill.

Report the plan, branch and pinned parent, changed files, candidate and final
SHAs, upstream SHA, verification, review passes, ledger, artefact paths, and
one of a blocker, `Review cap reached`, or `Reviewed and pushed`.
