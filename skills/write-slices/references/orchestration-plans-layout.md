# Plans Layout

```text
plans/specs/<stage>/<spec_slug>/{record.json,<spec_slug>.md,<spec_slug>.slices.md}
plans/slices/<stage>/<slug>/{record.json,<slug>.md,<slug>.reviews/,<slug>.execution/,<slug>.evidence/}
plans/builds/<build-id>/manifest.json
plans/releases/<lifecycle>/<release-id>/preparation.json
plans/deployments/<deployment-id>/manifest.json
plans/audits/<audit-id>/
```

Specification/Slice Status matches stage folder; Approval Status independently
remains draft/approved. Progress, folder creation or checks imply no approval.
Update schema-v2 record/narrative together under operational-records on approval,
selection, moves and rewrites. JSON owns operational/report values; prose/Sheets
are projections. Slugs use durable repo terms, not dates/agents/vague names (e.g.
catalog_relationship_ownership); unique per spec/slice namespace across stages,
drafts, superseded and legacy locations.

## Approval and changes

Save/trim drafts with both statuses draft and present absolute paths for approval.
Approval sets approved and moves whole folder to backlog; no approved delivery stage.
Approve saved map/children together; parent approval alone approves no child.
Human to_do selection records review/readiness, including authorized explicit build
selection. No repeat approval/agent plan-review phase or artifacts for unchanged
approved scope; separately requested critique is outside delivery.

Specs define complete outcome/stable acceptance IDs; only approved parents in
backlog/to_do/in_progress/review authorize decomposition/build. Slices link parent/
map, own cohesive acceptance IDs, exclude siblings and have independent verification/
rollback boundaries. Classify legacy standalone slices explicitly with same cohesion.
Maps stay beside parent, use slugs rather than stage paths, assign one owner per
acceptance ID with outcome/blockers/verification/rollback/exclusions. Save proposed
maps/children before approval; map status draft/approved/stale, only approved permits build.

Material changes to acceptance/scope/binding decisions/authorized complexity/required
verification/external acceptance reset parent draft+draft approval/map stale:

- Unstarted backlog/to_do children return draft, preserving approvals/selection/
  evidence and repaired references.
- Started/review/in_release children retain stage/evidence with reapproval blockers;
  affected delivery waits for revised spec/map/children approval.
- Merged/fulfilled need follow-up slices; superseded history stays unchanged.

Reapprove saved decomposition together; unstarted return backlog, separate decision
to reselect to_do. Slice outcome/ownership/exclusion/dependency changes use write-slices
reapproval/draft/stale map, retaining evidence; after final merge use follow-up.
Clarifications preserve approval. Implementation-only splits preserving outcome,
ownership/exclusions/release/external acceptance are clarifications: record reason/
verification/rollback, save new drafts, use covering build authority to approve
map/children into backlog without another human gate.

Verification-phase clarification follows operational-records reconciliation rules.
Preserve approved requirements and receipts; moving a saved mandatory branch gate
later requires explicit covering authority and synchronized spec/map/child/build
changes. A new skill version or an ordinary build invocation is not that authority.
Apply material-change reapproval rules unless the recorded decision explicitly
covers the affected plan amendments. Unchanged evidence/review counts survive;
reclassification alone does not restart execution or review.

## Delivery gates

| Stage | Meaning |
| --- | --- |
| draft | Saved scope/decomposition awaiting approval |
| backlog | Approved, unselected; parent/map approved before slice selection; code prerequisites may remain |
| to_do | Human-reviewed selected scope; move selected children only |
| in_progress | Implementation/fixes/checks/trim/correctness underway |
| hold | Explicit authorized pause/reason; retain approval/selection/pins/history; resume only under recorded authority |
| review | Accepted pushed verified own implementation/checks, proportionate trim, clean correctness or five-pass cap after accepted remediation/closure; final merge pending |
| in_release | Pinned member of fully assembled recorded candidate, confirmed commit/tree/inclusion |
| merged | Confirmed final-destination merge/landed commit, required acceptance outstanding |
| fulfilled | Final merge plus all required acceptance passed or limitations explicitly accepted by authorized decision maker |
| superseded | Replaced under recorded authority, no selection/build/fulfillment credit |

Review entry pins immutable review_handoff SHA/outcome/evidence, preserves artifacts
and pending checks' owners/procedures/prerequisites. Own review completion waits
for neither ancestors' decisions nor descendants/external/candidate checks. Routine
restacks retain review while current evidence becomes pending; changed parents
require restack/verification before release. Defects/check failures/behavior changes
needing edits return owners in_progress. Cap disposition alone is no final acceptance.
Hold establishes no completion/waiver.

In_release needs assembled candidate, not selection/preparation/individual PRs/partial
assembly. Record release_candidate release_id/preparation_record/candidate_sha/
included_tip_sha on branch, or link preparation entry if no build; verify Git/squash
inclusion. Historical rewrites retain build pins/reviews and separate build_tip_sha
from selected source/included tip with preparation evidence; review equivalence
needs independent proof. Already merged/fulfilled stay there. Invalidated/cancelled/
superseded/withdrawn candidates return unmerged members review unless another qualified
candidate covers unchanged tips; record replacements. Implementation defects return
owners in_progress. Candidate stage proves no staging/acceptance/final merge/deployment.

