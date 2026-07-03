---
name: gitlab-post-merge-cleanup
description: 'Restore the local checkout after GitLab merge requests land: switch to the target branch, fast-forward it, prune remote-tracking refs, safely advance stale local branch refs to their merged rebased SHAs, and safe-delete merged local branches. Use after merging one or more merge requests or when asked to tidy local branches after merges. Local-only; never force-deletes branches or pushes.'
metadata:
  layer: capability
---

# GitLab Post-Merge Cleanup

Tidy the local checkout after merge requests land. Local-only: never push,
force-delete branches, or touch remote state beyond `git fetch --prune`.

## Inputs

- Target branch (default `develop`).
- Optional record file of `branch old_remote_sha rebased_head_sha` triples,
  one whitespace-separated triple per line, as written by
  `gitlab-merge-stack`. When no record file is supplied, no branch ref may be
  advanced and only branches whose heads are already ancestors of the target
  branch may be deleted. Standalone mode sweeps every such merged local
  branch, including long-lived ones; supply a record file when cleanup should
  touch only the just-merged stack.

## Workflow

Run from the user's checkout:

```bash
.agents/skills/gitlab-post-merge-cleanup/scripts/cleanup_merged_branches.sh <target-branch> [record-file]
```

The script:

1. Switches to the target branch, fast-forwards it with
   `git pull --ff-only`, and prunes remote-tracking refs.
2. With a record file: for each recorded branch, advances the local branch
   ref to the recorded `rebased_head_sha` only when the local branch still
   equals the recorded `old_remote_sha` and the rebased head SHA is already
   merged into the target branch, then safe-deletes the branch with
   `git branch -d`.
3. Without a record file: never advances any branch ref, and safe-deletes
   only local branches whose heads are already ancestors of the target
   branch.
4. Reports a per-branch outcome: `advanced`, `deleted`, or `skipped` with a
   reason.

## Rules

- Never stash, revert, or delete user work. If switching to the target branch
  fails because of local modifications, stop and report the blocker with the
  current branch, the dirty files, and the exact commands the user can rerun
  after moving their local work.
- Use `git branch -d` only; never `git branch -D`.
- Skip and report branches with local-only commits, mismatched SHAs, or
  checkouts in other worktrees.

## Output

Report the target-branch restore status and every per-branch outcome,
including each skipped branch and its reason.
