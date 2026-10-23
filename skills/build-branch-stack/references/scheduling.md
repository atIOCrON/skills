# Scheduling Contract

After every implementation/check/push/trim/review result, import handoffs and
reassess dispatch before waiting. Fill actual worker/reviewer/shared-resource
capacity with independent work within/across specs; prioritize current block and
unlocking prerequisites, then later specs. Without parallel capacity finish current
spec unless blocked. No branch/wave/one-spec/build-phase barrier.

| Gate | Unlocked work |
| --- | --- |
| Readiness + verified prerequisite inclusion in pinned base | Isolated implementation, including later specs |
| Committed candidate | Exact verification |
| Verified pushed tip + pinned parent | Prepared status/provisional trim |
| Owner complete + returned lease + verified predecessor | Coordinator restack/verify/push/accept |
| Accepted tip verified/pushed | Map proof; return invalidated work to owner |
| Own trim proportionate + verified pushed tip | Correctness pass 1 |
| Prior findings handled + valid trim/current verified pushed tip | Next eligible pass/closure |

Verification in this table means branch implementation verification under the
operational-records phase contract. Pending release integration/activation checks
do not block implementation, reviews, placement or build completion. Inventory and
hand off their owners/procedures/milestones; an agent executor does not change phase.

Linear order controls placement, not code need. Prove prerequisites in authoring
base; acceptance/ancestor reviews need not finish first. Missing code permits only
independent preparation. Each branch trims before correctness, branches overlap;
moving parents leave pinned review provisional until settled restack/mapping.

Wait only for named prerequisites, actual resources, integrity/ownership, major
conflicts or acceptance order. Major conflicts name competing contracts/architectures,
incompatible patch/dependency order or redesign-scale rewrites. Ordinary rebases,
minor file overlap/generated reconciliation/later-spec placement/ancestor reviews
cannot idle implementation capacity. Record reason/condition/capacity and individual
pause/exclusion; paused owners remain assigned under runtime rules.

Use isolated worktrees/evidence and pinned authoring bases. Coordinator owns shared
state/accepted refs/tail; owners finish/return leases before assembly under queue-build.
Stop/isolate affected in-flight work before rewrite; never rebase active owner checkout.
Resolve ordinary conflicts with backups/owned ranges. Restack descendants once
upstream settles, continuing pinned reviews/unrelated work. Verify new tips with
smallest sufficient checks plus capability-proven unchanged-input/effective reuse.
Return invalidated work to same owner, retaining original completion separately
from acceptance/current coverage. Release readiness is separate; authorized prefix
tests belong to the release/staging workflow, pin snapshot/route feedback and add
no whole-build barrier or waived gate. Proven implementation defects return to
their owners; a pending later check alone does not reopen branch review.
