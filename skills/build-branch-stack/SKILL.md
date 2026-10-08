---
name: build-branch-stack
description: Build explicit approved scope or automatically drain the to_do spec queue as a linear stack, prioritizing parallel implementation and maintaining one canonical build manifest.
disable-model-invocation: true
metadata:
  layer: runner
---


Read `references/operational-records.md` before creating or updating plan metadata,
builds, releases or deployments. Its schema-v2 JSON contract is authoritative
for operational records. Write and validate canonical JSON alongside each state
change; do not leave the browser report to reconstruct state from Markdown.
Use `scripts/validate_operational_records.py <record> --project-root <original-project>`
for each owned record before handoff. Whole-project audit findings are separate.
Keep historical extensions and existing authorization, verification and review
gates; they do not authorize schema aliases or inferred reporting values.
# Build Branch Stack

Build and push reviewed slices from explicit scope or, when none is supplied,
the approved `plans/specs/to_do/` queue and slice maps. Specs group work; slices
are implementation units. One coordinator owns the linear stack and manifest.
Prioritize parallel implementation within and across specs; accept each spec
as a contiguous block. Use `open-stack-requests` in draft mode as branches stabilize when CR
publication is authorized; do not wait for release assembly.

Minimize elapsed time to verified release handoff without weakening any gate.
Dispatch all eligible work up to actual worker, reviewer, and resource capacity.
Impose no branch-count or wave-size limit; reuse proven equivalent evidence.
Follow `references/scheduling.md` throughout execution.

## Resources

Resolve `orchestration_skill_root` to this directory. Read
`references/orchestration-runtime.md` and
`references/orchestration-plans-layout.md` first, then
`references/queue-build.md` for selection, resumption, spec order, stack
assembly, and concurrent release ownership. For each plan, use
`references/git-branch-commit.md` for branch and commit operations,
`references/git-sync-branch.md` for verified pushes, then
`references/from-reviewed-plan-to-git-handoff.md`. Read other references when
their step requires them. Read `references/artefact-audit.md` after a feature
reaches `review/`; revisit only its pending cross-branch questions after a tested
stack snapshot exists. Read `references/release-manifest.md` before creating or
changing the manifest.
For concurrent prefix preparation, read sibling
`prepare-release-integration/references/release-preparation.md` for snapshots
and handoffs; `queue-build.md` defines build ownership.

Read `references/trim-review.md` before launching the first trim pass.

## Inputs

- Optional explicit specs, slices, branches, or repair/resume manifest.
  Otherwise discover the queue under `references/queue-build.md`.
- Executable reviewed slices at `plans/slices/<stage>/<slug>/<slug>.md`,
  each linked to its approved parent and map, or explicitly classified legacy
  cohesive slices. Missing readiness is recorded before dispatch.
- Base branch: the remote default unless the user names another.
- Starting branch: the base unless the user names an existing parent.
- Plan branch: create one by default, or use a user-selected existing branch
  after validating its parent, existing commits, and remote state.
- Code prerequisite map, separate from Git stacking order. A verified
  cumulative parent may contain several required slices.
- Layout: `linear` for new builds unless the user specifies another layout;
  preserve the existing layout on resume.
- Build ID and manifest path. New runs use `stack-build-<YYYYMMDDTHHMMSSZ>`
  under `plans/builds/`; generate once using the runtime identity rules.
  Repairs and resumes retain their existing ID and manifest.
- For a repair run, the canonical release manifest, affected branches, and the
  publisher's evidence that any affected ready CRs are draft.

Append linear candidates to the verified tail in spec blocks. Independent
workers may share a verified authoring base; the coordinator restacks before
acceptance. Record placement separately from functional prerequisites. In an
explicit dependency/base-targeted layout, independent branches use the base.
Honor real prerequisites; never invent dependencies to explain stack order.
Release scope follows what must ship. Never impose a branch-count cap. When
the graph, conflict surface, or acceptance cost is unusually high, make a
smaller implementation split with concrete evidence. The user controls release
scope; this runner controls whether one branch is a safe implementation unit.

## Progress

Keep one compact table and update it on state, review, commit, restack, or
verification changes:

```text
| Plan | Status | Reviews | Branch | Commit | Next action | Waiting on |
```

