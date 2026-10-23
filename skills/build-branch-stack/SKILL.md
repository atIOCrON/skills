---
name: build-branch-stack
description: Build approved slices as a linear branch stack, verify individual implementations, and hand integration testing to release/staging workflows. Support explicit scope or the to_do spec queue with parallel implementation and one canonical build manifest.
disable-model-invocation: true
metadata:
  layer: runner
---

# Build Branch Stack

Build and push approved executable slices from explicit scope or the approved
`plans/specs/to_do/` queue. Specs group work; slices own implementation. Finish
with individually verified branches in `review/` and a canonical build manifest.
Verify individual branch implementations here. Assembled-runtime integration,
cross-feature and deployed-asset/full storefront/Admin/cache/provider flows belong
to the later release/staging workflow: `prepare-release-integration` coordinates
`rebuild-staging-with-branches` and `verify-staging-acceptance`. Release selection,
acceptance and freeze belong to release preparation. Agent execution or branch-only
feature ownership does not turn release testing into a branch-completion gate.

## Contracts and ownership

Resolve `orchestration_skill_root` to this directory. Read these references before
selection/dispatch; each owns the named rules:

| Reference under `references/` | Authoritative rules |
| --- | --- |
| `operational-records.md` | Schema-v2 JSON, receipts, counts, operator handoffs and validation |
| `orchestration-plans-layout.md` | Approval, stages, parent reconciliation, moves and legacy paths |
| `orchestration-runtime.md` | Persistent owners, providers/transports, execution leases, IDs and sessions |
| `queue-build.md` | Selection/resumption, spec blocks, authoring/accepted pins and release ownership |
| `scheduling.md` | Eligibility, parallel capacity, isolation and waiting reasons |
| `review-convergence.md` | Failure families, architecture reassessment, fix limits and review cap |

The coordinator owns canonical state/plan moves, order/restacks/publication and
proof transfer. Persistent plan/approved-chain owners complete implementation,
checks/trim/correctness/closure and later fixes, including restack-invalidated work.
Use runtime's provider-matching, GUI-visible ChatGPT/Codex owner and same-session
rules. No native implementation owners or unauthorized provider fallback; preserve
counts/reviewer contexts. Invocation adds no credentials/external authority.

## Inputs and readiness

- Optional specs, slices, branches or repair/resume manifest; otherwise discover
  and drain the queue under `queue-build.md` without asking for selection.
- Approved executable slices at `plans/slices/<stage>/<slug>/<slug>.md`, linked
  to approved parents/maps, or explicitly classified cohesive legacy slices.
- Base: remote default unless specified. Starting branch: base unless an existing
  parent is specified. Create plan branches by default; validate a user-selected
  existing branch's parent, commits and remote state before adoption.
- Real code prerequisites, surfaces and checks, separate from Git placement.
  A verified cumulative parent may satisfy several prerequisites.
- Layout: `linear` for new builds unless specified; preserve layout on resume.
  Accept contiguous spec blocks onto the verified tail. Explicit dependency/
  base-targeted layouts place independent branches on base. Impose no branch cap.
- New build: generate `stack-build-<YYYYMMDDTHHMMSSZ>` once under runtime rules at
  `plans/builds/<build-id>/manifest.json`. Repairs/resumes retain ID/path. Repair
  inputs include the release record, affected branches and publisher evidence
  that affected ready CRs are draft.

Before moves or edits, inspect repository instructions, plans, maps, refs and CI.
Require approved slice, parent and map; eligible parent stages are `backlog`,
`to_do`, `in_progress`, `review`. Reject draft, stale, superseded, `in_release`,
merged or fulfilled inputs. Human `to_do` selection already records readiness:
require no agent plan-review artefacts or reapproval of unchanged scope.

Before branch creation/adoption, require one actor/integration-visible outcome,
coherent verification/rollback, explicit sibling exclusions and complete owned
acceptance-ID mapping. Split independently shippable/failing/rollback groups;
reassess combined providers, SDKs, lifecycle owners, acceptance environments or
coordinators introduced solely by grouping unrelated outcomes. Decompose within
approved scope; seek a decision only if ownership, outcomes or exclusions change.
Apply the same cohesion gate to legacy plans.

Read `references/implementation-readiness.md` before dispatch and include it in
owner instruction paths. Resolve missing capability, identity or evidence readiness.
Classify verification obligations under `operational-records.md` before dispatch;
only branch implementation obligations enter `implementation.required_check_ids`.
Carry later checks as pending with owners/procedures and blocking release or
activation milestones. On resume reconcile saved mandatory gates and approved
plans/maps under explicit covering authority; skill changes alone amend neither.

## Autonomous decision authority

An authorized build permits repository-local implementation, verification,
architecture, narrow dependency correction, plan amendments and slice decisions
needed for selected approved release scope without further approval when they:

- serve existing acceptance or a demonstrated prerequisite;
- preserve outcomes, exclusions, binding contracts and release membership;
- retain coherent implementation and rollback boundaries;
- add no independently releasable product capability;
- use the narrowest viable native owner or supported extension; and
- waive no evidence gate and require no production, destructive, credential,
  financial, legal or external-communication authority.

