# Plans Layout

Broad feature specifications and executable vertical-slice plans have separate
lifecycles:

```text
plans/specs/<spec_slug>/<spec_slug>.md
plans/specs/<spec_slug>/<spec_slug>.slices.md
plans/<stage>/<slug>/<slug>.md
plans/<stage>/<slug>/<slug>.reviews/
plans/<stage>/<slug>/<slug>.execution/
plans/<stage>/<slug>/<slug>.evidence/
plans/releases/<release-id>/manifest.json
```

A specification defines the complete outcome and stable acceptance IDs. Keep it
at this path; record its lifecycle inside the document as `draft`, `approved`,
`fulfilled`, or `superseded`. Only an `approved` specification may be sliced or
built. Delivery progress is derived from its child plans, not from an
`in_progress` specification state.

The `.slices.md` file is the approved decomposition manifest. It gives every
acceptance ID one owning slice and records each slice's outcome, blockers,
verification boundary, rollback boundary, and exclusions. It uses slice slugs,
not stage-dependent paths, and does not duplicate branch, plan-stage, release,
or deployment state. Its `Slice Map Status` is `approved` or `stale`.
Specifications and slice maps never move through stage directories and are not
branch implementation inputs.

A material change to an approved or fulfilled specification returns it to
`draft` and makes its slice map `stale`. Clarifications that preserve acceptance
IDs, scope, binding decisions, authorized complexity, and external acceptance
retain status. After reapproval, revise the decomposition and obtain user
approval before restoring the slice map to `approved`.

During an authorized build, an implementation-only split that preserves the
approved outcome, acceptance ownership, exclusions, release scope, and external
acceptance is a clarification. Record its reason and revised rollback and
verification boundaries; the specification and slice map remain `approved`.

Each staged feature is one approved vertical slice. Its directory and plan
filename share a lowercase `snake_case` slug. The plan references its parent
specification and approved slice map, owns a cohesive set of acceptance IDs,
excludes sibling outcomes, and has an independent verification and rollback
boundary.
An explicitly classified legacy plan may stand alone only after it passes the
same cohesion check.

Stages are `backlog`, `to_do`, `in_progress`, `review`, and `done`. Use the
feature's current directory as `<feature_dir>` in other references. Move the
whole directory at a stage transition; never move the plan without its
artefacts, merge it into an existing destination, or move it while a worker or
reviewer is using its old path. Resolve the new plan and artefact paths before
the next step, and refresh any handoff or manifest references. Create stage
directories as needed. Keep links within a feature relative to its directory
so stage moves preserve them.

Release manifests live outside feature stage directories so plan moves do not
move the release source of truth. Keep branch order, targets, SHAs, checks,
acceptance, CRs, integration, and deployment state in the canonical JSON
manifest. Treat spreadsheets and prose summaries as generated or reconciled
views, not competing authorities.

- `backlog`: a newly written plan, not yet selected for implementation.
- `to_do`: a reviewed plan selected for the current implementation batch.
  Move only selected plans from `backlog`.
- `in_progress`: implementation, fixes, CLI code review loops, commits,
  and required branch checks are underway, or a defect needs an implementation
  fix. Keep a slice here through proportionate trim and clean correctness
  reviews or the five-pass cap. Finish accepted cap remediation and closure;
  record unresolved findings. Do not wait for ancestor reviews or descendants
  to finish this slice's review passes.
- `review`: the slice's implementation and trim are complete, and correctness
  passes are clean or capped. At entry, its committed, pushed tip passes exact-tip
  verification; trim is proportionate; correctness reviews are clean or the
  five-pass cap is reached. Record `review_handoff` on that SHA and preserve
  artefacts. A capped slice may await human disposition here. Ancestors may
  still be `in_progress/`, and unfinished descendants do not hold this move.
  Keep the slice here through routine restacks, pending current-tip checks,
  review mappings, human acceptance, and external or release-candidate checks.
  A changed ancestor requires restack and re-verification before release
  progression, but does not undo completed implementation. Return to
  `in_progress/` when a defect, failed check, or behavioral change requires
  implementation work. Record pending external checks with owners and
  procedures, and deferred candidate checks with prerequisites.
- `done`: every final human or external acceptance check passed or its limitation
  was explicitly accepted by an authorized decision maker. A review-cap human
  disposition alone does not satisfy this final acceptance gate. The change request
  must also be merged and its landed commit confirmed. Move the feature here
  after those conditions are met and update recorded paths.

For repair runs, return only slices needing implementation work to
`in_progress/`. Restack and re-verify affected descendants in their current
stage unless they also need implementation work.
For features already in `done/` under the earlier stage convention, verify the
change request and acceptance evidence. Move features with pending acceptance
or unmerged change requests to `review/`; a failed acceptance check needing a
fix sends the feature to `in_progress/`.

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
