# From Reviewed Plan To Git Handoff

Implement one reviewed vertical-slice plan, push verified revisions, and finish
trim and correctness reviews or reach the correctness cap. Do not create a CR.

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
   verified, pushed candidate so the caller can run trim across the wave before
   correctness reviews. An unfinished descendant is not release-ready.
8. Require a proportionate trim result on the current tip or a valid restack
   mapping before `code-review-loop.md`. Then verify, push, and
   review every accepted fix commit. If it returns `Review cap reached`, preserve
   the committed, verified, pushed work and artefacts. Return the capped result
   for the caller to move into `review/` with a durable `review_handoff`;
   human disposition remains a separate release gate. If an
   ancestor moves, continue eligible passes against this branch's pinned diff
   and retain the provisional status until wave-boundary restack and review
   mapping or a fresh pass.
9. Require local, upstream, remote, and verified tips to match; require the
   pinned parent to be an ancestor. Return clean reviews or a cap record with
   unresolved findings, trim, checks, and exact-tip evidence. The caller moves
   the slice to `review/` after its own passes finish, regardless of ancestor
   review status. Release readiness separately requires qualified ancestors
   and clean reviews or an accepted capped disposition on the current tip.

Do not mark a candidate release-ready with failed checks or unresolved material findings
unless an authorized human explicitly accepts each finding on the exact
review-capped tip in the separate disposition.
Failed verification or integrity blocks new descendants; a verified candidate
with review findings may parent provisional descendants. For
insufficient ownership, in-scope ambiguity, failed verification or review, or
unresolved findings needing implementation, preserve evidence, return the feature to `in_progress/`,
amend the design or ownership, and continue with a new immutable candidate. For staged/unstaged
overlap, failed push, unexpected parent movement, revision mismatch, or missing
artefacts, do not overwrite work; reconcile the integrity failure or block the
affected chain. Recorded wave parent movement defers restack, not reviews.
Continue independent branches. Require a human decision only at the
authority boundary defined by the calling skill.

Report the plan, branch and pinned parent, changed files, candidate and final
SHAs, upstream SHA, verification, review passes, ledger, artefact paths, and
one of a blocker, `Review cap reached`, `Reviewed provisionally`, or
`Reviewed and pushed`.
