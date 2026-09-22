---
name: build-branch-stack
description: Build approved vertical-slice plans as proportionate, verified, reviewed remote branches and maintain the canonical release manifest before integration.
disable-model-invocation: true
metadata:
  layer: runner
---

# Build Branch Stack

Build and push release branches from reviewed vertical-slice plans. Parent
feature specifications are context, not executable branch inputs. Record each
stable branch in the canonical release manifest. Use `open-stack-requests` in
draft mode as branches stabilize when the task authorizes change-request (CR)
publication; do not wait for release assembly.

## Resources

Resolve `orchestration_skill_root` to this directory. Read
`references/orchestration-runtime.md` and
`references/orchestration-plans-layout.md` first. For each plan, use
`references/git-branch-commit.md` for branch and commit operations,
`references/git-sync-branch.md` for verified pushes, then
`references/from-reviewed-plan-to-git-handoff.md`. Read other references when
their step requires them. Read `references/artefact-audit.md` after a feature
reaches `review/`; revisit only its pending cross-branch questions after a tested
stack snapshot exists. Read `references/release-manifest.md` before creating or
changing the manifest.

## Inputs

- Ordered reviewed vertical-slice plans at
  `plans/<stage>/<slug>/<slug>.md`, each linked to its approved parent
  specification and slice map, or selected legacy plans explicitly classified
  as cohesive slices.
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
the graph, conflict surface, or acceptance cost is unusually high, return the
work for a smaller split with concrete evidence. The user controls release
scope; this runner controls whether one branch is a safe implementation unit.

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
preserved artefacts, passed required branch-level agent checks, and recorded
human, external, and not-yet-runnable release-candidate checks. Final stack
checks gate release progression, not this feature status.
Pending external acceptance or not-yet-runnable release-candidate checks do not
make the branch `Blocked`. Number review passes. Never describe a current or
future pass as “final,” “last,” “closing,” or “concluding.” A pass can only be
identified retrospectively as the last completed pass after every completion
condition is satisfied. Before then, call it “pass N,” “the current pass,” or
“the next fresh pass.”

## Readiness

Before moving plans or editing code, inspect repository instructions, selected
plans, parent specifications, slice maps, branch refs, and available CI. Reject
a parent specification as an implementation input. Require each parent
specification and slice map to have status `approved`; stop on a `draft`,
`fulfilled`, `superseded`, or `stale` input. Resolve each plan by its mapped
slice slug rather than a stage-dependent path. For each selected plan, answer
before creating or adopting a branch:

- What single actor-visible or integration-visible outcome does it deliver?
- Can any acceptance group ship, fail, or roll back independently?
- Does it combine providers, SDKs, lifecycle owners, or external acceptance
  environments?
- Would a cross-cutting coordinator exist only because unrelated outcomes were
  grouped?
- Does every owned acceptance ID map to this slice, with sibling outcomes
  explicitly excluded?

Stop and return the plan for decomposition when it fails this cohesion gate.
An explicitly classified legacy plan must meet the same standard.

Identify required verification for each touched surface, its prerequisites
(such as locked dependencies, services,
fixtures, or disabled components), and whether CI runs on the target branches.
Detect and select every applicable capability skill for specialized changed surfaces.
Require each selected capability to define fast authoring checks, exact
candidate verification, final integration verification, and the immutable
input identities and equivalence rules that permit safe reuse. A reusable check
must account for every determining input, including source, configuration,
locked dependencies and fixtures, toolchain, runtime binding, and effective
result; otherwise rerun it. The capability must also identify the source
representation and the effective generated or runtime result reviewers need.
Record those commands and evidence here without copying ecosystem-specific
procedures into this orchestration skill.
Prepare reproducible local checks for requirements CI cannot run. If a required
agent-run gate or prerequisite is missing, resolve its scope and ownership before
implementation; do not silently add unrelated CI or tooling work. Distinguish
checks the agent can run from human or external acceptance (such as a sandbox
wallet test). Record intended commands, any agreed gate gap, and each external
check's procedure, owner, and pending result in plan evidence. Runtime lifecycle
logic requires executable local behavioural proof at the highest practical
seam; source-shape assertions may supplement but not replace it.

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
3. Follow `from-reviewed-plan-to-git-handoff.md`. Before editing, require the
   implementation worker to create the design checkpoint specified by
   `plan-implement.md`; stop if it exposes a cohesion failure or unauthorized
   architecture. Run the applicable capability's authoring checks during
   implementation and its exact candidate verification before accepting the
   candidate. Do not substitute capability final-integration verification for
   per-plan candidate verification. Then selectively stage and review
   any new edits, commit if needed, and verify the exact commit in a clean
   worktree through fresh execution, deterministic evidence reuse, or both, as
   defined in `verification-runner.md`.
   Create or update the remote branch at the first verified commit. Push each
   verified fix and review the pinned parent-to-commit diff. Keep the feature in
   `in_progress/` through all code review passes and fixes. Update the branch's
   manifest entry after every verified tip change.
