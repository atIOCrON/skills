---
name: from-task-brief-to-git-handoff
description: 'Take a user task brief end to end: reviewed plan, implementation, verification, staged-diff code review, and final git handoff readiness. Use when the user provides a task brief and wants the full pipeline without intermediate handoffs.'
metadata:
  layer: runner
---

# From Task Brief To Git Handoff

Run the full route from task brief to git handoff by composing the two primary
route skills.

## Inputs

Require:

- task brief;
- plan slug or enough context to choose one.

Ask only if the task brief is missing or the slug cannot be chosen safely.

## Route

1. Use `.agents/skills/from-task-brief-to-reviewed-plan/SKILL.md`.
2. If the reviewed-plan route ends with `Ready for implementation`, use
   `.agents/skills/from-reviewed-plan-to-git-handoff/SKILL.md`.

## Stop Conditions

Stop when either composed route reports a blocker or requires a user decision.

## Output

Report:

- plan path;
- reviewed-plan route outcome;
- git-handoff route outcome when run;
- blocker or `Ready for git handoff`;
- next skill: `.agents/skills/git-branch-commit-push/SKILL.md` when ready.
