# GitHub Change Request Adapter

Implement `change-request-lifecycle.md` for GitHub pull requests (PRs).

Before each `gh` command, load the bundled PATH setup:

```bash
eval "$("$orchestration_skill_root/scripts/ensure_forge_cli.sh" github)"
```

Require `gh auth status` to succeed. Resolve the authenticated login with
`gh api user --jq .login`. Inspect repository capabilities with:

```bash
gh repo view --json squashMergeAllowed,deleteBranchOnMerge
```

GitHub exposes squash as a repository capability, not a per-PR setting. Require
`squashMergeAllowed == true`; report `deleteBranchOnMerge` without changing it.

## Create Draft

Require `gh pr list --head "<branch-name>" --state open --json number` to return
no PR, then compose metadata with `change-request-description.md` and run:

```bash
gh pr create \
  --draft \
  --head "<branch-name>" \
  --base "<target-branch>" \
  --title "<title>" \
  --body "<description>" \
  --assignee "@me"
```

## Refresh Or Change Readiness

Refresh metadata with `gh pr edit <number> --title "<title>" --body
"<description>"`. Return a PR to draft with `gh pr ready <number> --undo`.
Mark it ready with `gh pr ready <number>`, then request review with
`gh pr edit <number> --add-reviewer "<independent-reviewer>"`.

After each action, query the PR with:

```bash
gh pr view <number> \
  --json number,url,state,isDraft,headRefName,headRefOid,baseRefName,baseRefOid,assignees,reviewRequests
```

Require the normalized lifecycle invariants. Report the PR number and URL,
draft state, source and target SHAs, assignee, reviewer, squash capability, and
source-branch deletion policy.