The coordinator records selection, spec order/current spec, prepared candidates,
assignments, and accepted tail in `schedule`, with contributor history in
`sessions`. Give each waiting task a concrete reason under `scheduling.md`;
routine conflict risk or later spec placement cannot justify idle capacity.

Use `Queued`, `In progress`, `Review cap reached`, `In review`, `Release ready`,
or `Blocked`. `In review` means this slice's implementation, trim, and
correctness passes finished or reached the cap; it does not depend on ancestor
review decisions or descendants. Record the transition SHA in `review_handoff`.
`Release ready` requires current-tip checks, clean reviews or accepted capped
disposition, qualified pinned ancestors, and final stack checks. A routine
restack makes current-tip evidence pending without changing `In review`.
Number review passes. Call an ongoing pass “pass N” or “next fresh pass”; use
“final,” “last,” or “closing” only after all completion conditions are satisfied.

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

The runner may create a prerequisite slice within the same approved outcome,
release scope, ownership, and exclusions. Save it as a draft, record approval
under existing build authority, and update the map, dependency graph, and
manifest using the shared layout. Independently releasable new outcomes require
a product-scope decision.

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

Read `references/review-convergence.md` before the first implementation or
review dispatch and on each architecture reassessment. Preserve its review
pass cap, failure-family counts, authority boundaries, and capped handoffs.

## Readiness

Before moving plans or editing code, inspect repository instructions, plans,
parent specs, slice maps, branch refs, and CI. Specs are selection/grouping
inputs; executable slices own implementation. Resolve specs and slices by slug
in their stage folders. Require
`Approval Status: approved` on both, an approved map, and parent stage `backlog`,
`to_do`, `in_progress`, or `review`. Reject draft, in_release, merged, fulfilled, superseded, or
stale inputs. Require plan review before implementation dispatch; record
unreviewed selected slices as waiting and complete the required review when
authorized. Migrate legacy folders under the shared layout. Before creating or
adopting a branch, answer:

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

Resolve explicit selection or resume/discover the queue under `queue-build.md`
before moving files. For a fresh run, initialize the canonical JSON manifest
from the pinned starting base, selected specs/slices, explicit exclusions, real
code prerequisites, declared surfaces, and planned checks. Keep unimplemented
work in `schedule.work`, not placeholder branch entries. In linear mode,
`branches` contains only accepted, verified, pushed stack branches. Use schema-v2 `operational-records.md` for new and adopted JSON.
At each implementation, pass and review/restack handoff, import validated
receipts and the worker's `operator_handoff`, derive counts, and run
`scripts/validate_operational_records.py <manifest> --project-root <original-project> --require-operator-handoff`.
Initialize handoffs as draft; after implementation verification, reconcile
operator text and classifications against the branch-only diff and current
pin, then mark ready. A suggested test and pass condition claim no acceptance
result. Retain historical v1 tools only for historical records; never fabricate
receipts to pass validation. Reconcile Sheet and prose trackers
from the manifest.

Move only the selected reviewed feature directories from
`backlog/` to `to_do/`. Accept selected features already in `to_do/`. Resolve
their new plan paths before starting; leave unrelated backlog features alone.
At every child transition, including repairs, update `Slice Status` and
reconcile the parent from its complete approved map. Preserve approval, repair
links, and report blockers using the shared layout.
For a selected legacy `plans/<slug>.md`, move it and any sibling
`<slug>.reviews/`, `<slug>.execution/`, and `<slug>.evidence/` into
`plans/slices/to_do/<slug>/` first. Stop on a destination collision.

Use the scheduling contract to dispatch work as each branch becomes eligible.
Pin each authoring base and eventual stack parent separately. Failed
verification or integrity blocks dependent work, not unrelated preparation;
unfinished ancestor reviews do not block implementation or the next spec block.
Keep prepared slices in `in_progress/` until stack acceptance and review mapping;
accepted slices stay there until their own trim and correctness finish. Draft
CRs require accepted, verified pinned branches; ready CRs need a qualified chain.

For each eligible implementation, dispatch these branch-local steps:

1. Record real code prerequisites and the assigned authoring base. Fetch and
   pin that base; in linear mode it may be a shared verified baseline rather
   than the future stack predecessor.
2. Create its local plan branch from the assigned authoring base, or validate the selected
   existing plan branch with `git-branch-commit.md`, then move its feature from
   `to_do/` to `in_progress/` before implementation. On a repair run, verify
   the existing branch and manifest instead of recreating it; move only
   affected features to `in_progress/` only when implementation work is needed;
   restack descendants in their current stage.
