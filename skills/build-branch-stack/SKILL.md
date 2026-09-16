---
name: build-branch-stack
description: Implement reviewed plans as verified, code-reviewed branches synchronized with origin. Stop before opening change requests.
disable-model-invocation: true
metadata:
  layer: runner
---

# Build Branch Stack

Build and push a branch stack from reviewed plans. Use `open-stack-requests`
later when the user wants change requests (CRs).

## Resources

Resolve `orchestration_skill_root` to this directory. Read
`references/orchestration-runtime.md` and
`references/orchestration-plans-layout.md` first. For each plan, use
`references/git-branch-commit.md` for branch and commit operations,
`references/git-sync-branch.md` for verified pushes, then
`references/from-reviewed-plan-to-git-handoff.md`. Read other references when
their step requires them.

## Inputs

- Ordered reviewed feature plans at `plans/<stage>/<slug>/<slug>.md`, or
  selected legacy `plans/<slug>.md` files to migrate.
- Base branch: the remote default unless the user names another.
- Starting branch: the base unless the user names an existing parent.
- Dependency map: each plan's one required unmerged predecessor, or `none`.
- For a repair run, the existing stack manifest, affected branches, and the
  publisher's evidence that any affected ready CRs are draft.

Input order alone does not establish a dependency. Branch independent plans
from the base. If a plan needs multiple unmerged predecessors, stop for a
different split or a merged prerequisite; do not invent a linear parent.

## Progress

Keep one compact table and update it on state, review, commit, restack, or
verification changes:

```text
| Plan | Status | Reviews | Branch | Commit | Next action |
```

Use `Queued`, `In progress`, `Blocked`, or `Complete`. `Complete` requires the
feature in `done/`, a clean-reviewed, verified final SHA matching local,
upstream, and remote tips, a pinned parent, preserved artefacts, and passed
final stack checks. Number review passes; never predict a final pass.

## Workflow

For a fresh run, move only the selected reviewed feature directories from
`backlog/` to `to_do/`. Accept selected features already in `to_do/`. Resolve
their new plan paths before starting; leave unrelated backlog features alone.
For a selected legacy `plans/<slug>.md`, move it and any sibling
`<slug>.reviews/`, `<slug>.execution/`, and `<slug>.evidence/` into
`plans/to_do/<slug>/` first. Stop on a destination collision.

For each plan:

1. Record why it depends on its parent. Fetch and pin the parent branch and SHA.
2. Create its local plan branch from that parent, then move its feature from
   `to_do/` to `in_progress/` before implementation. On a repair run, verify
   the existing branch and manifest instead of recreating it; move only
   affected features and descendants back to `in_progress/` when needed.
3. Follow `from-reviewed-plan-to-git-handoff.md`: selectively stage and review
   the candidate tree, commit, and verify the exact commit in a clean worktree.
   Create the remote branch at the first verified commit. Push each verified
   fix, move the feature to `review/` before code review, and review the
   pinned parent-to-commit diff. After a pass requiring a fix, move it back to
   `in_progress/`; repeat until clean. Do not open a CR.
4. Preserve the feature's `.reviews/`, `.evidence/`, and any `.execution/`
   folders before removing a worktree. Use this branch as a parent only where
   dependency evidence requires it.

Before each plan and final handoff, compare every local parent with its pinned
SHA and refetch any parent already on `origin`. If a parent moved, move only
affected descendants to `in_progress/` before restacking; return each verified
candidate to `review/`. Synchronize reviewed tips with explicit leases.
Classify each delta as `verbatim`, `mechanical regeneration`, or
`intentional behavior change`. Verify the first two deterministically, and
verify and review any changed commit. An unexpected local branch change needs
a scope decision before it can count as reviewed.

After all plans:

1. Run deterministic pre-handoff checks on every chain head and independent
   branch. For an ordered independent batch, build an unpushed temporary
   integration commit from the pinned base in merge order and test it. Check
   that applicable CI covers behavior tests and risk-based lint, type,
   dependency, secret, and static-security checks; stop if a required class
   is absent or cannot run.
2. When `scripts/codex/protected_full_pipeline.py` exists, run it with the
   committed lock-selected seed and baseline:

   ```bash
   python -m scripts.codex.protected_full_pipeline \
     --data-root <absolute-protected-data-root> \
     --commit "<verified-chain-head-or-temporary-integration-sha>" \
     --output-dir <verification-artifact-directory>
   ```

Keep bulk output outside artefact folders and index concise evidence under
the last plan. Never publish or refresh protected seed or baseline data here.
Treat a lock mismatch or unexpected output as a blocker.

After all final checks pass, move selected features still in `review/` to
`done/`; leave unaffected features already in `done/` there. Write the stack
manifest at the last plan's final evidence path and check every recorded plan
and artefact path. If a move or manifest write fails, return any just-moved
features to `review/` and report the blocker.

## Rules

- Make the least-complex change that satisfies each plan and binding contract.
- Require proportionate regression tests for changed behavior.
- Map changed surfaces to plan scope or a binding contract. Stop for user
  approval before adding an unplanned deliverable.
- Preserve unrelated dirty work; never broadly stage, clean, or revert it.
- Review immutable commits, not the index. The index is a candidate-tree gate.
- Run fresh `claude`, `codex`, and `cursor` reviewers in parallel for every
  pass. All three must complete successfully.
- Do not amend a reviewed commit without invalidating its review. Use
  deterministic scope, identity, hash, ancestry, and restack checks.
- Stop for failed verification, unresolved findings, unsafe commits, revision
  mismatch, or unpreserved artefacts. When the full-pipeline export test
  exists, do not skip it unless the user cancels it.

## Handoff

Save a stack manifest under the last plan's `.evidence/` folder in `done/`.
Record the base branch and pinned SHA. For each branch, record its plan,
dependency evidence, current feature and artefact paths, parent branch and
pinned SHA, local, upstream, and remote tip and tree SHAs, verification
commands and result, and clean review SHA and passes. Record final integration
and protected-pipeline commands, tested SHAs, and results. Report
`Verified and pushed` or the blocker. This skill creates no CR.
