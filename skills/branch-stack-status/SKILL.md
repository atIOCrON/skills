---
name: branch-stack-status
description: Report a build's selected queue, accepted stack tail, parallel work, and completed review-loop counts without changing state.
disable-model-invocation: false
metadata:
  layer: capability
---

# Branch Stack Status

Accept ordered branch names or a build/legacy release manifest. Explicit branch
scope takes precedence. Otherwise discover the uniquely applicable unfinished
build under the original workspace's `plans/builds/`; if ambiguous, list IDs,
paths, and owners rather than combine stacks.

Work read-only. Do not edit files, refs, plans, or the manifest.

1. Read the current build manifest (or supplied legacy release manifest).
   Report `schedule` selection, spec order/current spec, coordinator, verified
   tail, and queued/implementing/prepared/blocked work with assignments and
   waiting reasons. Check accepted refs for tail drift; report without repair.
   For manifest-only input, tabulate accepted `branches` in manifest order and
   summarize planned/prepared work separately; neither counts as accepted.
   Resolve each requested branch's plan from the manifest. If absent or moved, search `plans/slices/` by
   slice slug and branch evidence, then legacy plan locations. Derive the stage
   from the slice directory using the shared stages, resolving legacy `done`
   as `merged` with a confirmed final merge and outstanding acceptance, or
   `fulfilled` with confirmed merge and acceptance evidence. Parent
   stage is a rollup and cannot substitute for this branch's child stage.
   Never present a predecessor's plan as the branch's own plan; say "No
   dedicated plan" when appropriate.
2. Inspect the plan stage, exact branch tip, trim ledger, correctness triage
   ledger, reviewer artifacts, and documented mappings after restacks.
   Report a snapshot time. Preserve the user's branch order and include
   every requested branch exactly once.
3. Count completed loops across the recorded branch history:
   - Trim Loops: completed, validated three-reviewer trim passes.
   - Code Loops: completed, validated three-reviewer correctness discovery
     passes. Use historical_completed_passes plus completed_passes when
     the manifest records both as distinct periods. Otherwise confirm the
     numbered passes against their ledgers.
   - Do not count launched but incomplete passes, reviewer transport retries,
     same-session format repairs, targeted closures, test-only closure
     mappings, or valid restack mappings.
   - A documented zero-diff trim applicability decision counts as zero loops.
   - If counts conflict or cannot be verified, show "Unclear" and explain.
4. Assign one status using this precedence:
   - Exhausted: correctness review reached its cap without a clean result.
   - Complete: this branch's own correctness reviews are clean and finished.
     An unfinished ancestor or external release check does not change that.
   - Code Review Started: correctness discovery has begun but is not finished.
   - Trim Finished: trim is proportionate on the current tip, or formally
     inapplicable to a zero-diff branch, and correctness has not begun.
   - Trim Started: trim has begun but has no proportionate current-tip result.
   - Implementation Finished: a candidate is committed and verified, with no
     trim review begun.
   - Implementation Started: implementation or required branch verification
     has begun but no verified candidate is finished.
   - Not Started: no implementation work has begun.
5. Output the accepted/requested branch table with exactly these columns:
   Branch | Plan file | Status | Trim Loops | Code Loops

Use clickable absolute links for plan files. Briefly explain missing plans,
zero-diff branches, exhausted caps, and any provisional Complete branches.
Do not equate individual branch completion with release readiness or plan
fulfillment. `Complete` in this table means correctness review is complete;
`merged` means final merge confirmed with acceptance outstanding; `fulfilled`
requires both. Report any merged slices separately from unmerged review work,
without changing the review-completion statuses above. Report any parent
rollup discrepancy read-only, without moving plans.
If no branches have been accepted yet, say so and report selected work from
the schedule; do not fabricate a branch table or placeholder commits.
