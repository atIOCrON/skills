# Stacked Merge Request Terminology

- **Base target branch**: the branch the complete stack eventually merges
  into, normally `develop`.
- **Stack parent branch**: the previous branch in the ordered stack. The
  first stack branch's parent is the base target branch.
- **MR target branch**: the GitLab target branch of a single merge request.
- **True stacked MR**: a merge request whose MR target branch is its stack
  parent branch rather than the base target branch.
- **True stacked MR chain**: the stack layout where the first MR targets the
  base target branch and each later MR targets the previous stack branch.
  Stacked-plan runs create this layout.
- **Base-targeted stack**: the stack layout where every MR targets the
  base target branch directly.

Ordinary single-branch merge requests target the base target branch by
default; only stack mode overrides MR targets.
