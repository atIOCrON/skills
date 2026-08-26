---
name: plan-create
description: Create a final implementation plan in plans/ from an idea, discussion, or prompt. Use when the user asks to create/write/draft a plan, especially after saying "Create a plan". Ask and resolve blocking questions before writing. Not for reviewing or implementing an existing plan; use plan-review or plan-implement for those.
metadata:
  layer: capability
---

# Plan Create

Create one final Markdown plan under `plans/`. The plan is a standalone implementation contract, not a chat recap.

## Read First

- Use `AGENTS.md` as the docs index and read the relevant `docs/*.md` for the plan scope.
- Inspect the current code and all likely in-repo readers affected by the change.
- Do not inspect existing plans for background context. Read a prior plan only when the user names it, asks to continue it, or the new plan explicitly depends on it.

## Before Writing

- Resolve all material questions with the user before creating the plan.
- Choose a filename `plans/<plan_slug>.md` using the plan slug format defined
  in `.agents/skills/orchestration-conventions/references/plans_layout.md`.
- If the idea conflicts with current code or repo standards, resolve the conflict first.

## Plan Rules

- Write the plan as final instructions: "Do X, Y, and Z."
- Reference only current docs, current code, and files the implementer should touch.
- Do not reference deprecated plans, deprecated code, old architecture, rejected alternatives, or chat decisions.
- Do not write "we decided", "instead of", "not doing", or similar history.
- Do not leave open questions, placeholders, TODOs, or optional implementation branches.
- Include verification that can be run by the implementer.
- Verification must be deterministic and practical for the orchestration loop,
  preferably completing within about 5 minutes. If full validation is slower or
  flaky, include a fast smoke verification in the plan and place the full suite
  outside the loop.

## Suggested Shape

```markdown
# <Plan Title>

## Goal
<final outcome>

## Current State
<only current, verified facts>

## Implementation
<ordered, concrete steps>

## Contract Propagation
<schemas, readers, CLI flags, views, exports, docs, or configs that must change together>

## Edge Cases And Failure Semantics
<empty, duplicate, stale, partial-failure, rerun, ordering, and scale behavior>

## Rebuild Or Migration
<required rebuild, migration, backfill, or why none is needed>

## Files To Change
<paths and expected changes>

## Verification
<commands or checks>

## Out Of Scope
<only boundaries the implementer must respect>
```
