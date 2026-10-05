# Plans Layout

Specs and executable slices share lifecycle stages; approval is separate:

```text
plans/specs/<stage>/<spec_slug>/record.json
plans/specs/<stage>/<spec_slug>/<spec_slug>.md
plans/specs/<stage>/<spec_slug>/<spec_slug>.slices.md
plans/slices/<stage>/<slug>/record.json
plans/slices/<stage>/<slug>/<slug>.md
plans/slices/<stage>/<slug>/<slug>.reviews/
plans/slices/<stage>/<slug>/<slug>.execution/
plans/slices/<stage>/<slug>/<slug>.evidence/
plans/builds/<build-id>/manifest.json
plans/releases/<stage>/<release-id>/preparation.json
plans/deployments/<deployment-id>/manifest.json
plans/audits/<audit-id>/
```

Both use `draft`, `backlog`, `to_do`, `in_progress`, `review`, `in_release`, `merged`,
`fulfilled`, and `superseded`. `Specification Status` or `Slice Status` must
match the folder. `Approval Status` is `draft` or `approved`. Delivery progress
preserves scope approval. Writing requests, folders, and successful checks do not imply approval.

## Operational Records

Maintain schema-v2 `record.json` with each spec and slice. Operational JSON
contracts are in `operational-records.md`; Markdown is narrative, not report
input. Update JSON on approval, selection, stage moves and source rewrites.

Build manifests record implementation, branch dependencies, reviews, checks,
and every contributing session. Keep them in `builds/<build-id>/` after their
changes ship; a release links its contributing builds rather than copying or
moving them. New build IDs use `stack-build-<YYYYMMDDTHHMMSSZ>` from UTC time,
generated once and retained across repairs and resumes; describe scope in the
manifest. Existing IDs and legacy `release_id` fields remain unchanged.

Release records identify selected scope, pinned candidates, PR assembly, and
acceptance. Use `releases/active/` while preparing or awaiting final disposition,
`released/` after the final merge and required acceptance are confirmed,
`superseded/` for an identified replacement, and `cancelled/` for an explicitly
abandoned candidate. Record the disposition, evidence, and replacement links,
then move the whole folder and repair maintained references. Deployment alone
does not establish a released candidate. Resume unchanged inputs under the same
ID; changed scope or pinned inputs create a new linked candidate, not an attempt
subfolder. Move an existing whole-release record; create a linked summary only
when none exists. Do not duplicate its build evidence or invent historical states.

Deployment receipts record installing a candidate, with environment and outcome
inside `deployments/<deployment-id>/`. Retain failed and superseded receipts;
link their release when applicable. Historical release folders may retain mixed
release/deployment evidence.

Use `audits/<audit-id>/` for separate investigations, production acceptance,
reconciliation and maintenance records that may span builds or releases. Link
applicable plans and operational records. Implementation checks stay with their
build or slice. Keep audit folders flat; include an index of findings, commands,
outcomes and retained evidence. Moving an archive does not authorize deleting it.

Resolve supplied legacy record paths on resume; do not create a second record
at the new default. Defer moves used by active workers until they finish or
adopt the new path. Preserve dated logs and archives, and retain a migration map.

## Drafting and Approval

Save specs and slices in `draft/` with both statuses `draft`. Revise and trim
the files, then present their absolute paths for explicit approval. Approval
sets `Approval Status: approved` and moves the whole folder to `backlog/`;
there is no `approved/` delivery stage. Approve saved children with their
decomposition; parent approval alone does not approve them. Required plan
review precedes implementation selection and does not use delivery `review/`.

A spec defines the complete outcome and stable acceptance IDs. Decompose or
build only approved specs in `backlog`, `to_do`, `in_progress`, or `review`.
Each slice references its parent and map, owns cohesive acceptance IDs,
excludes sibling outcomes, and has independent verification and rollback
boundaries. Standalone legacy plans require explicit classification and the
same cohesion check.