Treat a plan as a hypothesis. When evidence disproves its mechanism, preserve
it, return affected slices to `in_progress`, and amend plan, design checkpoint,
verification boundary, graph and manifest. Before edits record failure class,
alternatives, decision, added production surface, rollback effect and required
evidence. Follow Review Convergence across designs and architecture epochs.

Save in-scope prerequisites/splits as drafts, record approval under existing
build authority, and update map, graph and manifest. New product outcomes require
a scope decision. Require a human only to change product/release/frozen scope,
acceptance/exclusions, binding contract/policy, required evidence, broad upstream
ownership, or authority outside the above.

Integrity failures never authorize overwriting work. Reconcile unexplained ref
movement, staged/unstaged overlap, failed leases or missing artefacts; otherwise
block the affected chain and continue independent slices.

## Workflow

1. Select/resume and initialize pinned v2 scope under `queue-build.md`; planned/
   prepared work stays schedule.work, accepted verified pushed placements branches.
   Apply layout moves/parent reconciliation to selected scope, preserving history.
2. Dispatch all eligible work under `implementation-dispatch.md`/`scheduling.md`:
   isolated owners/checkouts/bases/leases, actual capacity, no artificial wave or
   ancestor-review barrier. Owners follow `from-reviewed-plan-to-git-handoff.md`
   and its implementation/staging/commit/exact-verification/publication references.
3. Import early candidates/completion promptly. After owner completion/lease return,
   assemble owned ranges in spec order with backups/comparison/checks/lease-push,
   record acceptance then tail. Prepared work cannot advance tail or enter review.
4. Read `trim-review.md` then `code-review-loop.md`; each branch trims before
   correctness, branches overlap. Fresh parallel Claude/Codex/Cursor outputs all
   complete substantively; local formatting repair never restarts review. Isolated
   provisional fixes wait for three-way triage before commit/push. Preserve counts.
5. Check/refetch parent pins before each plan/final handoff. Continue pinned reviews
   until upstream settles, then restack under git-branch-commit/git-sync-branch.
   Classify deltas, minimally verify with capability-proven reuse, and apply separate
   correctness/trim/disposition mappings. Return invalidated work to same owner;
   preserve stages unless edits needed. No correctness discovery pass 6.
6. Accepted slices enter review after own current checks, proportionate trim and
   clean/capped correctness after remediation/closure, with immutable review_handoff.
   External/ancestor/descendant gates do not delay move; failed moves return
   in_progress, routine restacks retain review/current coverage pending.
7. Authorized draft publication routes stable accepted pins to open-stack-requests
   before release assembly; this skill opens no CR. Ready gates remain separate.
   Run `artefact-audit.md` at handoff; primary-checkout planning changes no verified
   tip, and incomplete audit is separate from branch readiness.

Read `references/operational-records.md` before metadata changes. At implementation,
pass and restack handoffs, import validated receipts and `operator_handoff`, derive
counts and validate each owned canonical record:

```bash
python3 <skill-root>/scripts/validate_operational_records.py <manifest> --project-root <original-project> --require-operator-handoff
```

Initialize operator text as draft; reconcile wording/classifications against the
branch-only diff, current pin and `plan-implement.md` before marking ready.
Suggested tests claim no acceptance result. Never fabricate receipts or write v1
aliases into v2. Read `references/release-manifest.md` for build metadata and
conditional historical maintenance. Trackers and prose project canonical JSON.

## Progress and handoff

Update one compact table on state, review, commit, restack or verification changes:

```text
| Plan | Owner | Worker complete | Accepted/restacked | Checks / Reviews | Branch / Commit | Next action / Waiting on |
```

Record selection/order/current spec, prepared work, assignments, pauses/exclusions,
capacity and tail in schema-v2 extensions under the owning contracts. Every
waiting task needs a concrete reason and resume condition. Separate completion
on the original authoring tip from accepted placement and current coverage.
Number ongoing passes; use “final,” “last” or “closing” only retrospectively.

Finish with verified pushed selected tips, current branch checks, proportionate
trim, completed/capped correctness, safe placement and applicable evidence.
Preserve explicit user/repository branch gates; add no assembled-runtime
integration, deployment pipeline or release acceptance gate to build completion.
Use focused runtime/database proof when concrete implementation risk requires it,
with the cheapest sufficient seam and justified exceptions. Leave completed slices
in `review` while later checks remain explicitly pending, rather than waived/passed.
Pending required acceptance blocks fulfillment/production decisions unless an
authorized decision explicitly accepts the limitation; final merge remains required.

Use `references/orchestration-final-handoff.md` for branch reporting. Include
selection, spec order/current spec, tail, owners, worker-complete/accepted states,
child/parent stages, transition/current-tip evidence, caps/dispositions, pending
checks/restacks and prerequisites, pauses/exclusions, audit decisions, planning
references and incomplete work. Link the validated manifest and any pinned release
preparation; state whether authorized draft CRs were published or remain next.

For selected releases, hand pins, ancestry, prerequisites, branch evidence,
capped dispositions and acceptance requirements to `prepare-release-integration`.
Read sibling `prepare-release-integration/references/release-preparation.md` for
concurrent snapshots/handoffs; import membership/stage handoffs before shared
moves or repairs. Do not freeze a build merely because selected work finished.
