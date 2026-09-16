---
name: from-reviewed-plans-to-stacked-merge-requests
description: Turn reviewed plans into verified GitLab merge requests, chaining only changes with real dependencies.
metadata:
  layer: runner
---

# From Reviewed Plans To Stacked Merge Requests

Use when the user provides reviewed plans to implement, verify, review, commit,
push, and publish as dependent or independent GitLab merge requests.

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
- Base target branch: the repository default unless the user names another.
- Starting branch: the base target unless the user names an existing parent.
- Layout: `auto` by default, or `chained` / `base-targeted` when the user
  explicitly selects one.
- Dependency map: each plan's one required unmerged predecessor, or `none`.

Terms are defined in `references/orchestration-stacked-mrs.md`. In `auto` mode,
target the nearest unmerged branch the plan needs; otherwise target the base.
Input order alone does not establish a dependency. Split independent roots into
separate chains rather than creating a multi-root merge run. If one plan needs
multiple unmerged predecessors, stop: merge a prerequisite first or redesign
the split instead of inventing a linear parent.

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

1. Record the plan's dependency evidence. Set its parent to the required
   unmerged predecessor, or the base target when none exists, and pin its SHA.
2. Before implementation, use `git-branch-commit-push.md` to create and check out
   the plan branch from that parent.
3. Follow `from-reviewed-plan-to-git-handoff.md`. It must:
   - stage selectively and self-review the candidate tree;
   - block staged/unstaged overlap on candidate files;
   - commit before formal review;
   - verify the exact commit in a clean detached worktree;
   - push and open a draft MR against the dependency parent;
   - review the pinned parent-to-commit diff;
   - create, verify, push, and re-review new commits after material fixes;
   - prove local, upstream, MR, verified, and reviewed SHAs match, the MR target
     branch is the dependency parent, and its head equals the pinned parent
     SHA; and
   - mark the MR ready only after a clean review.
4. Confirm the MR's effective `squash_on_merge` is true.
5. Preserve the plan's `.reviews/`, `.evidence/`, and any `.execution/` folders
   before removing a worktree.
6. Record the branch as a parent only for plans that depend on it.

Before each plan, every ready transition, and final handoff, refetch every
dependency branch and compare it with the recorded SHAs. On movement, return
the affected MR and its ready descendants to draft. Accept an unexpected source
change only with user confirmation. Then refresh metadata, restack only its
descendants, verify, and review the new commits before restoring ready status.

After all plans:

1. Run deterministic pre-handoff checks on every dependency-chain head and
   independent MR head. For an ordered independent batch, build an unpushed
   temporary integration commit from the pinned base in merge order and test
   that combined state. Confirm applicable CI includes behavior tests and
   risk-based lint, type, dependency, secret, and static-security checks; stop
   when a required class is absent or cannot run.
2. When `scripts/codex/protected_full_pipeline.py` exists, run it with the
   committed lock-selected seed and baseline:

   ```bash
   python -m scripts.codex.protected_full_pipeline \
     --data-root <absolute-protected-data-root> \
     --commit "<verified-chain-head-or-temporary-integration-sha>" \
     --output-dir <verification-artifact-directory>
   ```

Keep bulk output outside artefact folders and index concise evidence under the
last plan. Never publish or refresh protected seed or baseline data here. Treat
a lock mismatch or unexpected output as a blocker.

## Rules

- Make the least-complex change that satisfies the plan and affected contracts.
- Require changed behavior to have proportionate regression tests. A plan need
  not name those tests explicitly.
- Map every changed surface to plan scope or a binding contract. Stop for user
  approval before adding an unplanned deliverable.
- Preserve unrelated dirty work; never broadly stage, clean, or revert it.
- Use explicit dependency-parent and MR-target branches; never rely on defaults.
- Chain only genuine dependencies. Independent branches start from and target
  the base branch.
- Review immutable commits, not the index. The index is only a candidate-tree
  scope gate.
- Run fresh `claude`, `codex`, and `cursor` reviewers in parallel for every
  review pass. All three must complete successfully.
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

Return each dependency group and independent MR with its dependency evidence,
branch, pinned parent, target, final SHA, verification, review passes, ready
status, squash value, artefacts, restack evidence, final pipeline status, and
confirmation that nothing was merged.