The `.slices.md` map stays beside its parent and moves with it. Save proposed
maps and children before approval. `Slice Map Status` is `draft`, `approved`,
or `stale`; only approved maps authorize builds. Give each acceptance ID one
owner and record slice outcomes, blockers, verification and rollback boundaries,
and exclusions. Use slugs, not stage-dependent paths. Keep branch, release,
and deployment state in the corresponding operational records.

Material changes to acceptance IDs, scope, binding decisions, authorized
complexity, required verification, or external acceptance reset a spec's stage
and approval to `draft` and its existing map to `stale`. Apply these child rules:

- Move unstarted `backlog` or `to_do` children to `draft`, setting both slice
  and approval statuses to `draft`. Preserve prior approvals, selection history,
  and evidence; update maintained links and manifest paths.
- Preserve stages and evidence for `in_progress`, `review`, and `in_release`
  children; record the reapproval blocker in their plans and build/release records.
  Block affected delivery until the revised spec, map, and child plans are approved.
- Preserve `merged` and `fulfilled` results; use follow-up slices for changed
  requirements. Leave superseded history unchanged.

Approve the revised spec, map, and saved children together; add no per-child
approval ceremony. Reapproved unstarted children return to `backlog`; restoring
`to_do` requires a separate selection decision.

Changes to a slice's approved outcome, ownership, exclusions, or dependencies
require reapproval through `write-slices`: save it as a draft, mark the map
stale, and preserve implementation and review evidence. After final merge,
use a follow-up slice for new work. Clarifications preserve approval.

An implementation-only split preserving approved outcomes, ownership,
exclusions, release scope, and external acceptance is a clarification. Record
its reason and revised verification and rollback boundaries. Save new children
as drafts; existing build authority may approve them and the revised map if
it covers the split. Record that authority, advance them to `backlog`, and
retain spec approval without adding a human approval gate.

## Parent Progress

Reconcile parents after decomposition approval and every child stage change
within `write-slices`, `build-branch-stack`, or release/merge completion.
A spec awaiting approval stays in `draft`. Before delivery, an approved spec without an
approved decomposition stays in `backlog`. Draft or stale maps alone do not reset
child stages; a parent returned to draft applies the child rules above.

Require a nonempty approved map, approved children resolving exactly once
across current and legacy locations, and consistent acceptance ownership.
Missing, duplicate, draft, unapproved, or superseded children, a draft/stale map,
inconsistent ownership, or a destination collision block reconciliation.
Retain the current stage and report the blocker; an empty map proves nothing.

Apply these rules in order to the complete approved map, not just the selected
release or currently running batch:

| Mapped child states | Parent stage |
| --- | --- |
| Every slice fulfilled and required parent acceptance passed or explicitly accepted | `fulfilled` |
| Every slice merged or fulfilled, with required child or parent acceptance outstanding | `merged` |
| Every slice in in_release, merged, or fulfilled, with at least one in_release and one prepared candidate covering all unmerged slices | `in_release` |
| Every slice in review, in_release, merged, or fulfilled, with at least one final merge pending and no complete prepared candidate coverage | `review` |
| Any slice started, and at least one slice remains in backlog, to_do, or in_progress | `in_progress` |
| None started and at least one selected in to_do | `to_do` |
| Every slice in backlog | `backlog` |

A defect returning an unmerged child to `in_progress` returns its parent there.
Keep merged work in `merged` while acceptance remains unresolved; track required
fixes in follow-up slices without undoing the confirmed merge. Add no acceptance
gate absent from the approved spec. Release preparation reconciles `in_release`
after complete candidate assembly.
`merge-stack` reconciles `merged` and
`fulfilled` after confirmed final merges, including partial runs and resumes;
intermediate integration merges establish neither stage.

On a parent transition, move its folder and map, update `Specification Status`,
repair references, and report the change in that workflow. Read-only workflows
report discrepancies without moving files. Do not infer legacy standalone parents.

## Supersession

Before moving a replaced plan to `superseded/`, record replacement slugs,
reason, and approval or existing authority. Preserve history and evidence;
superseded plans cannot be selected, built, or counted as fulfilled.

