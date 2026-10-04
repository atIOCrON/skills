# Scheduling Contract

Prioritize parallel work. After each implementation, verification, push, trim,
or correctness result, update state and dispatch eligible work before waiting.
Read `queue-build.md` for selection, spec blocks, and ownership. Linear order
controls stack placement, not functional dependency.

## Dispatch

| Event | Work unlocked |
| --- | --- |
| Readiness passed; code prerequisites in a verified pinned base | Isolated implementation, including later specs |
| Candidate committed | Exact-candidate verification |
| Independent candidate verified but not next in order | Mark prepared; dispatch other work |
| Next candidate prepared; predecessor verified and pinned | Coordinator restacks, verifies, pushes, and accepts |
| Accepted tip verified and pushed | Its trim; dependent implementation |
| Its trim proportionate; tip verified and pushed | Correctness pass 1 |
| Prior findings handled; trim valid; new tip verified and pushed | Next eligible pass or closure under `code-review-loop.md` |

Fill useful worker/reviewer capacity with independent slices within and across
specs. Prioritize the current block and work that unlocks prerequisites, then
later specs. Impose no branch-count, wave-size, or one-spec dispatch limit.
Without parallel capacity, finish the current spec first unless concretely blocked.

Serialize only work with unavailable code prerequisites, anticipated major
conflicts, actual resource limits, or integrity issues. Minor same-file overlap,
ordinary rebasing, and predictable generated-file reconciliation are expected
costs. Major conflicts involve competing runtime contracts/architectures,
incompatible dependency/patch ordering, or broad rewrites likely to need
redesign. Name affected paths/contracts and expected impact; generic conflict
risk is insufficient. Keep unrelated work running.

Verified prerequisites unlock provisional descendants before ancestor reviews
finish. Do not implement dependent behavior against empty branches or missing
contracts; independent research/preparation may proceed.

Overlap implementation, verification, trim, and correctness. Each accepted
branch finishes its own trim before correctness; sibling/spec reviews impose
no barrier. Review immutable, pinned parent-to-tip diffs. Later-spec results
wait prepared for ordered acceptance without occupying idle workers.

Reuse expensive checks only under capability equivalence rules for unchanged
inputs and effective results. Otherwise rerun; re-verify after a base change.

## Capacity and Isolation

Use separate worktrees, explicit ownership, pinned authoring bases, and distinct
evidence paths. The coordinator owns canonical state and accepted refs/tail,
subject to publication handoffs; worker branches are separate from the stack.

Record actual worker, reviewer, and shared-resource capacity. Before waiting,
check dispatchable work. Every waiting task needs a concrete prerequisite,
major conflict, resource/capacity limit, ownership/integrity issue, or acceptance
order reason. Pending ancestor/sibling reviews, later spec placement, and
routine conflict risk do not justify idle implementation capacity.

Resolve ordinary conflicts autonomously within scope, preserving backups and
owned ranges. Behavior changes require fresh verification/review. Restack
affected descendants once upstream fixes settle; continue pinned-diff reviews
and unrelated work. No build-wide implementation, review, or restack barrier
applies; final release gates remain.

For independent A1, A2, B1 in specs A then B: dispatch all three if capacity
permits; accept A1, restack/verify/accept A2, then B1. A's reviews may continue.
For A1 -> A2, start A2 once A1 is verified and pushed; independent B1 can start
earlier from a verified base.
