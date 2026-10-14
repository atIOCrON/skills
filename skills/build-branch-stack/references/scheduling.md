# Scheduling Contract

Start all eligible independent plans concurrently up to actual resources and
user priorities. Each runs in its own persistent owner chat, or one chat for
an approved dependency chain, under `orchestration-runtime.md`. Keep that owner
through implementation, checks, trim, correctness and fixes.
After each implementation, verification, push, trim,
or correctness result, update state and dispatch eligible work before waiting.
Read `queue-build.md` for selection, spec blocks, and ownership. Linear order
controls stack placement, not functional dependency.

## Dispatch

| Event | Work unlocked |
| --- | --- |
| Readiness passed; code prerequisites in a verified pinned base | Isolated implementation, including later specs |
| Candidate committed | Exact-candidate verification |
| Candidate verified and pushed; authoring parent pinned | Mark prepared; start provisional trim |
| Next owner complete; predecessor verified and pinned | Coordinator restacks, verifies, pushes, and accepts |
| Accepted tip verified and pushed | Coordinator assesses mappings; existing owner runs necessary trim/review work |
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

Verified authoring code unlocks dependent work before final placement or
ancestor reviews finish. Prove required code is included in the pinned base;
stack acceptance is not a code prerequisite. Do not implement dependent
behavior against empty branches or missing contracts; independent research/preparation may proceed.

Overlap implementation, verification, trim, and correctness. Each prepared or
accepted branch finishes its own trim before correctness. Review immutable,
pinned parent-to-tip diffs with all code prerequisites present. Later-spec
results may run provisional reviews while awaiting ordered acceptance; stack
placement and unfinished sibling/ancestor reviews impose no review barrier.

Reuse expensive checks only under capability equivalence rules for unchanged
inputs and effective results. Otherwise rerun; re-verify after a base change.

## Capacity and Isolation

Use separate worktrees, explicit ownership, pinned authoring bases, and distinct
evidence paths. The coordinator owns canonical state and accepted refs/tail,
subject to publication handoffs; worker branches are separate from the stack.
The owner keeps its authoring base pinned until its handoff; the coordinator
assembles results onto the final stack. Stop or isolate affected in-flight work
before rewriting its ref; transfer leases and pins explicitly. Never rebase an
owner's active checkout underneath it.

Record actual chat/process, reviewer and shared-resource capacity. Preserve
individual pauses and exclusions while other eligible work continues. Include
concrete waiting reasons and resume conditions; a paused owner is not a free
assignment to replace or restart elsewhere. Before waiting, check dispatchable work. Every waiting task needs a concrete prerequisite,
major conflict, resource/capacity limit, ownership/integrity issue, or acceptance
order reason. Pending ancestor/sibling reviews, later spec placement, and
routine conflict risk do not justify idle implementation capacity.

Resolve ordinary conflicts autonomously within scope, preserving backups and
owned ranges. Behavior changes require fresh verification/review. Restack
affected descendants once upstream fixes settle; continue pinned-diff reviews
and unrelated work. No build-wide implementation, review, or restack barrier
applies; final release gates remain.

Retrieve completed owner handoffs and import candidate/check/review receipts at
every checkpoint before waiting. Report worker complete on its authoring tip,
accepted/restacked on its final placement, and release ready separately. Owner
completion may be capped; it does not imply clean reviews or release authority.
After a restack the coordinator classifies evidence applicability and sends
invalidated work back to the same owner. Preserve original completion evidence.
Explicitly authorized local prefix testing pins the assembled snapshot; route
feedback to existing owners without imposing a whole-build barrier or waiving
release gates.

For independent A1, A2, B1 in specs A then B: dispatch all three if capacity
permits; start provisional trim as each candidate verifies and pushes. Accept
A1, restack/verify/accept A2, then B1; map reviews or rerun invalidated passes.
For A1 -> A2, start A2 once A1 is verified and pushed; independent B1 can start
earlier from a verified base.