For slices, revise and approve the active map, transfer each acceptance ID to
one replacement owner, and update blocker links before excluding the old slice
from parent progress. Superseding a parent blocks child delivery; record which
children are replaced or reassigned to an approved parent. Replacement never
fulfills a child.

## Moves and Legacy Layout

Move whole folders, including maps and artefacts, at lifecycle transitions.
Create destination parents; stop on collisions or active users of the old path.
Never merge folders. Update internal status, incoming and outgoing links,
handoffs, and manifest plan/artefact paths. For a frozen manifest whose digest
includes moved paths, recompute the digest after path-only repairs; retain its
freeze authorization and time, and record old/new digests and the migration.
Changed source, dependency, or candidate scope still invalidates the freeze.
Verify paths and report incomplete
moves or repairs without undoing confirmed merges. Keep internal slice links
relative so they survive moves.

Spec slugs and slice slugs must each be unique across stages, including drafts,
superseded history, and legacy locations. Read-only workflows resolve legacy
paths without moving them. Authorized writing or delivery workflows migrate
encountered plans while preserving approval, acceptance IDs, evidence, and progress:

- Legacy `Specification Status: approved` records approval, not delivery.
  Add `Approval Status: approved`; derive the new stage from a valid approved
  map and verified children, or use `backlog` when no decomposition exists.
  Invalid maps block progress derivation; repair the map before moving the
  parent out of its legacy location. Keep legacy draft specs unapproved;
  preserve recorded fulfillment and supersession subject to their evidence.
- Legacy slices in `backlog`, `to_do`, `in_progress`, `review`, or `merged` keep
  that stage, subject to confirmed final-merge evidence for `merged`.
  Add explicit slice status and approval metadata from recorded approvals and
  the approved map; do not invent approval for unmatched or unapproved plans.
  Unapproved plans become saved drafts while preserving their existing evidence.
- Legacy `plans/slices/done/` or `plans/done/` becomes `fulfilled/` only after
  confirming landed merges and completed or explicitly accepted acceptance.
  A confirmed final merge with pending acceptance goes to `merged`; an unmerged
  change goes to `review`, or `in_progress` when a failed check needs a fix.
- Encountered `review` slices with confirmed final merges go to `merged` while
  acceptance remains pending, or directly to `fulfilled` once satisfied.
- Move `plans/specs/<spec_slug>/` to its reconciled lifecycle stage and
  `plans/<stage>/<slug>/` under `plans/slices/`, applying the same rules.
  Classify a legacy broad specification through `write-specs`; never treat it
  as a slice. A spec with no recorded approval is a draft.

Use the move rules above; leave no duplicate.

## Delivery Stages

Operational records live outside spec and slice lifecycle folders. Their
canonical JSON owns branch order, targets, SHAs, checks, acceptance, CRs,
integration, and deployment state; spreadsheets and prose are reconciled views.

- `draft`: saved specification or slice awaiting scope/decomposition approval.
- `backlog`: approved scope, not yet selected for implementation. A slice's
  parent and map must also be approved before it is considered for `to_do`.
  Required child-plan review and implementation prerequisites may remain pending.
- `to_do`: a reviewed slice selected for the implementation batch; the parent
  reflects selection across its approved map. Move only selected children.
- `in_progress`: implementation, fixes, CLI code review loops, commits, and
  required branch checks are underway, or a defect needs implementation work.
  Keep a slice here through proportionate trim and clean correctness reviews
  or the five-pass cap. Finish accepted cap remediation and closure; record
  unresolved findings. Do not wait for ancestor reviews or descendants to
  finish this slice's review passes.
