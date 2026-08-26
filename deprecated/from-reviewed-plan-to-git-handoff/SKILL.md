---
name: from-reviewed-plan-to-git-handoff
description: Run a reviewed plans/ file through implementation, verification, staged-diff code review, and final handoff. Use when the plan is already approved or reviewed and the desired outcome is ready for git branch/commit/push.
metadata:
  layer: runner
---

# From Reviewed Plan To Git Handoff

Implement a reviewed plan and run staged-diff code review until the work is
ready for git handoff.

## Inputs

Require:

- reviewed or approved `plans/<slug>.md`;
- implementation ownership scope, or enough plan context to derive one.

Ask only if the plan path or implementation ownership scope is missing.

## Route

Ledger, material, and artefact terms are defined in
.agents/skills/orchestration-conventions/SKILL.md.

1. Load `AGENTS.md`, the plan, and relevant docs named by `AGENTS.md`.
2. Use `.agents/skills/implementation-dispatch/SKILL.md` for initial
   implementation.
3. Use `.agents/skills/verification-runner/SKILL.md`.
4. Use `.agents/skills/staged-diff-scope/SKILL.md`.
5. Use `.agents/skills/reviewer-preflight/SKILL.md` for claude and for
   cursor.
6. Use `.agents/skills/code-review-loop/SKILL.md`.
7. Use `.agents/skills/orchestration-final-handoff/SKILL.md` for git handoff.

## Stop Conditions

- Ownership scope is insufficient.
- Intended staged-diff scope is unclear or includes unrelated files.
- Verification remains blocked after allowed repair attempts.
- Reviewer preflight fails for Claude Code or Cursor.
- Code review has unresolved material ledger entries, contradictions, accepted
  fixes, or recurring escalations.

## Output

Report:

- plan path;
- changed files;
- verification status;
- code-review pass outcomes;
- triage ledger path and terminal-status counts;
- blocker or `Ready for git handoff`;
- next skill: `.agents/skills/git-branch-commit-push/SKILL.md`.
