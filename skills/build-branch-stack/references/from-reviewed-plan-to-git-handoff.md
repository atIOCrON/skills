# From Approved Plan to Git Handoff

Existing persistent owner completes approved human-selected slice on assigned
verified authoring base through checks/push/trim/correctness, no CR. Require
in_progress plan, approved parent/map/ownership, plan branch and pinned parent;
caller creates/adopts branch first. Coordinator owns canonical state/moves/
acceptance/publication, except explicit authoring lease.

| Step | Required reference/action |
| --- | --- |
| Implement/adopt | plan-implement.md and implementation-readiness.md; slice is executable, spec is not; checkpoint before edits |
| Candidate | staged-diff-scope.md, git-branch-commit.md; satisfying adopted tip needs no empty commit |
| Verify/publish | verification-runner.md then git-sync-branch.md via coordinator/lease; await remote-pin confirmation |
| Early handoff | Return verified candidate immediately to unlock prerequisites, retain in_progress/schedule.work |
| Review completion | trim-review.md then code-review-loop.md on own verified pushed pinned diff; no cross-branch barrier; continue provisionally through parent movement |
| Final handoff | orchestration-final-handoff.md: exact checks/trim, clean reviews or cap/unresolved findings, identities/pins/counts/paths |

Coordinator accepts and moves review only after own gates; ancestor/descendant
reviews and pending release integration/activation acceptance do not delay own
completion. Handoff preserves later checks' phase, owner, executor, procedure,
prerequisites, blocking milestone and status; branch verification passes claim no
release result. Failed branch verification/integrity blocks dependents, verified candidates with findings may
parent provisional work. Needed implementation returns owner in_progress; reconcile
integrity without overwrite, block only affected chain, continue independent work.
Restack after upstream settles; parent movement does not block eligible pinned
reviews. Seek human input only at caller authority boundary. Return blocker,
`Review cap reached`, `Reviewed provisionally` or `Reviewed and pushed`.
