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
batch. Changing reviewed behavior invalidates its reviews. A conflict-free
mechanical restack may retain all three reviews only under the Restack rules
below. Never amend a published commit.

## Reviewed Revision

Before `review/` handoff, require the local, upstream, fetched remote, and
verified tips to match, plus proportionate trim and clean correctness reviews
or the exhausted cap after fixes and closure. Keep automated review state and
unresolved findings. Require the pinned parent SHA to be an ancestor; its ref
may have advanced. Ready CRs and release progression require the parent head
at its pin and clean current-tip reviews or an accepted capped disposition.
Restack a changed parent, verify, map reviews or run a fresh pass when allowed,
and synchronize the new tip before release progression.

## Restack

Require a clean implementation tree. Use a clean worktree if preserved feature
stage moves prevent a clean restack; never discard them. If a change request
exists, the publication skill must return it and ready descendants to draft
first.

1. Record old base and branch tips, any old remote tip, and the new parent
   SHA. Create a recoverable backup ref for the old tip.
2. Rebase with `git rebase --onto <new-base-sha> <old-base-sha> <branch-name>`.
   Stop automatic restacking on conflicts. Inspect and resolve each conflict
   under the plan's scope, preserving a backup of the old tip. Apply the
   generated-metadata exception in `code-review-loop.md` only with its proof.
3. Compare ranges with `git range-diff` and deterministic source, tree, and
   effective-output identity checks. Classify each delta as `verbatim`, `mechanical
   regeneration`, or `intentional behavior change`.
4. Verify the new tip in a clean detached worktree and update the pinned base
   and review pack. Retain prior reviews only for an equal `range-diff` with
   effective-identity evidence or the narrow `reviewed_restack` mapping in
   `code-review-loop.md`. Record the old-to-new SHA mappings and required
   evidence. Unmapped manual resolutions, inequalities, changed effective
   output, or behavior changes need a fresh three-reviewer pass when below the
   cap. At the cap, keep the actual review state and finish exact-tip verification.
   Carry the accepted human disposition through a valid behavior-preserving
   mapping when the accepted findings' risk is unchanged; seek a new decision
   only when that applicability cannot be proved.

Use `git-sync-branch.md` for the lease-protected push. A provisional wave
descendant stays `in_progress/` until its own trim and correctness reviews
finish or reach the cap. A routine restack of a completed slice leaves it in
`review/` while current-tip evidence is refreshed. Stop for an unexpected
source change, an existing ready change request, or an unclassified delta.
Report branch, parent and candidate SHAs,
verification, restack evidence, and unrelated local files.
