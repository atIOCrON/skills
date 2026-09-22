---
name: write-slices
description: Decompose an approved feature specification into independently verifiable vertical-slice plans and a stable acceptance/dependency map for branch implementation.
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

Present the proposed slices and ask the user to approve their granularity and
dependency graph before creating files. For each slice show:

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

Split when subsets have different providers or SDKs, lifecycle owners,
acceptance environments, rollback paths, or can fail while the rest remains
valid. Also split when grouping is the only reason to introduce a shared
coordinator. Sharing a page, package, release, or subsystem does not make
separate outcomes one slice.

Combine slices when neither can be deployed safely or demonstrated without the
other. Prefer independent safety and observability over a target ticket count.

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
- agent-run behavioural checks and separate human or external acceptance; and
- required database objects at the same precision as the parent spec.

Name the existing test facility each slice will extend, or state that no
permanent automated test is required and record the focused command or external
acceptance instead. Do not plan a new custom browser, runtime, provider,
package, or application harness unless the user explicitly approved that
harness by name. General approval of the specification or slice map does not
count. If a new harness appears necessary, present it as a separate decision
before writing approved child plans. Count test-support complexity in the
one-context slice test, and prefer one representative scenario over a field,
provider, or state matrix.

Do not copy the entire parent specification. Include only the context,
decisions, criteria, and verification needed to implement and review this
slice. Theme cleanup, migration, or other supporting work travels with the
slice whose behaviour requires it; do not create horizontal cleanup plans.

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

Check that the parent specification and slice map are approved, every parent
acceptance ID has exactly one owner, every blocker is necessary, every child
excludes sibling outcomes, and each slice passes the slice test. Report the
absolute paths of the specification, slice map, and child plans. These plans
still require review before `build-branch-stack`.
