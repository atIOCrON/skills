# Post-Merge Cleanup

Local cleanup is optional and never determines merge success. It is local-only:
never push, force-delete branches, or touch remote state beyond fetch and prune.

## Inputs

- Remote (default `origin`) and target branch (default `develop`).
- Required record file of
  `branch old_remote_sha rebased_head_sha landed_sha` quadruples, one
  whitespace-separated record per line, as written by the squash-aware
  merge-stack workflow. Legacy triples remain accepted for non-squash merges
  and treat `rebased_head_sha` as `landed_sha`.
- Mode: `local-if-clean` (default) or `none` (explicit override).

## Workflow

For `none`, stop and leave the checkout untouched. For `local-if-clean`, run
cleanup when the original checkout is clean; otherwise skip it and leave that
checkout untouched. This workflow never creates, applies, or drops a stash.

Then run:

```bash
scripts/cleanup_merged_branches.sh <remote> <target-branch> <record-file>
```

The script:

1. Switches to the target, fast-forwards it from the selected remote, and
   prunes that remote's tracking refs.
2. For each recorded branch, verifies that the landed
   commit is in the target branch and, for squash merges, has the same tree as
   `rebased_head_sha`. It advances the local branch ref to `landed_sha` only
   when the local branch still equals `old_remote_sha`, then safe-deletes the
   branch with `git branch -d`.
3. Reports a per-branch outcome: `advanced`, `deleted`, or `skipped` with a
   reason.

## Rules

- Never revert or delete user work, and never disturb pre-existing stashes. If
  cleanup fails, report the current branch and affected files.
- Use `git branch -d` only; never `git branch -D`.
- Skip and report branches with local-only commits, mismatched SHAs, or
  checkouts in other worktrees.
- Never escalate from `local-if-clean` to stashing.

## Output

Report the target branch and every per-branch outcome, including each skipped
branch and its reason.
