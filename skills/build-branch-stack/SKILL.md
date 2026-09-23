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
from the base. If a plan needs multiple unmerged predecessors, split the
implementation within the selected scope or use a merged prerequisite; do not
invent a linear parent.
Release scope follows what must ship. Never impose a branch-count cap. When
the graph, conflict surface, or acceptance cost is unusually high, make a
smaller implementation split with concrete evidence. The user controls release
scope; this runner controls whether one branch is a safe implementation unit.

## Progress

Keep one compact table and update it on state, review, commit, restack, or
verification changes:

```text
| Plan | Status | Reviews | Branch | Commit | Next action |
```

Use `Queued`, `In progress`, `Review cap reached`, `Blocked`, or `Ready for
human review`. `Review cap reached` is a per-plan terminal state for this build
run, not a blocker for the whole queue: keep the feature in `in_progress/`, do
not parent from or publish it, leave dependent descendants queued, and continue
the next eligible independent plan. `Ready for human review` requires the
feature in `review/`, a verified final SHA matching local,
upstream, and remote tips, a pinned parent, clean reviews from all three
providers on that SHA or valid equal-range-diff or test-only-closure mappings,
preserved artefacts, passed required branch-level agent checks, and recorded
human, external, and not-yet-runnable release-candidate checks. Final stack
checks gate release progression, not this feature status.
Pending external acceptance or not-yet-runnable release-candidate checks do not
make the branch `Blocked`. Number review passes. Never describe a current or
future pass as “final,” “last,” “closing,” or “concluding.” A pass can only be
identified retrospectively as the last completed pass after every completion
condition is satisfied. Before then, call it “pass N,” “the current pass,” or
“the next fresh pass.”

## Autonomous Decision Authority

An authorized build task permits repository-local implementation,
verification, architecture, narrow dependency-correction, plan-amendment, and
implementation-slice decisions needed to complete the selected approved
release scope without further approval. A decision is within this authority
when it:

- serves an existing acceptance condition or demonstrated prerequisite;
- preserves approved outcomes, exclusions, binding contracts, and release
  membership;
- keeps coherent implementation and rollback boundaries;
- adds no independently releasable product capability;
- uses the narrowest viable native owner or supported extension; and
- neither waives required evidence nor requires production, destructive,
  credential, financial, legal, or external-communication authority.

Treat each plan as a controlled implementation hypothesis. When runtime or
review evidence disproves its mechanism, preserve the evidence; return affected
features to `in_progress/`; amend the plan, design checkpoint, verification
boundary, dependency graph, and manifest as needed; then continue. Record the
failure class, alternatives, decision, added production surface, rollback
effect, and required evidence before editing.

The runner may create a prerequisite implementation slice when it decomposes
the same approved acceptance outcome without changing release scope,
acceptance ownership, or exclusions. Update the slice map, dependency graph,
and manifest. A new independently releasable outcome remains a product-scope
decision.

Require a human decision only to change product or release scope, acceptance
conditions or exclusions, a binding contract or policy, a required evidence
gate, frozen scope, or broad upstream ownership, or to perform an action outside
the authority above. Invocation does not supply missing credentials or external
authority.

An integrity failure such as unexplained branch movement, staged/unstaged
overlap, a failed lease, or missing artefacts never authorizes overwriting work.
Diagnose and reconcile it. If that is impossible, block the affected chain and
continue independent slices.

## Review Convergence

An architecture epoch is a sequence of fixes under one design. Record its
number, mechanism, and state owner in the design checkpoint. Start a new epoch
when the mechanism, native owner, state model, dependency strategy, or slice
boundary materially changes; record the prior epoch's failure class and why the
new design removes it.

Within an epoch, group findings by invariant or ownership failure and fix one
root cause instead of adding one guard per example. Do not rerun unchanged
expensive checks or enlarge tests beyond candidate-owned behaviour.

Accept a runtime review finding only when it is reproduced on the pinned SHA
through an existing supported production-like flow or deductively proven from
committed code and a binding contract. Give each accepted finding a failure
family defined by its invariant, runtime owner, supported path, and observable
failure. Match that family across all passes, files, designs, and epochs. Static
plausibility is advisory and cannot trigger code, tests, ledger entries,
closure, or another pass.

