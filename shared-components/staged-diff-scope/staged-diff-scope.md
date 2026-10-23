# Staged Commit Scope

Prepare exact candidate tree, not formal code review. Require repo, plan, owned
paths/modules and reason initial-candidate/post-fix-candidate/staged-changes-entry.
Inspect `git status --short`; identify unrelated dirty/untracked files. Stage only
explicit intended implementation/accepted-fix paths, never broad git add, cleanup
or revert. Exclude workflow moves/review/execution/evidence unless owned by plan.

Inspect cached name-only/stat/full diff and `git diff --cached --check`; block
out-of-scope paths or any staged path with unstaged edits. Record `git write-tree`.
Commit this approved tree before immutable parent-to-tip review, never review index.
Return staged/unrelated dirty lists, stat, tree SHA, in-scope/blocked and blocker reason.
