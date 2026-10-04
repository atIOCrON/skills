# Stacked Change-Request Terms

- **Change request**: a GitLab merge request, GitHub pull request, or equivalent.
- **Base branch**: the branch that receives the complete stack, normally
  `develop`.
- **Dependency parent**: the nearest unmerged branch whose behavior a change
  requires. It is the base branch when no dependency exists.
- **Stacking predecessor**: the actual Git parent branch chosen for an explicit
  linear build. It may be functionally independent; record placement separately
  from code prerequisites.
- **Chained stack**: the first change targets the base; each later change
  targets its dependency parent or recorded stacking predecessor.
- **Base-targeted batch**: independent branches that each target the base.

Input order does not establish dependency. Chained targets must match ancestry;
base-targeted branches must not contain one another. Run independent roots of a
hybrid graph separately. Stop on a join that needs multiple unmerged parents;
allow a single verified cumulative parent that already contains all recorded
code prerequisites, with their inclusion proven. Do not hide required work.
