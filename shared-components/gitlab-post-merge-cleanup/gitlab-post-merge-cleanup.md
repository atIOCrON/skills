# GitLab Post-Merge Cleanup

Tidy the local checkout after merge requests land. Local-only: never push,
force-delete branches, or touch remote state beyond `git fetch --prune`.

## Inputs

- Target branch (default `develop`).
- Optional record file of
  `branch old_remote_sha rebased_head_sha landed_sha` quadruples, one
  whitespace-separated record per line, as written by the squash-aware
  merge-stack workflow. Legacy triples remain accepted for non-squash merges
  and treat `rebased_head_sha` as `landed_sha`. When no record file is supplied,
  no branch ref may be advanced and only branches whose heads are already
  ancestors of the target branch may be deleted. Standalone mode sweeps every
  such merged local branch, including long-lived ones; supply a record file
  when cleanup should touch only the just-merged stack.

## Workflow

Run from the user's checkout. If it is dirty, first record the branch and
status, then stash staged, tracked, and untracked changes with a unique message;
record the stash OID and verify the checkout is clean. Do not create a stash
when the checkout is already clean.

Then run:

```bash
scripts/cleanup_merged_branches.sh <target-branch> [record-file]
```

The script:

1. Switches to the target branch, fast-forwards it with
   `git pull --ff-only`, and prunes remote-tracking refs.
2. With a record file: for each recorded branch, verifies that the landed
   commit is in the target branch and, for squash merges, has the same tree as
   `rebased_head_sha`. It advances the local branch ref to `landed_sha` only
   when the local branch still equals `old_remote_sha`, then safe-deletes the
   branch with `git branch -d`.
3. Without a record file: never advances any branch ref, and safe-deletes
   only local branches whose heads are already ancestors of the target
   branch.
4. Reports a per-branch outcome: `advanced`, `deleted`, or `skipped` with a
   reason.

Return to the original branch when it still exists and remains appropriate;
otherwise use the target branch. If the workflow rebased that branch, align it
only through the recorded-SHA safeguards above. Apply the recorded stash OID
with its index state, verify the saved changes were restored, then locate and
drop only the stash entry with that OID.

## Rules

- Never revert or delete user work, and never disturb pre-existing stashes. If
  cleanup, branch restoration, or stash restoration fails or conflicts, stop
  with the temporary stash intact and report the current branch, affected
  files, stash OID, and recovery commands.
- Use `git branch -d` only; never `git branch -D`.
- Skip and report branches with local-only commits, mismatched SHAs, or
  checkouts in other worktrees.

## Output

Report the target-branch and temporary-stash restore status and every per-branch
outcome, including each skipped branch and its reason.
