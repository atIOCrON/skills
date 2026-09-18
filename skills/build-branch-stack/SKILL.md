---
name: build-branch-stack
description: Build verified, reviewed remote branches and maintain the canonical release manifest before integration.
disable-model-invocation: true
metadata:
  layer: runner
---

# Build Branch Stack

Build and push release branches from reviewed plans. Record each stable branch
in the canonical release manifest. Use `open-stack-requests` in draft mode as
branches stabilize when the task authorizes change-request (CR) publication;
do not wait for release assembly.

## Resources

Resolve `orchestration_skill_root` to this directory. Read
`references/orchestration-runtime.md` and
`references/orchestration-plans-layout.md` first. For each plan, use
`references/git-branch-commit.md` for branch and commit operations,
`references/git-sync-branch.md` for verified pushes, then
`references/from-reviewed-plan-to-git-handoff.md`. Read other references when
their step requires them. Read `references/artefact-audit.md` after final stack
checks. Read `references/release-manifest.md` before creating or changing the
manifest.

## Inputs

- Ordered reviewed feature plans at `plans/<stage>/<slug>/<slug>.md`, or
  selected legacy `plans/<slug>.md` files to migrate.
- Base branch: the remote default unless the user names another.
- Starting branch: the base unless the user names an existing parent.
- Plan branch: create one by default, or use a user-selected existing branch
  after validating its parent, existing commits, and remote state.
- Dependency map: each plan's one required unmerged predecessor, or `none`.
- Release ID and canonical manifest path. For a fresh run, create
  `plans/releases/<release-id>/manifest.json`; for a repair, require the
  existing manifest.
- For a repair run, the canonical release manifest, affected branches, and the
  publisher's evidence that any affected ready CRs are draft.

Input order alone does not establish a dependency. Branch independent plans
from the base. If a plan needs multiple unmerged predecessors, stop for a
different split or a merged prerequisite; do not invent a linear parent.
Release scope follows what must ship. Never impose a branch-count cap. When
the graph, conflict surface, or acceptance cost is unusually high, recommend a
smaller split with concrete evidence, but let the user decide release scope.

## Progress

Keep one compact table and update it on state, review, commit, restack, or
verification changes:

```text
| Plan | Status | Reviews | Branch | Commit | Next action |
```

Use `Queued`, `In progress`, `Blocked`, or `Ready for human review`. The last
status requires the feature in `review/`, a verified final SHA matching local,
upstream, and remote tips, a pinned parent, clean reviews from all three
providers on that SHA or recorded equal-range-diff mappings for all three,
preserved artefacts, passed agent-run implementation and final stack checks,
and recorded human or external checks.
Pending external acceptance does not make the branch `Blocked`. Number review
passes; never predict a final pass.

## Readiness

Before moving plans or editing code, inspect repository instructions, selected
plans, branch refs, and available CI. Identify required verification for each
touched surface, its prerequisites (such as locked dependencies, services,
fixtures, or disabled components), and whether CI runs on the target branches.
Prepare reproducible local checks for requirements CI cannot run. If a required
agent-run gate or prerequisite is missing, resolve its scope and ownership before
implementation; do not silently add unrelated CI or tooling work. Distinguish
checks the agent can run from human or external acceptance (such as a sandbox
wallet test). Record intended commands, any agreed gate gap, and each external
check's procedure, owner, and pending result in plan evidence.

## Workflow

For a fresh run, initialize the canonical JSON manifest from the pinned base,
selected plans, explicit exclusions, demonstrated dependencies, declared
surfaces, and planned checks. Validate it with
`scripts/validate_release_manifest.py`. Do not copy branch state from a Sheet;
reconcile any Sheet or prose tracker from the manifest.

Move only the selected reviewed feature directories from
`backlog/` to `to_do/`. Accept selected features already in `to_do/`. Resolve
their new plan paths before starting; leave unrelated backlog features alone.
For a selected legacy `plans/<slug>.md`, move it and any sibling
`<slug>.reviews/`, `<slug>.execution/`, and `<slug>.evidence/` into
`plans/to_do/<slug>/` first. Stop on a destination collision.

For each plan:

1. Record why it depends on its parent. Fetch and pin the parent branch and SHA.
2. Create its local plan branch from that parent, or validate the selected
   existing plan branch with `git-branch-commit.md`, then move its feature from
   `to_do/` to `in_progress/` before implementation. On a repair run, verify
   the existing branch and manifest instead of recreating it; move only
   affected features and descendants back to `in_progress/` when needed.
3. Follow `from-reviewed-plan-to-git-handoff.md`: selectively stage and review
   any new edits, commit if needed, and verify the exact commit in a clean worktree.
   Create or update the remote branch at the first verified commit. Push each
   verified fix and review the pinned parent-to-commit diff. Keep the feature in
   `in_progress/` through all code review passes and fixes. Update the branch's
   manifest entry after every verified tip change. Once Claude, Codex, and
   Cursor have cleanly reviewed the logical change and its required agent
   checks pass, validate the manifest. If the current task authorizes CR
   creation, hand the branch to `open-stack-requests` in draft mode; otherwise
   record that publication as the next action. This skill does not open the CR
   itself.
