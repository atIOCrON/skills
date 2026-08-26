---
name: plan-rank
description: Review and rank remaining plans by best implementation order. Use when asked to inspect plans/, compare ease, dependencies, risk, or sequencing, and present an implementation order without changing code.
metadata:
  layer: capability
---

# Plan Ranking

Rank remaining `plans/` work for implementation order. Read-only unless the user explicitly asks for edits.

## Scope

- Include root-level `plans/*.md` that are not clearly completed.
- Exclude `plans/done/`, artefact/review folders, and generated outputs.
- If completion status is ambiguous, note it instead of guessing silently.

## Method

1. Read `AGENTS.md` and relevant docs, especially project brief, standards, data flow, quality gates, and any docs named by the plans.
2. Inventory candidate plans with read-only commands such as `find`, `rg`, and targeted file reads.
3. For each plan, assess:
   - Dependencies: required predecessors, shared files, schema/data flow prerequisites.
   - Ease: size, locality, clarity, implementation complexity.
   - Risk: blast radius, data correctness impact, migration/backfill concerns.
   - Verification cost: tests, fixtures, Docker/pipeline checks likely needed.
   - Strategic value: whether it unlocks later plans or removes recurring friction.
4. Sort by dependency order first, then easiest/lowest-risk among currently unblocked plans.
5. Check `git status --short`; mention dirty-worktree caveats only if they affect confidence.

## Output

Keep concise and direct:

- Start with a ranking table using exactly these columns:
  - Rank
  - Plan
  - Ease
  - Dependency Notes
- Rank is the recommended implementation order.
- Ease should be a short label such as Easy, Medium, Hard, or Very hard.
- Dependency Notes should explain prerequisites, blockers, grouping, deferral, or "None" in one concise phrase.
- After the table, add only brief notes for plans that should be grouped, split, deferred, or spiked first.

Do not edit code, plans, or docs. Do not run long pipelines unless the user asks.
