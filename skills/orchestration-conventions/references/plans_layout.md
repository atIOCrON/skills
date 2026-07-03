# Plans Layout

- Active plans live at `plans/<plan_slug>.md`.
- Completed plans move to `plans/done/`.
- Review artefacts for a plan live in `plans/<plan_slug>.reviews/`, which
  contains:
  - `plan-review-pass<N>/` directories, one per plan-review pass;
  - `code-review-pass<N>/` directories, one per code-review pass;
  - `code-review-triage-ledger.md`, the cross-pass triage ledger.

## Plan Slug Format

Plan slugs are lowercase snake_case built from durable repo terms. Avoid
dates, agent names, and vague words. Examples from `plans/`:

- `catalog_relationship_ownership`
- `valid_gtin_quality_gate`
