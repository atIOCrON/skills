# Change Request Layouts

- **Base target branch**: the branch the complete stack eventually merges
  into, normally `develop`.
- **Dependency parent**: the nearest unmerged branch whose behavior a change
  requires. It is the base branch when no such dependency exists.
- **Stacking predecessor**: the actual Git predecessor chosen for an explicit
  linear build; functional prerequisites are recorded separately.
- **Change request (CR)**: a forge-hosted proposal to merge one source branch
  into one target branch. Providers may call it a merge request or pull request.
- **CR target branch**: the target branch of a single change request.
- **Chained CR**: a CR whose target is its dependency parent or recorded stacking predecessor rather than the
  base branch.
- **True stacked CR chain**: the layout where the first CR targets the base
  target branch and each later CR targets the previous stack branch.
  Use it for functional chains or explicitly linear builds with proven ancestry.
- **Base-targeted stack**: the layout where every CR targets the
  base target branch directly.

An ordered input list does not prove functional dependency. Independent roots
branch from and target the base unless an explicit linear build places them
above a recorded stacking predecessor. Avoid branches that inherit earlier changes while their CRs
target the base: those CRs show cumulative, misleading diffs. A plan with
multiple unmerged parents requires a merged prerequisite or a verified
cumulative predecessor containing every required slice. Prove that inclusion;
do not hide missing prerequisites or manufacture functional dependencies.
