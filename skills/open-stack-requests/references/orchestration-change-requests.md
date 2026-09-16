# Change Request Layouts

- **Base target branch**: the branch the complete stack eventually merges
  into, normally `develop`.
- **Dependency parent**: the nearest unmerged branch whose behavior a change
  requires. It is the base branch when no such dependency exists.
- **Change request (CR)**: a forge-hosted proposal to merge one source branch
  into one target branch. Providers may call it a merge request or pull request.
- **CR target branch**: the target branch of a single change request.
- **Chained CR**: a CR whose target is its dependency parent rather than the
  base branch.
- **True stacked CR chain**: the layout where the first CR targets the base
  target branch and each later CR targets the previous stack branch.
  Use it only when each later change requires its predecessor.
- **Base-targeted stack**: the layout where every CR targets the
  base target branch directly.

An ordered input list does not prove dependency. Independent plans branch from
and target the base. Avoid branches that inherit earlier changes while their CRs
target the base: those CRs show cumulative, misleading diffs. A plan with
multiple unmerged dependency parents is a DAG join, not a linear stack. Merge a
prerequisite first or redesign the split; do not hide the join in one parent.
