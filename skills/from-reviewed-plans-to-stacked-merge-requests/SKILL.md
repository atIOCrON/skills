---
name: from-reviewed-plans-to-stacked-merge-requests
description: Run an ordered list of reviewed plans through implementation, verification, pushed stacked branches, and GitLab merge requests without merging. Bundles all reusable orchestration components required by the route.
metadata:
  layer: runner
---

# From Reviewed Plans To Stacked Merge Requests

Use when the user provides one or more reviewed plan filenames and wants each
plan implemented, reviewed, committed, pushed, and opened as a GitLab merge
request stacked on the previous plan branch.

## Bundled Resources

Supporting workflow instructions are under `references/`, and executable
helpers are under `scripts/`. They are bundled resources, not separately
installed or discoverable skills.

Resolve `orchestration_skill_root` to this skill directory. Before processing
plans, read `references/orchestration-runtime.md` and select the host mapping.

Read each reference only when the workflow reaches the step that needs it. For
each plan, begin with `references/from-reviewed-plan-to-git-handoff.md`.
Direct stack operations additionally use:

- `references/git-branch-commit-push.md`;
- `references/gitlab-create-mr.md`.

## Inputs

- Ordered reviewed plan filenames or `plans/<file>.md` paths.
- Base target branch: `develop` unless the user names another.
- Starting branch: the base target branch unless the user names an existing
  stack head to continue from.

Stacked-MR terms (base target branch, stack parent branch, MR target branch,
true stacked MR chain) are defined in
`references/orchestration-stacked-mrs.md`. This
route creates a true stacked MR chain.

## Workflow

For each plan, in order:

1. Start from the current stack head. The first plan's stack parent branch is
   the starting branch; every later plan's stack parent branch is the
   previous plan's branch.
2. Read and follow `references/from-reviewed-plan-to-git-handoff.md`.
3. Run any stack-level or final verification not already covered by the
   git-handoff route.
4. Stage intended files only, then read and follow
   `references/git-branch-commit-push.md`
   for branch, commit, and push. Explicitly pass the plan's stack parent branch as
   `<base-branch>`; never rely on the helper's `develop` default in stack
   mode.
5. After the branch is pushed, read and follow
   `references/gitlab-create-mr.md` to
   create a true stacked MR. Explicitly pass the plan's stack parent branch as
   `<target-branch>`. The first plan's MR therefore targets the base target
   branch and every later MR targets the previous stack branch. Require the
   created MR's effective `squash_on_merge` value to be `true` before moving
   on.
6. Before moving on, verify `plans/<slug>.reviews/` exists and contains the
   code-review-loop review artefacts. If using a temporary worktree, copy
   ignored plan/review artefacts back to the user's main checkout and verify
   them there before deleting or abandoning the worktree.
7. Stay on the pushed branch before starting the next plan.

After all plan branches are committed and pushed, verify the clean final stack
head:

1. Run the repository's documented deterministic pre-handoff checks.
2. When `scripts/codex/protected_full_pipeline.py` exists, run:

   ```bash
   python -m scripts.codex.protected_full_pipeline \
     --data-root <absolute-protected-data-root> \
     --commit "$(git rev-parse HEAD)" \
     --output-dir <verification-artifact-directory>
   ```

Protected verification must use the committed lock-selected seed and baseline.
Never publish or refresh either during this route. Treat a lock mismatch or
unexpected output as a blocker; seed or baseline transitions require their
separate reviewed publication workflow.

## Rules

- Preserve unrelated dirty work; never stage or revert it.
- Use the bundled `git-branch-commit-push` component's branch naming and
  commit-message standards, with the current stack head as the parent for each
  plan branch.
- Pass explicit `<base-branch>` and `<target-branch>` values to the bundled git
  components for every stack item; do not rely on their defaults.
- Use a clean worktree for `gitlab-create-mr` if unrelated dirty work would
  fail its glab preflight (distinct from the reviewer preflight that the
  git-handoff route runs via `reviewer-preflight`).
- Do not use deprecated `git-branch-and-merge`.
- Do not merge any merge request, clean up, or delete branches.
- Do not leave a created MR with squash-on-merge disabled.
- Do not finish until every plan has a preserved `plans/<slug>.reviews/`
  folder or an explicit blocker explaining why preservation failed.
- Stop and report blockers if tests fail, export output is unexpected, or a
  clean commit cannot be created safely.
- Do not skip the final full-pipeline export test unless the user explicitly
  cancels it.

## Final Response

Return the ordered branch stack with branch name, stack parent branch, MR
target branch, commit SHA, push status, verification summary, per-plan
export-test status, final full-pipeline export-test status, merge-request
status and effective squash-on-merge value, review-artefact folder paths, and
confirmation that no merge was performed.
