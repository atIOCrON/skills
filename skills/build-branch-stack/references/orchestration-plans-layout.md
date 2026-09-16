# Plans Layout

Each feature has one plan. Its directory and plan filename share a lowercase
`snake_case` slug:

```text
plans/<stage>/<slug>/<slug>.md
plans/<stage>/<slug>/<slug>.reviews/
plans/<stage>/<slug>/<slug>.execution/
plans/<stage>/<slug>/<slug>.evidence/
```

Stages are `backlog`, `to_do`, `in_progress`, `review`, and `done`. Use the
feature's current directory as `<feature_dir>` in other references. Move the
whole directory at a stage transition; never move the plan without its
artefacts, merge it into an existing destination, or move it while a worker or
reviewer is using its old path. Resolve the new plan and artefact paths before
the next step, and refresh any handoff or manifest references. Create stage
directories as needed. Keep links within a feature relative to its directory
so stage moves preserve them.

- `backlog`: a newly written plan, not yet selected for implementation.
- `to_do`: a reviewed plan selected for the current implementation batch.
  Move only selected plans from `backlog`.
- `in_progress`: implementation, code review, fixes, restacks, and final stack
  checks are underway. Keep the feature here throughout the code review loop.
- `review`: the branch passed code review and final stack checks and is ready
  for human review. Keep it here while its change request is open. Return it to
  `in_progress` if a fix or restack is needed.
- `done`: the change request was merged and its landed commit confirmed. Move
  the feature here after confirmation and update recorded paths.

For repair runs, move only affected features and descendants back to
`in_progress` when changes are needed. Leave unaffected features in place.
For features already in `done/` under the earlier stage convention, verify the
change request state and move unmerged features to `review/`.

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
