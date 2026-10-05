---
name: write-slices
description: Draft saved vertical-slice plans from approved specifications, obtain decomposition approval, trim unnecessary splits and checks, and maintain acceptance ownership and dependencies.
disable-model-invocation: true
metadata:
  layer: capability
---


Read `references/operational-records.md` before creating or updating plan metadata,
builds, releases or deployments. Its schema-v2 JSON contract is authoritative
for operational records. Write and validate canonical JSON alongside each state
change; do not leave the browser report to reconstruct state from Markdown.
Use `scripts/validate_operational_records.py <record> --project-root <original-project>`
for each owned record before handoff. Whole-project audit findings are separate.
Keep historical extensions and existing authorization, verification and review
gates; they do not authorize schema aliases or inferred reporting values.
# Write Slices

Turn one approved parent specification into branch-sized implementation plans.
Each plan must deliver a narrow, complete path through every affected layer and
leave the repository in a valid state.

Resolve paths against the user's primary checkout. Read
`references/orchestration-plans-layout.md` for moves and legacy migration.
Locate the parent by slug, including legacy paths; migrate broad legacy specs
through `write-specs`. Read its evidence, relevant code and contracts, and every
acceptance ID. Require `Approval Status: approved` and stage `backlog`, `to_do`,
`in_progress`, or `review`, rather than an `approved/` folder.

## Saved Drafts Before Approval

Use one slice when the outcome fits the slice test. Split only for concrete
implementation, release, or verification boundaries, not per file, layer,
acceptance ID, or planning phase.

Save proposed children in `plans/slices/draft/` with `Slice Status: draft` and
`Approval Status: draft`. Save the map beside its parent with
`Slice Map Status: draft`; material revisions make an approved map `stale`. Preserve prior
decisions and evidence. Revise and trim the files before seeking approval;
present absolute paths, slice slugs and observable outcomes, acceptance
ownership, blockers (or `none`), verification and rollback boundaries, and exclusions.

Approval of the saved decomposition and children sets the map and child
approval to `approved`, moves approved draft children to `backlog/`, and sets
`Slice Status: backlog`. Repair links, verify paths, and reconcile the parent.
Unchanged approved children retain their stage and approval unless the parent
returns to draft: apply the shared child reset and reapproval rules. Writing
files does not approve them; list order does not create dependencies. Add no
per-file approval gate.

## Slice Test

Each slice must:

- deliver one useful or safety-complete end-to-end behaviour;
- cross every required layer rather than isolate schema, backend, frontend, or
  tests as separate work;
- be independently testable and reviewable;
- be safe to release, disable, remove, or roll back without unfinished sibling
  work;
- fit in one fresh implementation context; and
- have at most one required unmerged predecessor. Use a merged prerequisite or
  a different split when several unmerged branches would be required.

Split independently useful outcomes with materially different implementation,
acceptance, or rollback boundaries. Providers, SDKs, lifecycle owners, and
acceptance environments inform this decision; they need not split a common
mechanical fix. Split if grouping alone requires a shared coordinator. A shared
page, package, release, or subsystem does not establish cohesion.

Combine slices when neither can be deployed safely or demonstrated without the
other. Keep cohesive fixes together when splitting only adds plans, branches,
approvals, or repeated checks. Prioritize independent safety and observability
over ticket count.

## Planning Trim Loop

Trim before decomposition approval, before child-plan handoff, and after
revisions add splits, dependencies, or checks.

1. Justify each extra slice and blocker. Remove administrative splits and
   dependencies based on list order or hypothetical reuse.
2. Inherit parent requirements and reuse checks. Justify added machinery,
   fixtures, checks, and gates by demonstrated slice risks. Choose the cheapest
   sufficient behavioural seam and ordinary reversion when it suffices.
3. Remove duplicated parent prose and sibling coverage. Confirm each acceptance
   ID has one owner and every slice passes the slice test.
4. Repeat only after a material reduction; stop when no justified reduction
   remains. Briefly report reductions or retained boundaries without adding an
   approval stage or ledger.

Preserve approved outcomes, constraints, and evidence requirements. Propose
disproportionate parent requirements as amendments via `write-specs`; do not
waive them in children. Seek reapproval when granularity or dependencies change;
detail changes within approved boundaries need no further approval. Use the
shared layout's existing-authority exception for implementation-only reslicing
during an authorized build.

## Acceptance Ownership

Give every parent acceptance ID exactly one owning slice. A regression check
may appear in several plans, but one slice owns the underlying behaviour. Do
not leave orphaned IDs or let sibling plans silently share ownership. A slice
may own several criteria only when they prove one cohesive outcome.

Save the decomposition manifest beside its parent at its current stage:

```text
plans/specs/<stage>/<spec_slug>/<spec_slug>.slices.md
```

The map moves with its parent. Only `Slice Map Status: approved` authorizes
builds; delivery tracking belongs in the release manifest and parent rollup.
Include:

```text
| Acceptance ID | Owning slice |
| Slice | Outcome | Blocked by | Verification boundary | Rollback boundary | Exclusions |
```

Use slugs, not stage-dependent paths; locate children under `plans/slices/<stage>/`.
Approved maps cannot retain draft or superseded owners. Material parent changes
make the map stale and block builds until reapproval under the shared rules.

## Child Plans

Create each child at:

```text
plans/slices/draft/<slice_slug>/<slice_slug>.md
```

Use a unique lowercase `snake_case` slug of at most 40 characters across current
and legacy stages. Reuse existing plans and preserve history and delivery
progress. Apply the shared approval, revision, and move rules. Each child needs:

- slice lifecycle status, approval status, parent path, map path, and slice slug;
- the single outcome and relevant problem evidence;
- owned acceptance IDs and observable acceptance conditions;
- affected capability and sibling-owned exclusions;
- demonstrated dependency and intended branch target;
- release, disable, removal, or rollback boundary;
- inherited binding decisions and explicitly authorized complexity;
- sufficient agent-run behavioural checks, with human or external acceptance
  only when required; and
- required new or modified database objects, when applicable, at the same
  precision as the parent spec.

Include only parent context, decisions, criteria, and verification needed for
this slice. Omit inapplicable topics or write `none`; do not invent work to fill
a template. Theme cleanup, migration, and other supporting work belong to the
slice requiring them, not separate horizontal plans.

## Wide Changes And Prefactoring

Do not create a shared abstraction merely because several future slices might
use it. A prefactor is a separate prerequisite only when current evidence shows
it is necessary, behaviour-preserving, independently verifiable, and narrower
than embedding it in the first slice.

For a genuinely inseparable wide mechanical migration, use
expand-migrate-contract: add the new form compatibly, migrate bounded groups
while keeping the repository valid, then remove the old form. Declare every
blocking edge. Do not use this exception for provider integrations, lifecycle
coordination, or speculative shared frameworks.

## Superseded Slices

Apply the shared supersession rules: record authorized replacements and reason,
draft replacement files, revise ownership and blocker links, and approve the
map and plans before retiring the old slice. Preserve history and evidence;
superseded slices never count as fulfilled. Existing build authority may cover
implementation-only replacements.

## Verification and Handoff

Before approval, finish trimming and verify saved drafts, unique acceptance
ownership, justified blockers, sibling exclusions, and the slice test. Report
absolute paths; leave unapproved children in `draft/`.

After approval, verify parent, map, and child metadata, moved paths, and repaired
references. Reconcile and report the parent stage. Backlog children still need
plan review before `build-branch-stack` selects them.