Only final destination merge (normally master), never staging/intermediate assembly,
qualifies merged/fulfilled. Acceptance failure preserves merge; fixes use follow-up.
If already accepted, final merge may move directly review/in_release→fulfilled.

## Parent reconciliation

Reconcile complete approved map after decomposition approval/every child transition,
including repairs/partial merges/resumes, never just selected batch/release. Draft
parent stays draft; approved without approved decomposition stays backlog. Stale/
draft map alone resets no child stages. Require nonempty approved map, each approved
child resolving exactly once across legacy/current paths and consistent ownership.
Missing/duplicate/draft/unapproved/superseded children, map/ownership/collision failures
retain parent stage with blocker. Apply in order:

| Complete mapped state | Parent |
| --- | --- |
| All fulfilled; parent acceptance satisfied/accepted | fulfilled |
| All merged/fulfilled; required child/parent acceptance outstanding | merged |
| All in_release/merged/fulfilled, some in_release; one prepared candidate covers all unmerged | in_release |
| All review/in_release/merged/fulfilled, final merge pending, no complete candidate coverage | review |
| Some started, some backlog/to_do/in_progress | in_progress |
| None started, some to_do | to_do |
| All backlog | backlog |

Unmerged defect returns parent in_progress. Add no unapproved acceptance. Release
workflow owns candidate reconciliation, merge workflow final merge/fulfillment.
Move parent/map, update status/links and report. Read-only workflows report discrepancies
without moves; infer no standalone parent.

## Supersession and moves

Supersession records replacement slugs/reason/authority and retains history/evidence.
Approve active map's replacement owner per acceptance ID and blockers before excluding
old slice. Superseded parent blocks delivery pending child replacement/reassignment;
replacement fulfills nothing.

Move whole folders/maps/artifacts; create parents, stop collisions/active old-path
users, never merge folders or duplicate plans. Repair status/incoming/outgoing links/
handoffs/manifest paths; internal slice links stay relative. Path-only frozen-digest
repairs retain authority/time with old/new digests/migration proof; source/dependency/
scope change invalidates freeze. Report failed moves without undoing confirmed merges.

Read-only callers resolve legacy paths; authorized writers migrate encountered plans:

- Old Specification Status approved means approval, not stage. Add approved metadata;
  derive stage from valid map/children or backlog without decomposition. Invalid map
  blocks derivation/move. Unapproved specs are drafts; retain fulfilled/superseded
  only with evidence.
- Legacy backlog/to_do/in_progress/review/merged slices retain stage (merged needs
  final merge). Derive approval from recorded decision/map, never invent it;
  unapproved/unmatched become drafts preserving evidence.
- Legacy plans/slices/done or plans/done requires final merge+acceptance for fulfilled;
  pending acceptance→merged; unmerged→review or in_progress if fixes needed. Apply
  same rule to encountered review slices already finally merged.
- Move plans/specs/<slug> to reconciled stage and plans/<stage>/<slug> into slices.
  Broad specs route through write-specs, never execute as slices.

## Operational archives and artifacts

Builds retain order/dependencies/pins/checks/reviews/sessions after shipping; releases
link evidence rather than copy/move it. New IDs once-generated UTC
stack-build-<YYYYMMDDTHHMMSSZ>; repairs/resumes retain ID/path and historical release_id.
Resolve existing legacy records instead of creating duplicates. Defer active-worker
moves until adoption; retain dated archives/migration map.

Release lifecycle active until final disposition; released needs final merge+acceptance;
superseded needs replacement, cancelled explicit abandonment. Record disposition/
evidence/links then move whole folder/repair refs. Deployment alone is no release.
Unchanged inputs resume ID, changed scope/pins create linked new candidate, not attempt
subfolders. Move existing whole-release record; linked summary only if absent, never
invent states. Deployment receipts retain failed/superseded outcomes/environment/
release links; historical folders may mix release/deployment evidence. Audits remain
flat investigations/acceptance/reconciliation/maintenance with indexed findings/
commands/results/evidence and plan/record links; archive move authorizes no deletion.

- .reviews: code-review-pass<N>, code-review-pack, code-review-triage-ledger and
  artefact-audit-ledger after audit. Preserve old plan reviews, not dispatch prerequisites.
- .execution: one-off helpers; permanent tests/tooling in normal repository locations.
- .evidence: small outputs/comparisons with index pinning commit/worktree/commands/
  results and relative evidence/helper links. Distinct worker/run subdirectories.
- Protected inputs/databases/dumps/bulk outputs stay outside artifacts with paths/
  reproduction in index. Preserve all three folders in primary checkout before cleanup.

Repair only slices needing implementation into in_progress; restack/reverify descendants
in current stages, then reconcile parents. Incomplete archive/audit moves never undo merges.