4. Once Claude, Codex, and Cursor have cleanly reviewed the logical change and
   its required branch-level agent checks pass, preserve the feature's
   `.reviews/`, `.evidence/`, and any `.execution/` folders before removing a
   worktree. Record pending human and external checks with procedures and owners.
   Record release-candidate checks that intrinsically require unbuilt descendant
   branches or a complete candidate with their prerequisites. Verify that the
   exact tip matches local, upstream, and remote refs, move the whole feature to
   `review/`, refresh its manifest and artefact paths, and validate the manifest.
   A missing prerequisite for a required branch-level check remains a blocker;
   do not classify it as a deferred release check. If the move or manifest write
   fails, return any just-moved feature to `in_progress/` and report the blocker.
   If the current task authorizes CR creation, hand the branch to
   `open-stack-requests` in draft mode; otherwise record publication as the next
   action. This skill does not open the CR itself. Use this branch as a parent
   only where dependency evidence requires it.

Before each plan and final handoff, compare every local parent with its pinned
SHA and refetch any parent already on `origin`. If a parent moved, move only
affected descendants to `in_progress/` before restacking; keep each candidate
there through verification and code review. Synchronize reviewed tips with
explicit leases.
Classify each delta as `verbatim`, `mechanical regeneration`, or
`intentional behavior change`. Verify every new tip with the smallest sufficient
combination of fresh checks and deterministic evidence reuse. Verification
proves that every required check applies to the current tip; it does not require
rerunning an unchanged check. A new SHA or reviewer pass alone is not grounds
to rerun one. Do not rerun an expensive deterministic check when the capability's
equivalence rules prove unchanged determining inputs and effective result.
A conflict-free restack
with equal `range-diff` and deterministic identity evidence retains all three
prior reviews; record their old-to-new SHA mappings. A fresh three-reviewer pass
is required for manual resolutions, unequal range diffs, changed generated
output, or behavior changes. An unexpected local branch change needs a scope
decision before it can count as reviewed.

After all plans:

1. When every branch in the selected release candidate exists, run deterministic
   pre-handoff checks on every chain head and independent branch. For an ordered
   independent batch, build an unpushed temporary integration commit from the
   pinned base in merge order and test it. Check the applicable capabilities'
   final integration verification against each exact chain head or temporary
   integration commit. Check
   that CI required by the plan, user, or repository policy runs on the target
   branches and covers applicable behavior tests and risk-based lint, type,
   dependency, secret, and static checks. Run required agent-run checks locally
   where CI is optional or cannot cover them. If later planned branches do not
   yet exist, record these release-candidate checks as pending with their exact
   prerequisites; checks on the current partial stack are not conclusive evidence
   for the eventual candidate. Pending release-candidate checks do not move a
   completed feature out of `review/`, but they block freeze, ready CRs, staging,
   and merge. If a required final stack check is absent or cannot run for a
   complete candidate, block release progression. If it fails, return the
   affected feature and demonstrated descendants to `in_progress/` for a fix,
   fresh verification, and code review. Record human or external acceptance as
   pending with its procedure and owner when it cannot yet be performed.
2. For a complete candidate, when
   `scripts/codex/protected_full_pipeline.py` exists, run it with the committed
   lock-selected seed and baseline. If the candidate is incomplete, record this
   check and its required branches as pending instead of running it on a partial
   stack:

   ```bash
   python -m scripts.codex.protected_full_pipeline \
     --data-root <absolute-protected-data-root> \
     --commit "<verified-chain-head-or-temporary-integration-sha>" \
     --output-dir <verification-artifact-directory>
   ```

