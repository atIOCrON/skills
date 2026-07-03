---
name: plan-review
description: Review one plans/ file for correctness, docs/ conformance, and data-engineering best practice. Use when asked to review/check/critique a plan. Requires a plan path. Do not edit. Not for running the multi-pass review loop; use plan-review-loop for that.
metadata:
  layer: capability
---

# Plan Review

Review one plan under `plans/`. Report issues only; do not edit the plan or code. If no plan path is provided, ask.

## Read

Always read:

- The named plan, end to end.
- Every cited `file:line`; wrong or stale claims are blockers.
- the docs AGENTS.md labels as code standards and as the project overview and
  architecture briefing

Then read relevant `docs/*.md` using the index in `AGENTS.md`.

Scan `plans/` and `plans/done/` for related or conflicting plans.

## Lenses

Apply both: `docs` for repo standards, and `best-practice` for mature data-engineering expectations even when docs are silent.

Best-practice checks include idempotency, raw/Bronze immutability, replay/backfill, schema-reader propagation, deterministic keys, lineage, declarative validation, observability, soft deletes for entities, scale sensitivity, batch boundaries, failure semantics, and verification. Do not ask for compatibility shims or deprecation paths; this repo forbids them.

## Check

Assess:

- current-code claims and line references
- problem statement and root cause
- approach soundness under both lenses
- scope and in-repo contract propagation
- dependencies on other plans
- migration or rebuild story
- verification plan
- empty input, duplicate input, stale input, partial failure, rerun, scale, and ordering assumptions
- clarity only when ambiguity affects implementation

Severity: `blocker` for false premises, bugs, unsafe design, missing verification, or standards conflict; `should-fix` for clear weaknesses; `nit` for minor clarity issues.

## Output

Every finding must cite the plan location and either a doc section, code line, or named best-practice principle. Include at least one best-practice consideration even if it is an explicit affirmation.

Use the supplied reviewer slug to create stable finding IDs in the
plan-review format defined in
`.agents/skills/orchestration-conventions/references/finding_ids.md`. If a
section has no findings, write exactly `- None`.

Use only the current plan, cited docs, current code, and command output you
inspect yourself. Do not use findings, summaries, or conclusions from previous
passes. Do not edit files, run destructive commands, change branches, commit,
push, access credentials, or inspect unrelated private files.

```markdown
## Summary
<one paragraph proving you understood the plan>

## Blockers
- [{finding_id}] [plans/<name>.md:<line-or-section>] [docs|best-practice|bug] <finding> - Evidence: <citation> - Recommendation: <fix>

## Should-fix
- [{finding_id}] [plans/<name>.md:<line-or-section>] [docs|best-practice|bug] <finding> - Evidence: <citation> - Recommendation: <fix>

## Nits
- [{finding_id}] [plans/<name>.md:<line-or-section>] [docs|best-practice|bug] <finding> - Evidence: <citation> - Recommendation: <fix>

## Contradictions
- [{finding_id}] [plans/<name>.md:<line-or-section>] <docs/code/best-practice conflict> - Evidence: <evidence> - Recommendation: <resolution>

## Open questions
- [{finding_id}] [plans/<name>.md:<line-or-section>] <question> - Evidence: <why this affects implementation>

## Skill Feedback
- <non-blocking feedback about unclear instructions, output format, command friction, missing constraints, or confusing workflow>
```

If there is no skill feedback, write exactly `- None`.

Frame material questions as blockers when they affect implementation
correctness.

End with one:

- `Approve - ready for implementer`
- `Revise - address blockers and re-review`
- `Needs discussion`

Keep the report machine-actionable: no hedging, no implementation design unless the user asks, and no demands for new tests outside the repo's verification model.
