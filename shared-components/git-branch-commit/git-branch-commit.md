# Git Branch Commit

Create or adopt local plan branches and commit approved candidate trees. Do not
push or create change requests.

Base branch `<base-branch>` defaults to the remote default; chained mode passes
the local dependency parent. Name branches by repository policy, or use `fix/`,
`feature/`, `docs/`, `refactor/`, or `chore/` for the corresponding change. Never
name tools, models, assistants, or bots in a branch.

## Branch Start

1. Inspect `git status --short` and `git branch --show-current`.
2. Fetch and prune `origin`. Resolve the parent locally. If it exists on
   `origin`, require the local parent to equal the fetched remote tip. A local
   stack parent need not exist on `origin`.
3. For a new plan branch, stop if its name exists locally or on `origin`.
   Record the pinned parent SHA, then run
   `git switch -c <branch-name> <parent-sha>`.
4. For a user-selected existing plan branch, record its initial local and
   fetched remote tips. If only the remote branch exists, create a local
   tracking branch at that tip. Require the pinned parent SHA to be an ancestor
   of the branch tip. If both tips exist, require the remote tip to be an
   ancestor of the local tip; stop on divergence or an unexpected remote-ahead
   state. Inspect the full parent-to-tip range and map its commits and changed
   paths to the selected plan. Stop for unrelated or unaccounted work. Do not
   reset, recreate, or rebase the branch merely to fit the plan.

Allow unrelated dirty files only when they cannot be overwritten or carry
ambiguous implementation state. Feature stage moves are workflow state; keep
them and their artefacts out of candidate commits. Do not implement on the
dependency parent.

## Candidate Commit

After `staged-diff-scope` approves a candidate tree:

1. Require the expected plan branch. Inspect status, staged stat, staged and
   unstaged paths, untracked paths, and the full staged diff.
2. Stop for an empty stage, out-of-scope path, or staged/unstaged overlap.
3. Require `git write-tree` to equal the approved candidate tree SHA.
4. Compose the message with `git-commit-message.md` and commit.
5. Require `HEAD^{tree}` to equal the approved tree SHA. Verify this exact
   commit before review.

An adopted tip that already contains the requested work needs no empty commit;
verify and review its exact SHA. Create a new commit for every accepted fix
batch. Changing a reviewed commit invalidates its review. Never amend a
published commit.

## Reviewed Revision

Before handoff, require the local branch tip, upstream, fetched remote tip,
latest clean-reviewed SHA, and latest verified SHA to match. Require the parent
head to equal its pinned SHA and remain an ancestor. A changed parent needs a
restack, verification, review, and synchronized push.

## Restack

Require a clean implementation tree. Use a clean worktree if preserved feature
stage moves prevent a clean restack; never discard them. If a change request
exists, the publication skill must return it and ready descendants to draft
first.

1. Record old base and branch tips, any old remote tip, and the new parent
   SHA. Create a recoverable backup ref for the old tip.
2. Rebase with `git rebase --onto <new-base-sha> <old-base-sha> <branch-name>`.
   Abort and stop on conflicts; resolving them changes behavior intentionally.
3. Compare ranges with `git range-diff` and deterministic patch, tree, and
   generated-output checks. Classify each delta as `verbatim`, `mechanical
   regeneration`, or `intentional behavior change`.
4. Verify the new tip in a clean detached worktree. Apply normal scope,
   verification, and review gates to intentional changes. Update the pinned
   base and review pack, then run a fresh review of the new range.

After clean review, use `git-sync-branch.md` for the lease-protected push. Stop
for an unexpected source change, an existing ready change request, or an
unclassified delta. Report branch, parent and candidate SHAs, verification,
restack evidence, and unrelated local files.