Keep bulk output outside artefact folders and index concise evidence under
the last plan. Never publish or refresh protected seed or baseline data here.
Treat a lock mismatch or unexpected output as a blocker.

Leave completed features in `review/` while release-candidate or human and
external checks are pending. If any later check reveals a defect, return the
affected feature and demonstrated descendants to `in_progress/` for a fix,
fresh verification, and code review. Refresh the canonical manifest at its
stable release path and check every recorded plan and artefact path. Freeze only
when the user selects a complete candidate, final stack checks pass, and all
included branch tips, all three clean reviews or mappings, and required agent
checks agree. Record the freeze authorization and scope digest, then validate
the manifest. Do not add scope after freeze. A critical addition requires an
authorized thaw, a new digest, and invalidation of affected integration,
pipeline, and acceptance evidence; noncritical additions go to a later release
unless the user changes the frozen scope.

Audit the selected features' preserved artefacts using
`references/artefact-audit.md`. Verify candidate follow-ups against the tested
stack state, or against the exact verified feature tip when no complete tested
snapshot exists. Record planning decisions in each feature's
`<slug>.reviews/artefact-audit-ledger.md`, and route distinct work still worth
doing through the specification and vertical-slice workflow. On repair runs,
reconcile prior decisions and planning artefacts for affected features. Write
these local planning files in the user's primary
checkout without changing verified branch tips. Report an incomplete audit
separately from branch readiness.

## Rules

- Make the least-complex change that satisfies each plan and binding contract.
- Require behavioural regression tests proportionate to the changed lifecycle;
  structural assertions alone are insufficient evidence of runtime behaviour.
- Map changed surfaces to plan scope or a binding contract. Stop for user
  approval before adding an unplanned deliverable.
- Stop and return to architecture or slice planning when implementation would
  introduce an unapproved page-global mutable coordinator, cross-provider
  lifecycle manager, retry or recovery framework, substantial replacement of
  a dependency-owned surface, one permanent dependency modification spanning
  independently testable defects, or local ownership of unsupported upstream
  behaviour. Do the same when the production footprint materially exceeds the
  design checkpoint. Line counts are signals, not fixed limits.
- Escalate a permanent dependency modification when no supported extension
  point exists or the project would assume ongoing ownership of upstream
  behaviour.
- Require the first discovery review to assess correctness and proportionality
  separately, including alignment with the platform's native owner. Resolve a
  proportionality failure by simplifying, splitting, upgrading, or choosing a
  different extension mechanism.
- Before accepting a finding, ask whether removing or simplifying new machinery
  closes it. A finding does not authorize a new responsibility merely because
  a broad acceptance condition can be cited.
- If two successive discovery passes expose new failure modes caused by the
  branch's coordinator, state machine, retry system, or lifecycle interception,
  stop local fixes and return to architecture review.
- Preserve unrelated dirty work; never broadly stage, clean, or revert it.
- Review immutable commits, not the index. The index is a candidate-tree gate.
- Run fresh Claude, Codex, and Cursor reviewers in parallel for every discovery
  pass. All three must complete successfully.
- Do not amend a published commit. Preserve clean review evidence across only
  conflict-free, equal-range-diff restacks with deterministic identity checks.
- Stop for failed verification, unresolved findings, unsafe commits, revision
  mismatch, or unpreserved artefacts. A failed branch-level check blocks the
  feature; a failed final stack check blocks release progression and returns the
  affected feature and demonstrated descendants to `in_progress/`. When the
  full-pipeline export test exists, do not skip it for a complete candidate
  unless the user cancels it.
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
`Verified and pushed, ready for human review` for every feature that meets the
branch-level criteria, even when release-candidate checks are legitimately
pending. Separately report whether release progression is ready or blocked,
including each pending check and prerequisite. Also report each feature's audit
ledger path and decisions, any specifications, slice maps, or backlog plans
created or reused, and incomplete audit work. State whether each draft CR was
created by the publication skill or remains a next action. This skill creates
no CR.
