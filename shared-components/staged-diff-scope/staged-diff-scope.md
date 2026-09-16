# Staged Commit Scope

Prepare one exact candidate tree for commit. This is a scope and self-review
gate, not the authoritative code review.

## Inputs

Require:

- repository root;
- plan path;
- intended file paths or module ownership list;
- reason: `initial-candidate`, `post-fix-candidate`, or
  `staged-changes-entry`.

## Workflow

1. Run `git status --short`.
2. Identify unrelated dirty and untracked files.
3. Stage only intended implementation files and accepted fix files with explicit
   `git add <path>` commands.
4. Run `git diff --cached --name-only`.
5. Stop if staged files include paths outside the intended scope.
6. Stop if any staged path also has unstaged edits. The committed, tested, and
   reviewed content must not differ.
7. Inspect `git diff --cached --stat`, `git diff --cached`, and
   `git diff --cached --check`.
8. Record the candidate tree with `git write-tree`.

## Scope Rules

- Leave unrelated dirty files unstaged.
- Do not use broad `git add .`.
- Do not revert or clean files.
- Do not stage plan-stage moves or review, execution, or verification artefacts
  unless the plan includes them.
- Do not use the index as the formal review boundary. Commit the approved tree,
  then review the pinned commit against its pinned dependency-parent SHA.

## Output

Report:

- staged file list;
- unrelated dirty file list;
- staged diff stat;
- candidate tree SHA;
- scope status: `in-scope` or `blocked`;
- blocker reason when blocked.
