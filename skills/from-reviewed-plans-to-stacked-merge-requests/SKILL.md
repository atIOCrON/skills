---
name: from-reviewed-plans-to-stacked-merge-requests
description: Run ordered reviewed plans through branch-first implementation, commit-pinned verification and review, pushed stacked branches, and ready GitLab merge requests without merging.
metadata:
  layer: runner
---

# From Reviewed Plans To Stacked Merge Requests

Use when the user provides reviewed plans to implement, verify, review, commit,
push, and publish as a true GitLab MR stack.

## Resources

Resolve `orchestration_skill_root` to this directory. Before processing plans,
read `references/orchestration-runtime.md` and
`references/orchestration-plans-layout.md`. For each plan, read
`references/git-branch-commit-push.md` to start its branch, then
`references/from-reviewed-plan-to-git-handoff.md`.

The route also uses `references/gitlab-create-mr.md`. Read other references only
when the active step requires them.

## Inputs

- Ordered reviewed plan filenames or `plans/<file>.md` paths.
- Base target branch: `develop` unless the user names another.
- Starting branch: the base target unless the user names an existing stack head.

Terms are defined in `references/orchestration-stacked-mrs.md`. This route
creates a true stack: each MR targets the preceding branch.

## Progress

Keep one compact table and update it only for state, review-pass, commit,
restack, or verification changes:

```text
| Plan | Status | Reviews | Branch | Commit | Next action |
```

Use `Queued`, `In progress`, `Blocked`, or `Complete`. `Complete` requires a
verified and clean-reviewed final SHA, synchronized branch and MR source,
preserved artefacts, correct MR target, ready status, and effective
squash-on-merge. Number review passes; never predict a final pass.

## Workflow

For each plan, in order:

1. Set its stack parent to the current stack head and pin that branch's SHA.
2. Before implementation, use `git-branch-commit-push.md` to create and check out
   the plan branch from that parent.
3. Follow `from-reviewed-plan-to-git-handoff.md`. It must:
   - stage selectively and self-review the candidate tree;
   - block staged/unstaged overlap on candidate files;
   - commit before formal review;
   - verify the exact commit in a clean detached worktree;
   - push and open a draft MR against the stack parent;
   - review the pinned parent-to-commit diff;
   - create, verify, push, and re-review new commits after material fixes;
   - prove local, upstream, MR, verified, and reviewed SHAs match, the MR target
     branch is the stack parent, and its head equals the pinned parent SHA; and
   - mark the MR ready only after a clean review.
4. Confirm the MR's effective `squash_on_merge` is true.
5. Preserve the plan's `.reviews/`, `.evidence/`, and any `.execution/` folders
   before removing a worktree.
6. Stay on the pushed plan branch; it becomes the next stack parent.

Before each plan, every ready transition, and final handoff, refetch every stack
branch and compare it with the recorded SHAs. On any movement, immediately
return the affected MR and every ready descendant to draft and mark them
`In progress`. Accept an unexpected source change only with user confirmation,
then refresh its MR metadata, verify, and review it. Restack descendants in order
through the git component, update each pinned parent, and rerun verification and
fresh review before restoring ready status.

After all plans:

1. Run the repository's deterministic pre-handoff checks on the clean final
   stack-head commit.
2. When `scripts/codex/protected_full_pipeline.py` exists, run it with the
   committed lock-selected seed and baseline:

   ```bash
   python -m scripts.codex.protected_full_pipeline \
     --data-root <absolute-protected-data-root> \
     --commit "$(git rev-parse HEAD)" \
     --output-dir <verification-artifact-directory>
   ```

Keep bulk output outside artefact folders and index concise evidence under the
last plan. Never publish or refresh protected seed or baseline data here. Treat
a lock mismatch or unexpected output as a blocker.

## Rules

- Make the least-complex change that satisfies the plan and affected contracts.
- Map every changed surface to plan scope or a binding contract. Stop for user
  approval before adding an unplanned deliverable.
- Preserve unrelated dirty work; never broadly stage, clean, or revert it.
- Use explicit stack-parent and MR-target branches; never rely on defaults.
- Review immutable commits, not the index. The index is only a candidate-tree
  scope gate.
- Do not amend published commits. Restacks may rewrite a draft branch only
  through the explicit force-with-lease procedure.
- Use deterministic commands for scope, identity, hashes, ancestry, and restack
  checks; do not ask reviewers to infer them.
- During restacking, classify every delta as `verbatim`, `mechanical
  regeneration`, or `intentional behavior change`. Verify the first two
  deterministically; implement, verify, and review the third normally.
- Do not merge MRs, delete branches, or leave squash-on-merge disabled.
- Stop for failed verification, unresolved findings, unsafe commit creation,
  revision mismatch, wrong MR target, failed push, or unpreserved artefacts.
- Do not skip the final full-pipeline export test unless the user cancels it.

## Final Response

Return the ordered stack with each branch, pinned parent, MR target, final SHA,
push and verification status, review passes, draft-to-ready MR status, effective
squash value, artefact and evidence paths, restack evidence, final pipeline
status, and confirmation that nothing was merged.
