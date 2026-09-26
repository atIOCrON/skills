# Scheduling Contract

Keep eligible work running while preserving branch-local gates. After each
implementation, verification, push, trim, or correctness result, update state
and dispatch newly eligible work before waiting. Continue useful local work
while workers run. Input order creates no dependency.

## Dispatch

| Event | Work unlocked |
| --- | --- |
| Readiness complete; required parent verified and pinned, or no dependency | Implementation in an isolated checkout |
| Candidate committed | Exact-candidate verification |
| Candidate verified | Push; eligible descendant implementation |
| Tip verified and pushed; parent pinned | This branch's trim |
| This branch's trim proportionate; tip verified and pushed | This branch's correctness pass 1 |
| Prior findings handled; trim still valid; new tip verified and pushed | Next eligible correctness pass or closure under `code-review-loop.md` |

Dispatch independent branches concurrently. Overlap implementation,
verification, trim, and correctness across branches. A verified parent permits
provisional descendant implementation before ancestor reviews finish. Each
branch completes its own trim before correctness; siblings need not finish.
Handle results as they arrive without changing commits still under review.

Before launching an expensive check, apply the capability's equivalence rules.
Reuse valid evidence for unchanged determining inputs and effective results;
otherwise rerun the check.

## Capacity and isolation

Assign implementation workers separate worktrees, explicit ownership, and
distinct evidence paths. Keep reviewer inputs immutable. Serialize conflicting
shared mutations, including manifest writes, stage moves, and branch-ref
updates, without stopping unrelated work.

Record actual worker, reviewer, and shared-resource capacity. Dispatch all
eligible work up to that capacity; impose no branch-count or wave-size limit.
Prioritize work that unlocks descendants or final checks, then other eligible
work; avoid starving independent branches.
Before any wait, check for dispatchable work. Every queued task needs a concrete
dependency, ownership conflict, resource constraint, integrity issue, or
capacity limit. Ancestor review status, sibling progress, and input order are
insufficient reasons to wait.

Restack only affected descendants once their upstream fixes settle; continue
eligible pinned-diff reviews and unrelated work. No release-wide implementation,
trim, correctness, or restack barrier applies.

For A → B and independent C: dispatch A and C concurrently. Once A is verified
and pushed, start A's trim and B's implementation concurrently. Start A's
correctness when its trim finishes, even while B is unfinished. For 100
independent branches, dispatch all 100 if actual capacity permits.