3. Follow `from-reviewed-plan-to-git-handoff.md` through the verified candidate.
   Require the design checkpoint in `plan-implement.md` before editing. Resolve
   cohesion or architecture changes under the rules above. Keep verification
   machinery proportionate to candidate-owned behavior; simplify a seam that
   simulates unchanged external or dependency-owned lifecycles. Run capability
   authoring checks and exact candidate verification, then selectively stage,
   review, commit, and verify the exact SHA in a clean worktree under
   `verification-runner.md`. Final integration checks do not replace candidate
   verification.
   Create or update the remote branch at the first verified commit. A provisional
   descendant may push provisionally on its recorded parent SHA after the
   ancestor ref advances: require that SHA to remain the tip's ancestor, pass
   integrity checks, and use an explicit lease for the expected remote branch
   state, including absence for a new branch. Fetch after the push and confirm
   local, upstream, remote, and verified tips match. Record the authoring base
   and verified candidate in `schedule.work` until linear-stack acceptance;
   record accepted parent movement and final pins in `branches`. Keep the feature in
   `in_progress/`. For this provisional case, the pinned-parent check in
   `git-sync-branch.md` applies to the recorded SHA, not the ancestor ref head;
   its first-push plain refspec also needs the explicit lease.

Record parallel authoring results as `prepared` in `schedule.work`. The
coordinator restacks onto the tail in spec order, re-verifies, pushes, and
records accepted pins/checks in `branches` before advancing `schedule.tail`.
Prepared candidates may run provisional trim/correctness on their verified,
pushed tips and pinned authoring parents. Record receipts in `schedule.work`;
carry conclusions onto accepted tips only through valid identity/mapping proof.
Follow `queue-build.md` for acceptance, evidence transfer, and publication handoffs.

Start each prepared or accepted branch's trim once its tip is verified and pushed
and its review parent SHA is pinned. Run eligible passes up to reviewer capacity.
A moving ancestor makes a descendant provisional, not ineligible. Within a
branch, triage pass N, apply accepted reductions, verify and push, then start pass N+1.
Start correctness pass 1 when that branch's trim is proportionate. Run eligible
numbered correctness passes concurrently across branches on pinned parent-to-tip diffs.
Eligibility requires handled prior findings and a verified, pushed tip, not
clean ancestors. Assess validated findings as they arrive; start provisional
fixes in an isolated checkout under `code-review-loop.md`. Reconcile all three
before changing the tip. Fix accepted findings from the earliest affected
branch forward. Defer descendant restacks until upstream fixes settle; they
may keep reviewing pinned diffs provisionally. Do not hold trim for a restack.
Once upstream fixes settle, restack affected descendants, verify tips, and
update pins, packs, and manifests. Retain reviews only through `code-review-loop.md` mappings;
below the cap, unmapped changes need a fresh pass. For an accepted capped
slice, carry the human decision through a proven unchanged-behavior restack
mapping and unchanged finding risk; otherwise remediate or seek a new decision.
Carry trim only while the new diff remains proportionate.

At the five-pass cap, finish accepted remediation and closure, verify, push,
and preserve artefacts. Record unresolved findings and `review_cap_reached`;
seek human disposition separately for release readiness.

Move each slice to `review/` when its verified pushed tip has proportionate
trim, passed branch checks, and clean correctness reviews or the exhausted cap.
Require stack acceptance and current-tip review coverage, not clean ancestors. Preserve
`.reviews/`, `.evidence/`, and `.execution/`; record `review_handoff` with the
transition SHA, outcome, and evidence. Record pending human, external, and
release-candidate checks with owners and prerequisites. Refresh paths and
validate the manifest. On move failure, return to `in_progress/`. Hand an
authorized draft CR to `open-stack-requests`; this skill opens no CR.

