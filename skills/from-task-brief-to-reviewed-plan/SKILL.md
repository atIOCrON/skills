---
name: from-task-brief-to-reviewed-plan
description: Run a task brief through plan creation and plan review only. Use when starting from a user task brief and the desired outcome is a reviewed plans/ file ready for implementation.
metadata:
  layer: runner
---

# From Task Brief To Reviewed Plan

Turn a task brief into a reviewed plan. This route stops before code
implementation.

## Inputs

Require:

- task brief;
- plan slug or enough context to choose one.

Ask only if the task brief is missing or the slug cannot be chosen safely.

## Route

1. Load `AGENTS.md`, the project overview doc named by AGENTS.md, and
   relevant docs named by `AGENTS.md`.
2. Use `.agents/skills/plan-create/SKILL.md` to create `plans/<slug>.md`.
3. Use `.agents/skills/reviewer-preflight/SKILL.md` for claude and for
   cursor.
4. Use `.agents/skills/plan-review-loop/SKILL.md`.
5. Use `.agents/skills/orchestration-final-handoff/SKILL.md` for the reviewed
   plan handoff.

## Stop Conditions

- Planning needs material user answers.
- Reviewer preflight fails for Claude Code or Cursor.
- Plan review stops on unresolved findings, contradictions, or user decisions.

## Output

Report:

- plan path;
- plan-review pass outcomes;
- reviewer artifact paths;
- blocker or `Ready for implementation`;
- next route: `.agents/skills/from-reviewed-plan-to-git-handoff/SKILL.md`.
