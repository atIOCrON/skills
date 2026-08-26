# Git Branch Commit Push

Automate local Git publication only. Do not edit files, stage files, or create a pull request.

Base branch `<base-branch>`: `develop` unless an orchestrating workflow supplies
one (stack mode passes the stack parent branch; see
`references/orchestration-stacked-mrs.md`).
Branch names must describe the change only: no tool, model, assistant,
`codex/`, `ai/`, or `bot/` references.

Allowed prefixes: `feature/`, `fix/`, `docs/`, `refactor/`, `chore/`.

Default to a fresh branch from a fresh `<base-branch>`. Continue on an
existing non-`develop` branch only when the user explicitly asks to continue
that branch in the current request.

## Preflight

Run:

```bash
git status --short
git branch --show-current
git diff --cached --stat
git diff --cached --name-only
git diff --name-only
git ls-files --others --exclude-standard
git diff --cached
```

If nothing is staged, stop.

Unstaged or untracked files are allowed when unrelated. Check overlap with staged files:

```bash
comm -12 \
  <({ git diff --name-only; git ls-files --others --exclude-standard; } | sort -u) \
  <(git diff --cached --name-only | sort -u)
```

If overlap exists, ask whether to continue. If no overlap exists, proceed and mention unrelated local changes in the final response.

## Workflow

1. If on a non-`develop` branch without an explicit caller-supplied
   `<base-branch>` and without the user explicitly asking to continue it,
   stop and report the current branch.

2. Fetch and prune remote refs:

```bash
git fetch --prune origin
```

3. Stop if the branch name already exists locally or on `origin`:

```bash
git show-ref --verify --quiet refs/heads/<branch-name>
git ls-remote --exit-code --heads origin <branch-name>
```

4. If creating a new branch, switch to `<base-branch>`, fast-forward it from
   origin, and create the new branch:

```bash
git switch <base-branch>
git pull --ff-only origin <base-branch>
git switch -c <branch-name>
```

   Stop if `<base-branch>` cannot be fetched, resolved, or fast-forwarded.

5. Compose the commit message with
   `references/git-commit-message.md`.

6. Commit only the staged changes:

```bash
git commit -m "<subject>" -m "<body>"
```

7. Push and set upstream:

```bash
git push -u origin <branch-name>
```

## Stop Conditions

Stop if switching branches or pulling would overwrite local work, dirty files overlap staged files, the branch name already exists, the commit fails, or the push fails.

## Final Response

Report the chosen base branch, the branch, commit hash, push result, and any unrelated uncommitted files left in the worktree. After successful actions, emit the required `::git-create-branch`, `::git-commit`, and `::git-push` directives.