Before each plan and final handoff, compare every local parent with its pinned
SHA and refetch any parent already on `origin`. If a parent moves, record the
movement and restack affected descendants once upstream fixes settle. Continue
eligible pinned-diff trim and correctness reviews. The recorded parent SHA
must remain an ancestor of the verified descendant tip; the parent ref need
not still point to it for a provisional push.
Require the normal integrity checks and an explicit lease against the expected
remote branch state for that push. On a repair run or unexpected movement,
restack affected descendants in their current stage and mark current-tip
evidence pending. Move a slice to `in_progress/` only when implementation work
is needed. Synchronize tips with explicit leases.
Classify each delta as `verbatim`, `mechanical regeneration`, or
`intentional behavior change`. Verify every new tip with the smallest sufficient
combination of fresh checks and deterministic evidence reuse. Verification
proves that every required check applies to the current tip; it does not require
rerunning an unchanged check. A new SHA or reviewer pass alone is not grounds
to rerun one. Do not rerun an expensive deterministic check when the capability's
equivalence rules prove unchanged determining inputs and effective result.
A restack retains reviews through an equal `range-diff` with effective-identity
proof, or a focused `reviewed_restack` mapping under `code-review-loop.md`.
That mapping permits a proven generated-metadata-only manual resolution; other
manual resolutions, unmapped changes, or changed behavior need a fresh pass.
Record SHA mappings and confirmations. Scope unexpected local changes.
When an otherwise-clean discovery pass has one accepted finding resolved only
by an eligible test-only remediation, follow `code-review-loop.md`: verify the
new SHA, obtain same-session closure from each originating reviewer, and record
`test_only_closure` mappings instead of running another discovery pass.

A qualified prefix needs its own candidate-wide checks; pending checks for the
larger build do not block it. After all plans, run full-stack checks without a
blanket review. Review again only where restacks or integration fixes changed
behavior or invalidated mappings:

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
   owning slice to `in_progress/` when a fix is needed; restack and re-verify
   affected descendants in their current stage. Record human or external acceptance as
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

Leave completed features in `review/` until a recorded, fully assembled release
candidate covers their pinned tips; then use `in_release` under the shared layout.
Keep that stage through pending release-candidate, human, or external checks.
Import release-coordinator membership handoffs and reconcile parents before
shared stage moves and manifest repairs. Build completion alone does not qualify. If a later check reveals a defect, return its
owner to `in_progress/` for a fix; restack affected descendants without
changing their stage unless they need implementation work. Refresh the canonical manifest at its
stable release path and check every recorded plan and artefact path. Freeze only
when the user selects a complete candidate, final stack checks pass, and all
included branch tips, automation-clean reviews or SHA-pinned accepted capped
dispositions, and required agent
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
- Complete each branch's trim phase before its correctness discovery. Correctness
  reviewers still flag material proportionality failures missed by trimming.
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
  conflict-free restacks with valid mappings or eligible test-only remediations
  with the identity, verification, and closure evidence required by
  `code-review-loop.md`.
- Never promote a candidate with failed checks or unresolved material findings
  that the recorded human disposition has not explicitly accepted on its exact
  review-capped SHA.
  Failed verification or integrity blocks new descendants. A verified candidate
  with review findings may parent provisional descendants; release readiness
  still waits for a qualified ancestor chain.
  Preserve evidence, identify the owning slice and root cause, return slices
  needing implementation fixes to `in_progress/`,
  correct the implementation or recorded design, and verify and review a new
  immutable candidate. Integrity failures block the affected chain until safely
  reconciled; continue independent work. When the full-pipeline export test
  exists, do not skip it for a complete candidate unless the user cancels it.
- Do not mark a feature `fulfilled/` while external acceptance is pending or a
  failure remains unresolved. Record passed checks or an authorized decision
  explicitly accepting each limitation before `fulfilled/`; retain the confirmed
  merge requirement in `references/orchestration-plans-layout.md`.
- Pending external acceptance also blocks a production decision unless an
  authorized decision explicitly accepts the limitation.

## Handoff

Save and validate the canonical manifest at
`plans/builds/<build-id>/manifest.json` or the repository-defined stable
path. It records the base, ordered branches, dependencies, targets, tips,
surfaces, checks, all three review mappings, CRs, exclusions, freeze, integration,
acceptance, and deployment state; link detailed evidence instead of duplicating
it. Report child and parent stages, `review_handoff`, current-tip evidence,
release readiness, and pending dispositions, restacks, and checks with prerequisites.
Report selection, spec order/current spec, tail, prepared work, assignments,
waiting reasons, and audit decisions, specs/maps, draft/backlog plans, and
incomplete work. Link the manifest and pinned release preparation. State whether
draft CRs were published or remain a next action; this skill creates no CR.