Before adopting a broader design, record the demonstrated failure, whether
deletion or simplification resolves it, the existing native owner, whether the
work is one invariant or several outcomes, whether tests exceed production
machinery, and any dependency patch's removal condition. Reject a design when
fewer state owners, async boundaries, patches, or extensions satisfy the same
approved outcome.

Two discovery passes anywhere in the ledger that expose new failures from the
same family, design, or verification model require an autonomous architecture
reassessment before more edits. Changing implementation shape or epoch does
not reset this count. Compare removal, simplification, replacement, upgrade,
the native owner, a narrow dependency correction, and a prerequisite split by
production surface, state ownership, rollback, verification cost, and
maintenance. Select the smallest
viable design, amend the recorded architecture, and continue with a fresh
candidate.

If two epochs fail for the same underlying reason, do not try a third variation
of that mechanism. Remove it, use the native owner, upgrade or narrowly correct
the owning dependency, split a prerequisite, or use an already-supported
contract that still satisfies the approved outcome. Mark the affected chain
blocked only when every viable repository-local option conflicts with a hard
constraint or the approved outcome.

After two accepted fix cycles in one failure family, prohibit another local
variation and record an autonomous continuation decision. Continue only for a
confirmed defect with a viable, non-repeated disposition. Require a human only
when every viable option crosses the authority boundary above.

Run at most five completed fresh three-reviewer discovery passes for one plan.
A pass counts when all three validated outputs have been triaged. Targeted
closure, same-session output repair, transport retry, deterministic review
mapping, and an incomplete reviewer launch do not count. The count persists
across task resumptions, implementation shapes, and architecture epochs. After
pass 5, finish its accepted in-scope remediation through normal commit,
verification, push, and targeted-closure rules. If the resulting tip does not
meet review completion without another discovery pass, do not start pass 6:
record `review_cap_reached` in the ledger and release manifest, keep the feature
in `in_progress/`, and continue the next eligible independent plan. This cap
does not waive a finding, review, verification, or readiness gate.

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

When a plan fails this cohesion gate, decompose its implementation within the
approved outcome and release scope. Stop only when decomposition would change
product scope, acceptance ownership, or exclusions. An explicitly classified
legacy plan must meet the same standard.

Before implementation, classify each owned acceptance group by its
candidate-owned mechanism; whether the candidate introduces or modifies its
lifecycle implementation or only changes routing, selection, configuration, or
reachability; its runtime owner; and its branch-local, inherited, and external
evidence. A candidate can change the observable product outcome without
changing the dependency-owned lifecycle implementation.

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
Copy any review-required source or effective result from outside the reviewer
repository workspace into the neutral review pack; a path, hash, or replay log
alone is insufficient.
Record those commands and evidence here without copying ecosystem-specific
procedures into this orchestration skill.
Prepare reproducible local checks for requirements CI cannot run. If a required
agent-run gate or prerequisite is missing, resolve its scope and ownership before
implementation; do not silently add unrelated CI or tooling work. Distinguish
checks the agent can run from human or external acceptance (such as a sandbox
wallet test). Record intended commands, any agreed gate gap, and each external
check's procedure, owner, and pending result in plan evidence. Runtime lifecycle
logic introduced or modified by the candidate requires executable local
behavioural proof at the highest practical seam; source-shape assertions may
supplement but not replace proof of that owned runtime behaviour. Merely making
an unchanged dependency-owned lifecycle reachable does not require
reconstructing it locally when exact effective-code identity, applicable
inherited test evidence, and explicit external acceptance establish the
contract. Lightweight test doubles may prove candidate-owned routing or
binding, but transitions implemented by a fake provider, server, persistence
layer, account store, or order lifecycle are not evidence of production
behaviour owned elsewhere.

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
   `plan-implement.md`; resolve any cohesion failure or architecture change
   through the authority and convergence rules above. Compare the proposed
   verification machinery with the candidate-owned production mechanism. If
   verification would introduce a provider simulator, server model,
   persistence fixture, retry framework, or more lifecycle machinery than the
   production change, simplify it or return
   the verification footprint for correction before editing. Approval of a
   plan does not authorize disproportionate verification machinery; preserve
   the acceptance outcome while amending a test seam that would simulate
   unchanged external or dependency-owned behaviour. Run the applicable
   capability's authoring checks during
   implementation and its exact candidate verification before accepting the
   candidate. Do not substitute capability final-integration verification for
   per-plan candidate verification. Then selectively stage and review
   any new edits, commit if needed, and verify the exact commit in a clean
   worktree through fresh execution, deterministic evidence reuse, or both, as
   defined in `verification-runner.md`.
   Create or update the remote branch at the first verified commit. Push each
   verified fix and review the pinned parent-to-commit diff. Keep the feature in
   `in_progress/` through all code review passes and fixes. Update the branch's
   manifest entry after every verified tip change and update
   `review_progress.completed_passes` after every completed discovery pass.
   If the code-review loop reaches its five-pass cap, commit all accepted
   in-scope work, verify and push the resulting candidate when verification
   passes, preserve its artefacts, record the cap state, and end work on that
   plan for this run. Set `review_progress.status` to `review_cap_reached` and
   link its ledger evidence. Do not move it to `review/`, open a CR, or use it
   as a dependency parent. Leave its descendants queued and continue other
   eligible plans.
