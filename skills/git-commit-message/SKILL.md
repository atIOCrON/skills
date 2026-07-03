---
name: git-commit-message
description: 'Compose a commit message from the staged diff: imperative subject under about 72 characters, a blank line, then what/why/impact/verification body lines. Use when asked to write or compose a commit message. Read-only; does not stage, branch, commit, or push; use git-branch-commit-push for that.'
metadata:
  layer: capability
---

# Git Commit Message

Compose a commit message from the staged diff. Read-only: do not stage,
branch, commit, push, or edit files.

## Workflow

1. Run `git diff --cached --stat`.
2. Run `git diff --cached`.
3. Stop with a clear message if nothing is staged.
4. Compose an imperative subject under about 72 characters.
5. Add a blank line, then body lines for what changed, why, impact, and
   verification.

Example:

```text
Update comparison delta ownership

What: Move delta field ownership into the comparison module.
Why: Keep comparison contracts close to the code that consumes them.
Impact: Export delta behavior is unchanged; ownership is easier to audit.
Verification: python -m pytest tests/ -q
```

## Output

Return only the commit message subject and body. Do not include git commands.
