---
name: write-slices
description: Decompose approved specifications into proportionate vertical slices, trim unnecessary splits and checks, and maintain acceptance ownership and dependencies.
disable-model-invocation: true
metadata:
  layer: capability
---

# Write Slices

Turn one approved parent specification into branch-sized implementation plans.
Each plan must deliver a narrow, complete path through every affected layer and
leave the repository in a valid state.

Resolve paths against the user's primary checkout. Require the parent at
`plans/specs/<spec_slug>/<spec_slug>.md`. Migrate a legacy broad specification
through `write-specs` first. Read it, its evidence, relevant code and contracts,
and every acceptance ID before proposing slices. Require its `Specification
Status` to be `approved`; stop on `draft`, `fulfilled`, or `superseded`.

## Draft Before Writing

Use one slice when the outcome fits the slice test. Split only for concrete
implementation, release, or verification boundaries, not per file, layer,
acceptance ID, or planning phase.

Trim the decomposition, then seek approval of its granularity and dependencies
before creating files. For each slice show:

- slug and actor-visible or integration-visible outcome;
- owned acceptance IDs;
- genuine blockers, or `none`;
- independent verification and rollback boundary; and
- explicit exclusions.

Revise the draft until approved. Do not treat list order as dependency.

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
detail changes within approved boundaries need no further approval.

## Acceptance Ownership

Give every parent acceptance ID exactly one owning slice. A regression check
may appear in several plans, but one slice owns the underlying behaviour. Do
not leave orphaned IDs or let sibling plans silently share ownership. A slice
may own several criteria only when they prove one cohesive outcome.

Write the approved decomposition manifest to:

```text
plans/specs/<spec_slug>/<spec_slug>.slices.md
```

This file is the stable slice map, not a release manifest or a second status
tracker. Require a `Slice Map Status` section with value `approved`; only write
it after the user approves the decomposition. Include:

```text
| Acceptance ID | Owning slice |
| Slice | Outcome | Blocked by | Verification boundary | Rollback boundary | Exclusions |
```

Use slice slugs, not stage-dependent plan paths. Locate a slice's current state
by finding its slug under `backlog`, `to_do`, `in_progress`, `review`, or
`done`. Mark the slice map `stale` when the parent specification materially
changes; no mapped plan may start until the user approves a revised map.

## Child Plans

Create each child at:

```text
plans/backlog/<slice_slug>/<slice_slug>.md
```

Use a unique lowercase `snake_case` slug of at most 40 characters. Never
overwrite or move an existing plan. Each child plan must contain:

- parent specification path, slice-map path, and slice slug;
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

## Verification

Complete the planning trim loop, then check that the parent specification and
slice map are approved, every parent acceptance ID has exactly one owner,
every blocker is necessary, every child excludes sibling outcomes, and each
slice passes the slice test. Report the absolute paths of the specification,
slice map, and child plans. These plans still require review before
`build-branch-stack`.
