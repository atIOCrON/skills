# Code Review Triage

Turn commit-pinned review feedback into accepted fix requests or concise
rebuttals. Do not edit implementation files.

## Inputs

Require reviewer responses, plan path, pass number, intended implementation
scope, review base and commit SHAs, neutral pack, and cross-pass ledger path:
`<feature_dir>/<plan_slug>.reviews/code-review-triage-ledger.md`.

## Read First

1. Confirm the pack's SHAs, ancestry, diff, verification evidence, and branch
   identity checks.
2. Read `git diff <base-sha>...<review-sha>` and committed content at
   `<review-sha>`; ignore the index and working tree.
3. Read applicable standards and nearby patterns.
4. Read or initialize the ledger using
   `references/orchestration-triage-ledger-protocol.md`.

## Rules

- Treat comments as hypotheses; deduplicate them before acting.
- Independently accept only `reproduced` or `binding-proof` findings that meet
  the material-finding definition. A reviewer label is not evidence.
- For `reproduced`, confirm the pinned SHA, supported production-like path,
  existing-facilities-only claim, command or procedure, artifact, and observed
  failure. For `binding-proof`, confirm the pinned committed code, binding
  source, and complete proof chain.
- Reject static plausibility and any claim that needs a new simulator,
  generalized delay, lifecycle framework, production guard, or substantial
  harness to establish it. Allow one bounded reproduction cycle with existing
  facilities per failure family; do not implement code or tests to prove a
  review hypothesis.
- Reject claims based only on unsupported inputs, hypothetical scale, future
  use, or architecture preference.
- General best practice cannot establish a defect alone.
- A pre-existing issue blocks only when this commit depends on or worsens it,
  or the plan requires its correction.
- Recommend the smallest fix mapped to an acceptance condition, demonstrated
  prerequisite, or binding contract. Flag a new independently releasable
  capability as a product-scope decision.
- Before accepting a fix, ask whether deleting or simplifying branch-introduced
  machinery closes the finding. A broad acceptance condition alone does not
  justify a new state owner, coordinator, retry system, or lifecycle
  responsibility; require an architecture checkpoint with demonstrated need.
- Batch material findings for one implementer. Do not routinely fix nits.
- Do not stage, commit, push, or inspect unrelated dirty work.

Resolve source conflicts in this order: safety, security, legal, and policy;
approved scope; repository standards; affected contracts; nearby conventions;
general best practice. Resolve repository-local conflicts within the calling
skill's authority. Require the user only when resolution changes approved
product scope or a higher-ranked binding source.

## Ledger And Handoff

The ledger is the only file triage may write. Apply its failure-family, status,
recurrence, architecture-source, and consolidation rules across all passes and
epochs. If the same failure family or branch-introduced coordinator, state
machine, retry system, lifecycle interception, or verification model produces
new material failure modes in any two recorded fresh passes, mark
`architecture-review-required` and do not dispatch another incremental fix.
Changing implementation shape or epoch does not reset this count. Return it for
autonomous architecture reassessment. Otherwise send accepted fixes through
`implementation-dispatch`, including finding ID, family ID, owner, required
change, evidence class, evidence, and verification check. The worker must
reproduce the failure or confirm the binding proof before editing. Fixes never
mutate the reviewed SHA.

After two accepted fix cycles in one failure family, prohibit another local
variation and record an autonomous continuation decision under the ledger
protocol. Continue only for a confirmed material defect with a viable
disposition that does not repeat an exhausted variation. Ask the user only when
every viable disposition crosses the calling skill's authority boundary. The
owning loop, not triage, enforces the five-pass plan cap after pass 5 has been
triaged and its accepted work processed.

## Output

```markdown
## Accepted Fix Requests
- [{finding_id}] [{ledger_id}] [{family_id}] <owner> - <required change> - Evidence class: <reproduced|binding-proof> - Evidence: <citation> - Verify: <check>

## Rejected
- [{finding_id}] [{ledger_id}] <reason with evidence>

## Contradictions
- [{finding_id}] [{ledger_id}] <conflict> - <evidence/resolution>

## Re-opened Concerns
- [{ledger_id}] <prior status> - <reason>

## Recurring Escalations
- [{ledger_id}] first_pass=<p> last_pass=<p> - <root-cause or architecture action>

## Architecture Ratchet
- [<architecture source>] passes=<previous>,<current> - <why incremental fixes must stop and which architecture alternatives need reconsideration>

## Autonomous Continuation Decision
- Trigger: <two family fix cycles|None> - Evidence: <confirmed findings and rejected hypotheses> - History: <related fixes and epochs> - Alternatives: <removal, simplification, native owner, upgrade, narrow dependency correction, split> - Decision: <reject|complete|redesign|change-owner|upgrade|dependency-correction|split|blocked-authority> - Next action: <one authorized action or None>

## Ledger Writes This Pass
- added: <ledger_id>, ...
- updated: <ledger_id> (<old_status> -> <new_status>), ...

## Worker Handoff
- <concise fix payload, or None>
```

Use `- None` for empty sections and `[no-ledger]` for non-material items. Skill
feedback and closure observations cannot create ledger entries, worker work, or
another pass. End
with exactly one: `Resolve contradictions`, `Ready for worker fixes`,
`Partial - blocker encountered`, `Architecture review required`, `Recurring
escalations - architecture reassessment required`, or `No code changes needed`.