4. Once Claude, Codex, and Cursor have cleanly reviewed the logical change and
   its required branch-level agent checks pass, preserve the feature's
   `.reviews/`, `.evidence/`, and any `.execution/` folders before removing a
   worktree. Record pending human and external checks with procedures and owners.
   Record release-candidate checks that intrinsically require unbuilt descendant
   branches or a complete candidate with their prerequisites. Verify that the
   exact tip matches local, upstream, and remote refs, move the whole feature to
   `review/`, set `review_progress.status` to `clean`, refresh its manifest and
   artefact paths, and validate the manifest.
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
When an otherwise-clean discovery pass has one accepted finding resolved only
by an eligible test-only remediation, follow `code-review-loop.md`: verify the
new SHA, obtain same-session closure from each originating reviewer, and record
`test_only_closure` mappings instead of running another discovery pass.

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
- Require behavioural regression tests proportionate to lifecycle
  implementation introduced or modified by the candidate. Do not infer local
  lifecycle ownership merely because the candidate exposes existing behaviour;
  structural assertions alone remain insufficient evidence of runtime
  behaviour the candidate owns.
- Keep verification machinery proportionate to the candidate-owned production
  mechanism. A test harness's own state transitions do not prove production
  behaviour.
- Map every changed surface to an acceptance condition, a demonstrated
  prerequisite, or a binding contract. Record an in-scope plan amendment before
  committing it. Split a distinct rollback boundary; do not add unrelated work.
- Reassess the architecture before introducing a page-global mutable
  coordinator, cross-provider lifecycle manager, retry or recovery framework,
  substantial dependency-surface replacement, unsupported upstream ownership,
  or a production footprint beyond the design checkpoint. Continue only with
  the smallest design allowed by Autonomous Decision Authority. Line counts are
  signals, not limits.
- Modify a dependency permanently only for a reproduced locked-version defect
  that no supported extension can satisfy. Record the defect, rejected
  extensions, smallest correction, removal condition, source and effective
  identities, behavioural evidence, replay order, and maintenance effect. Keep
  one coherent defect per patch and follow the applicable capability skill.
- Require the first discovery review to assess correctness and proportionality
  separately, including alignment with the platform's native owner. Resolve a
  proportionality failure by simplifying, splitting, upgrading, or choosing a
  different extension mechanism.
- Before accepting a finding, ask whether removing or simplifying new machinery
  closes it. A finding does not authorize a new responsibility merely because
  a broad acceptance condition can be cited.
- Apply Review Convergence when successive passes expose failures from the same
  candidate-owned architecture or verification model.
- Preserve unrelated dirty work; never broadly stage, clean, or revert it.
- Review immutable commits, not the index. The index is a candidate-tree gate.
- Run fresh Claude, Codex, and Cursor reviewers in parallel for every discovery
  pass. All three must complete successfully.
- Do not amend a published commit. Preserve clean review evidence across only
  conflict-free equal-range-diff restacks or eligible test-only remediations
  with the identity, verification, and closure evidence required by
  `code-review-loop.md`.
- Never promote or parent from a failing candidate. Preserve evidence, identify
  the owning slice and root cause, return affected slices to `in_progress/`,
  correct the implementation or recorded design, and verify and review a new
  immutable candidate. Integrity failures block the affected chain until safely
  reconciled; continue independent work. When the full-pipeline export test
  exists, do not skip it for a complete candidate unless the user cancels it.
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
