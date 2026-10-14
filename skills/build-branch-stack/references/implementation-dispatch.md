# Implementation Dispatch

Assign each independent plan to one persistent implementation chat, or assign
an approved dependency chain to one owner. Use `orchestration-runtime.md` for
creation, messaging, progress and pause/resume. Reuse this owner for every
amendment, verification failure and accepted finding.

## Assignment

Require repository and plan paths, provider, coordinator identity and return
route, owner name/ID, isolated checkout, owned files/modules, authoring branch
and verified base SHA, real code prerequisites, canonical manifest path,
assigned evidence directories, and candidate role. Name the chat
`<branch name without feature/> - Implementing`.

Render `implementation-dispatch-plan-invocation.md`. Supply absolute paths to
bundled `plan-implement.md`, `from-reviewed-plan-to-git-handoff.md`,
`implementation-readiness.md`, `orchestration-plans-layout.md`, and `operational-records.md`; have the owner
read those instructions. Include only unavailable essential content inline.
For a complex change, require the implementation analysis and design checkpoint
before editing. Give the owner the complete branch-local route: implementation,
checks, trim, fresh correctness reviews, closure, and fixes, preserving caps.

The coordinator registers the persistent ID and execution lease before
substantial work. Owners edit their checkouts/evidence, commit new revisions,
and return receipts; the coordinator owns canonical state, plan moves,
accepted refs, final order, restacks, and publication. Authoring pushes occur
only through an explicit coordinator lease naming the source, expected remote
SHA (or absence), allowed operation, and return condition. Owners never rewrite
accepted refs or restack others' branches. Hand back the lease before acceptance.
After acceptance, assign fixes to an isolated authoring checkout at the new pin;
the owner returns commits for coordinator installation and publication, then
continues reviews once the coordinator confirms verified remote-tip equality.

## Follow-up and Fixes

Send follow-ups to the same owner ID after checking execution ownership.
Batch accepted findings for that owner. Include current branch and parent pins,
reviewed/failed SHA, owned scope, accepted findings or concrete verification
failures, focused check, and relevant evidence paths. For each correctness
finding include family ID, `reproduced` or `binding-proof` class, supported path,
and evidence. Require the owner to independently reproduce it or confirm the
binding proof before editing; return unconfirmed findings to triage.

The owner makes new commits, checks, trim updates and fresh reviews when
required. Provisional edits use an isolated checkout at the reviewed SHA and
remain uncommitted until all three responses are triaged. Reconcile accepted
changes before committing; never amend a reviewed/published commit. Preserve
review counts and original-session closure. Send restack-invalidated review
work and user testing feedback to this owner with the coordinator's applicability
decision and new pins. Replacement is only for a genuinely unavailable session
under the runtime recovery rules, with history and evidence preserved.

## Guardrails and Return

Send accepted fixes only; prohibit speculative refactors, compatibility shims,
fallbacks and unrelated cleanup. Return exact paths/reasons when scope needs
expansion; the coordinator may adjust it within existing build authority.

Require an early verified-candidate handoff and a worker-completion handoff:
owner/coordinator identity, branch, commit, pinned authoring parent, checks,
trim/correctness outcomes and receipts, remaining dependencies/blockers,
operator handoff, and evidence paths. The coordinator promptly imports each
result and reports worker completion separately from accepted/restacked and
release-ready state. A completed handoff does not authorize release publication.
