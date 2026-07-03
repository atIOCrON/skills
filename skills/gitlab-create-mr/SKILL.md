---
name: gitlab-create-mr
description: Create a GitLab merge request with glab for an already-pushed branch, targeting a caller-supplied target branch (default develop), assigning and requesting review from the authenticated GitLab user, and enabling source branch deletion on merge.
compatibility: Requires git, glab, and jq with GitLab authentication
metadata:
  layer: runner
---

# GitLab Create MR

Create a GitLab GUI-visible merge request using `glab`. Do not commit, push, or edit files.

Defaults:

- Target branch `<target-branch>`: `develop` unless the caller supplies one.
  Stack mode passes the stack parent branch (see
  `.agents/skills/orchestration-conventions/references/stacked_mrs.md`); do
  not infer a non-default target.
- Assignee: authenticated GitLab username
- Reviewer: authenticated GitLab username
- Merge option: remove source branch when merged

## Preflight

A child process cannot change this shell's PATH, so begin every shell
invocation that runs `glab` with
`eval "$(.agents/skills/gitlab-create-mr/scripts/ensure_glab.sh)"`; the script
resolves `glab` and `jq` for non-interactive shells that did not load the
user's profile. Then run:

```bash
eval "$(.agents/skills/gitlab-create-mr/scripts/ensure_glab.sh)"
glab auth status
git branch --show-current
git status --short
git rev-parse --abbrev-ref --symbolic-full-name @{u}
git rev-list --left-right --count @{u}...HEAD
```

Stop if `ensure_glab.sh` reports an error, `glab` is unauthenticated, the current branch is `<target-branch>`, the branch has not been pushed, or `@{u}...HEAD` is not `0 0`.

Resolve the GitLab username:

```bash
eval "$(.agents/skills/gitlab-create-mr/scripts/ensure_glab.sh)"
username="$(glab api user | jq -r '.username')"
test -n "$username" && test "$username" != "null"
```

## Inputs

Inspect the pushed branch against `<target-branch>`. Stop if the target
branch cannot be fetched or resolved:

```bash
git fetch origin <target-branch>
git log --oneline origin/<target-branch>..HEAD
git diff --stat origin/<target-branch>...HEAD
git diff --name-only origin/<target-branch>...HEAD
```

Dirty worktree changes are allowed when unrelated because `glab mr create` uses pushed branch refs, not unstaged files. Check for overlap:

```bash
comm -12 \
  <({ git diff --name-only; git ls-files --others --exclude-standard; } | sort -u) \
  <(git diff --name-only origin/<target-branch>...HEAD | sort -u)
```

If dirty/untracked files overlap with branch diff files or would affect MR metadata generation, ask whether to continue. If they do not overlap, proceed and mention the unrelated local changes in the final response.

Check for an existing merge request for the source branch, with any target:

```bash
eval "$(.agents/skills/gitlab-create-mr/scripts/ensure_glab.sh)"
glab mr list --source-branch "<branch-name>"
```

Stop if an MR already exists; if its target branch differs from the requested
`<target-branch>`, report both targets in the blocker.

Compose the title and description with
`.agents/skills/gitlab-mr-description/SKILL.md`, passing `<target-branch>` as
its target branch.

## Workflow

Create the merge request:

```bash
eval "$(.agents/skills/gitlab-create-mr/scripts/ensure_glab.sh)"
glab mr create \
  --source-branch "<branch-name>" \
  --target-branch "<target-branch>" \
  --title "<title>" \
  --description "<description>" \
  --assignee "<gitlab-username>" \
  --reviewer "<gitlab-username>" \
  --remove-source-branch \
  --yes
```

Prefer explicit title and description over `--fill`.

## Final Response

Report the source branch, target branch, merge request URL, assignee,
reviewer, and remove-source-branch setting. After successful creation, emit the required `::git-create-pr` directive with the MR URL, branch, cwd, and `isDraft=false`.
