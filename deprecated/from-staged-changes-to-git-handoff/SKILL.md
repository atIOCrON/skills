---
name: from-staged-changes-to-git-handoff
description: Run already implemented intended changes through verification, staged-diff code review, and final handoff. Use when code changes already exist and the desired outcome is ready for git branch/commit/push.
metadata:
  layer: runner
---

# From Staged Changes To Git Handoff

Review and verify already implemented changes until they are ready for git
handoff.

## Inputs

Require:

- plan path or approved implementation intent;
- intended file paths or module ownership list;
- staged changes, or enough scope to stage intended files safely.

Ask only if the plan/intent or intended staged-diff scope is missing.

## Route

Ledger, material, and artefact terms are defined in
.agents/skills/orchestration-conventions/SKILL.md.

1. Load `AGENTS.md`, the plan or approved intent, and relevant docs named by
   `AGENTS.md`.
2. Use `.agents/skills/verification-runner/SKILL.md`.
3. Use `.agents/skills/staged-diff-scope/SKILL.md`.
4. Use `.agents/skills/reviewer-preflight/SKILL.md` for claude and for
   cursor.
5. Use `.agents/skills/code-review-loop/SKILL.md`.
6. Use `.agents/skills/orchestration-final-handoff/SKILL.md` for git handoff.

## Stop Conditions

- Ownership scope is insufficient.
- Intended staged-diff scope is unclear or includes unrelated files.
- Verification remains blocked after allowed repair attempts.
- Reviewer preflight fails for Claude Code or Cursor.
- Code review has unresolved material ledger entries, contradictions, accepted
  fixes, or recurring escalations.

## Output

Report:

- plan path or approved intent;
- staged files;
- verification status;
- code-review pass outcomes;
- triage ledger path and terminal-status counts;
- blocker or `Ready for git handoff`;
- next skill: `.agents/skills/git-branch-commit-push/SKILL.md`.