- `review`: implementation handoff is complete; operator review or release
  selection remains. Final destination merge is pending; implementation and
  trim are complete, and correctness passes are clean or capped. At entry, its pushed tip
  passes exact-tip verification; record `review_handoff` on that SHA and preserve
  artefacts. A capped slice may await human disposition here. Keep it here
  through routine restacks, pending current-tip checks, review mappings, human
  acceptance, and external or release-candidate checks until included in a
  recorded, fully assembled release candidate. Starting preparation, selecting
  branches, creating individual PRs, or partial assembly alone does not qualify.
  A changed ancestor
  requires restack and re-verification before release progression, but does
  not undo completed implementation. Return to `in_progress` when a defect,
  failed check, or behavioral change requires implementation work. Record
  pending checks with owners, procedures, and prerequisites. Parent `review`
  means some mapped scope still awaits review or release selection, or complete
  prepared-candidate coverage cannot be established.
- `in_release`: the slice's pinned tip is included in a recorded, fully assembled
  release candidate whose commit and tree are confirmed. Review, staging tests,
  acceptance, and the final PR now proceed through that release. Record the
  release ID, preparation path, candidate SHA, and included tip in the build
  manifest's branch `release_candidate` when a build manifest exists; otherwise
  link the preparation record's change entry from the slice. Verify inclusion
  against Git or recorded squash mapping. Preserve historical build pins; when
  the selected source differs, record its source and included tip separately
  from `build_tip_sha`, with evidence linking the preparation change entry.
  Do not imply unchanged code or review applicability without separate proof.
  This stage proves neither staging success, acceptance, final
  merge, nor production deployment. Keep already merged/fulfilled slices in
  their stages. A spec enters only when one prepared candidate covers every
  unmerged child in its complete approved map and all others are merged or
  fulfilled; partial scope leaves the parent in `review`. If that candidate is
  cancelled, superseded, withdrawn, or invalidated, return unmerged slices to
  `review` unless an unchanged tip remains covered by another qualifying
  candidate. Record replacement links. Defects requiring implementation return
  their owning unmerged slices to `in_progress`. Reconcile parents and repair
  maintained paths; active coordinators own shared moves and manifest writes.
- `merged`: the final destination merge (normally master) and landed commit are
  confirmed, but required acceptance remains pending or unresolved. Record merge
  evidence and each outstanding check's owner, procedure, and result. Staging
  deployment and intermediate integration merges do not qualify. A spec enters
  `merged` when every active mapped slice is merged or fulfilled and required
  child or parent acceptance remains outstanding. Preserve merge history when
  acceptance fails; use follow-up slices for fixes. Move directly from `review`
  or `in_release` to `fulfilled` when acceptance is satisfied at final merge.
- `fulfilled`: every final required acceptance check passed or its limitation
  was explicitly accepted by an authorized decision maker, and the change
  request's final destination merge and landed commit are confirmed. Review-cap
  disposition alone is insufficient. Implementation or code review completion
  alone is insufficient. For specs, all active mapped slices and required
  parent acceptance must meet the fulfillment rules above.
- `superseded`: replaced by identified plans and no longer actionable; use the
  supersession rules above.

For repair runs, return only slices needing implementation work to
`in_progress`. Restack and re-verify descendants in their current stage unless
they also need implementation work, then reconcile affected parents.

## Artefacts

- `<feature_dir>/<slug>.reviews/` contains `plan-review-pass<N>/`,
  `code-review-pass<N>/`, `code-review-pack/`, and
  `code-review-triage-ledger.md`. After the branch handoff audit it also
  contains `artefact-audit-ledger.md`, which records follow-up planning
  decisions for that feature.
- `<feature_dir>/<slug>.execution/` contains one-off scripts and execution
  helpers. Keep permanent tests and tooling in their normal repo locations.
- `<feature_dir>/<slug>.evidence/` contains small test outputs, measurements,
  and comparisons. Maintain `index.md` with the tested commit and worktree
  state, commands, results, and relative links to evidence and helpers.
- Give each worker or run distinct subdirectories. Keep protected inputs,
  large databases, dumps, and bulk outputs outside artefact folders; record
  external paths and reproduction commands in the index.
- Preserve all three folders, when present, in the user's main checkout before
  removing a worktree.

## Plan Slug Format

Use durable repo terms. Avoid dates, agent names, and vague words. Examples:
`catalog_relationship_ownership`, `valid_gtin_quality_gate`.
