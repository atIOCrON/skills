# Git Branch Commit

Create/adopt plan branches and commit approved trees; no push/CR. Base defaults
remote default; assigned verified authoring base may differ from final linear
predecessor. Only coordinator restacks/accepts. Name `<type>/<change-description>`
by purpose (feature/fix/docs/refactor/chore), never tools/models/bots.

## Start and commit

1. Inspect status/current branch; fetch/prune origin. Resolve/pin parent locally;
   if on origin require local equals fetched tip (unpublished local parent allowed).
2. New branch must be absent locally/remotely; switch -c from pinned parent SHA.
   Existing selected branch: record local/remote tips, create tracking local if
   remote-only, require parent ancestry and remote ancestor of local; stop divergence/
   unexpected remote-ahead. Inspect full range/paths for plan ownership. Never reset,
   recreate or rebase merely to fit scope.
3. Preserve unrelated dirty work only when safe/unambiguous; workflow moves/artifacts
   stay out of implementation commits. Never implement on parent.
4. After staged-diff-scope, confirm expected branch, status/stat/staged/unstaged/
   untracked/full diff; reject empty/out-of-scope/overlap. `git write-tree` must equal
   approved candidate tree. Compose under git-commit-message, commit and confirm
   HEAD tree equals it. Verify exact SHA before review. Satisfying adopted tip
   needs no empty commit; fixes use new commits, never amend published commits.

## Restack and handoff

Require clean implementation tree (separate worktree if stage moves prevent it;
never discard moves). Publication owner drafts existing CR and ready descendants
before rewriting. Record old base/tip/remote and new base with recoverable backup.

```bash
git rebase --onto <new-base-sha> <old-base-sha> <branch-name>
```

Resolve ordinary conflicts within authority; integrity/missing prerequisites/
out-of-authority resolution blocks affected operations only. Compare full ranges
with range-diff and deterministic source/tree/effective identities; classify
verbatim/mechanical regeneration/intentional behavior change. Stop unexpected
source changes, ready CRs or unclassified deltas. Verify new tip cleanly and refresh
parent pin/pack. Retain reviews only under build code-review-loop equal/focused
mapping proof; unmapped/manual/behavior/effective changes require fresh pass below
cap. At cap preserve real state and verify, carrying human disposition only with
proven unchanged behavior/finding risk; otherwise new decision/remediation.
Lease-push under git-sync-branch.

Review handoff needs local/upstream/fetched-remote/verified equality, parent-pin
ancestry, own proportionate trim and clean/capped correctness after remediation/
closure. Parent ref may move provisionally; ready CR/release requires matched
parent head and current clean/capped disposition. Unfinished owners remain
in_progress; routine restacks keep completed slices review with coverage pending.
Rewritten in_release sources invalidate membership under plans layout. Report
branch/parent/candidate SHAs, checks/restack proof and unrelated local files.