4. Preserve the feature's `.reviews/`, `.evidence/`, and any `.execution/`
   folders before removing a worktree. Use this branch as a parent only where
   dependency evidence requires it.

Before each plan and final handoff, compare every local parent with its pinned
SHA and refetch any parent already on `origin`. If a parent moved, move only
affected descendants to `in_progress/` before restacking; keep each candidate
there through verification and code review. Synchronize reviewed tips with
explicit leases.
Classify each delta as `verbatim`, `mechanical regeneration`, or
`intentional behavior change`. Verify every new tip. A conflict-free restack
with equal `range-diff` and deterministic patch evidence retains all three
prior reviews; record their old-to-new SHA mappings. A fresh three-reviewer pass
is required for manual resolutions, unequal range diffs, changed generated
output, or behavior changes. An unexpected local branch change needs a scope
decision before it can count as reviewed.

After all plans:

1. Run deterministic pre-handoff checks on every chain head and independent
   branch. For an ordered independent batch, build an unpushed temporary
   integration commit from the pinned base in merge order and test it. Check
   that CI required by the plan, user, or repository policy runs on the target
   branches and covers applicable behavior tests and risk-based lint, type,
   dependency, secret, and static checks. Run required agent-run checks locally
   where CI is optional or cannot cover them. Stop if a required agent-run check
   is absent, cannot run, or fails; record human or external acceptance as
   pending with its procedure and owner when it cannot yet be performed.
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

After all agent-run implementation and final stack checks pass, code review
findings are resolved, and remaining human or external acceptance checks are
recorded, move selected features still in `in_progress/` to `review/`; leave
unaffected features already in `review/` or `done/` there. Pending external
acceptance alone does not delay this move or the subsequent artefact audit.
If acceptance later reveals a defect, return the affected feature and
descendants to `in_progress/` for a fix, fresh verification, and code review.
Refresh the canonical manifest at its stable release path and check every
recorded plan and artefact path. Freeze only when the user selects the candidate
and all included branch tips, all three clean reviews or mappings, and required
agent checks agree. Record the freeze authorization and scope digest, then
validate the manifest. Do not add scope after freeze. A critical addition requires an
authorized thaw, a new digest, and invalidation of affected integration,
pipeline, and acceptance evidence; noncritical additions go to a later release
unless the user changes the frozen scope. If a move or manifest write fails,
return any just-moved features to `in_progress/` and report the blocker.

Audit the selected features' preserved artefacts using
`references/artefact-audit.md`. Verify candidate follow-ups against the tested
stack state, record planning decisions in each feature's
`<slug>.reviews/artefact-audit-ledger.md`, and create backlog plans for distinct
work still worth doing. On repair runs, reconcile prior decisions and plans
for affected features. Write these local planning files in the user's primary
checkout without changing verified branch tips. Report an incomplete audit
separately from branch readiness.

## Rules

- Make the least-complex change that satisfies each plan and binding contract.
- Require proportionate regression tests for changed behavior.
- Map changed surfaces to plan scope or a binding contract. Stop for user
  approval before adding an unplanned deliverable.
- Preserve unrelated dirty work; never broadly stage, clean, or revert it.
- Review immutable commits, not the index. The index is a candidate-tree gate.
- Run fresh Claude, Codex, and Cursor reviewers in parallel for every discovery
  pass. All three must complete successfully.
- Do not amend a published commit. Preserve clean review evidence across only
  conflict-free, equal-range-diff restacks with deterministic identity checks.
- Stop for failed verification, unresolved findings, unsafe commits, revision
  mismatch, or unpreserved artefacts. When the full-pipeline export test
  exists, do not skip it unless the user cancels it.
- Do not mark a feature `done/` while external acceptance is pending or a
  failure remains unresolved. Record passed checks or an authorized decision
  explicitly accepting each limitation before `done/`; retain the confirmed
  merge requirement in `references/orchestration-plans-layout.md`.
- Pending external acceptance also blocks a production decision unless an
  authorized decision explicitly accepts the limitation.

## Handoff

Save and validate the canonical manifest at
`plans/releases/<release-id>/manifest.json` or the repository-defined stable
path. It records the base, ordered branches, dependencies, targets, tips,
surfaces, checks, all three review mappings, CRs, exclusions, freeze, integration,
acceptance, and deployment state; link detailed evidence instead of duplicating
it. Report
`Verified and pushed, ready for human review` or the blocker, plus each
feature's audit ledger path, decisions, backlog plans created or reused, and
any audit work still pending. State whether each draft CR was created by the
publication skill or remains a next action. This skill creates no CR.
