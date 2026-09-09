# Plans Layout

- Active plans live at `plans/<plan_slug>.md`.
- Completed plans move to `plans/done/`.
- Review artefacts for a plan live in `plans/<plan_slug>.reviews/`, which
  contains:
  - `plan-review-pass<N>/` directories, one per plan-review pass;
  - `code-review-pass<N>/` directories, one per code-review pass;
  - `code-review-triage-ledger.md`, the cross-pass triage ledger.
- One-off scripts and execution helpers live in `plans/<plan_slug>.execution/`.
  Keep permanent tests and tooling in their normal repo locations.
- Small test outputs, measurements, and comparisons live in
  `plans/<plan_slug>.evidence/`. Maintain `index.md` there with the tested commit
  and worktree state, commands, results, and relative links to evidence and helpers.
- Give each worker or run distinct subdirectories; create them as needed.
- Keep protected inputs, large databases, dumps, and bulk outputs outside
  artefact folders. Retain concise summaries or small excerpts; record external
  paths and reproduction commands in the index.
- Preserve all three folders, when present, in the user's main checkout before
  removing a worktree.

## Plan Slug Format

Plan slugs are lowercase snake_case built from durable repo terms. Avoid
dates, agent names, and vague words. Examples from `plans/`:

- `catalog_relationship_ownership`
- `valid_gtin_quality_gate`
