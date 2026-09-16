# Stacked Change-Request Terms

- **Change request**: a GitLab merge request, GitHub pull request, or equivalent.
- **Base branch**: the branch that receives the complete stack, normally
  `develop`.
- **Dependency parent**: the nearest unmerged branch whose behavior a change
  requires. It is the base branch when no dependency exists.
- **Chained stack**: the first change targets the base; each later change
  targets its dependency parent.
- **Base-targeted batch**: independent branches that each target the base.

Input order does not establish dependency. Chained targets must match ancestry;
base-targeted branches must not contain one another. Run independent roots of a
hybrid graph separately. Stop on a join that needs multiple unmerged parents;
the linear stack model cannot represent it without hiding a dependency.
