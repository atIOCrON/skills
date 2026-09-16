# Change Request Layouts

- **Base target branch**: the branch the complete stack eventually merges
  into, normally `develop`.
- **Dependency parent**: the nearest unmerged branch whose behavior a change
  requires. It is the base branch when no such dependency exists.
- **MR target branch**: the GitLab target branch of a single merge request.
- **Chained MR**: an MR whose target is its dependency parent rather than the
  base branch.
- **True stacked MR chain**: the stack layout where the first MR targets the
  base target branch and each later MR targets the previous stack branch.
  Use it only when each later change requires its predecessor.
- **Base-targeted stack**: the stack layout where every MR targets the
  base target branch directly.

An ordered input list does not prove dependency. Independent plans branch from
and target the base. Avoid branches that inherit earlier changes while their MRs
target the base: those MRs show cumulative, misleading diffs. A plan with
multiple unmerged dependency parents is a DAG join, not a linear stack. Merge a
prerequisite first or redesign the split; do not hide the join in one parent.
