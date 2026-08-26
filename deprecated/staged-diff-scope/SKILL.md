---
name: staged-diff-scope
description: Staging and review-scope guard skill. Use before staged-diff code review to stage only intended implementation files or accepted fixes, preserve unrelated dirty work, and confirm the cached diff is in scope.
metadata:
  layer: capability
---

# Staged Diff Scope

Scope guard for staged-diff review workflows.

## Inputs

Require:

- repository root;
- plan path;
- intended file paths or module ownership list;
- reason: `initial-review`, `post-fix-review`, or `staged-changes-entry`.

## Workflow

1. Run `git status --short`.
2. Identify unrelated dirty and untracked files.
3. Stage only intended implementation files and accepted fix files with explicit
   `git add <path>` commands.
4. Run `git diff --cached --name-only`.
5. Stop if staged files include paths outside the intended scope.
6. Run `git diff --cached --stat` and keep the output for the review handoff.
7. If a staged file also has unstaged edits, note it and use staged-content
   inspection commands such as `git show :<path>` in later review/triage.

## Scope Rules

- Leave unrelated dirty files unstaged.
- Do not use broad `git add .`.
- Do not revert or clean files.
- Do not stage review artifacts unless the user explicitly includes them in the
  implementation scope.

## Output

Report:

- staged file list;
- unrelated dirty file list;
- staged diff stat;
- scope status: `in-scope` or `blocked`;
- blocker reason when blocked.
