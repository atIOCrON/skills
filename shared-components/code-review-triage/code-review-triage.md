# Code Review Triage

Assess pinned review hypotheses, no implementation edits. Require outputs, plan/pass,
owned scope, base/tip, pack and `<feature_dir>/<plan_slug>.reviews/code-review-triage-ledger.md`.
Confirm pack SHAs/ancestry/diff/checks, read committed content (not index/worktree),
standards/nearby patterns and `orchestration-triage-ledger-protocol.md`.

Use complete understandable responses despite format diagnostics: preserve originals/
findings, normalize locally under runner, never request formatting restarts. Deduplicate;
a reviewer label is no evidence. Accept only material `reproduced` or `binding-proof`:
confirm pin/path/existing-facilities/command/artifact/observed failure, or committed code/
binding source/full deduction. One bounded existing-facility reproduction per family;
never add code/tests/simulators/delay/lifecycle frameworks/guards/substantial harness to
prove a hypothesis. Reject speculation, unsupported inputs/scale/future needs/preferences;
best practice alone proves no defect. Existing issues block only when depended on,
worsened or required by scope. Preserve disposition of every reported finding.

Prefer deletion/simplification of new machinery; broad acceptance does not authorize
new ownership/coordinator/retry/lifecycle responsibility without demonstrated checkpoint
need. Batch accepted material fixes for existing owner, mapping each to acceptance,
prerequisite or binding source; independently releasable capability needs scope decision.
Do not routinely fix nits, stage/commit/push or inspect unrelated dirty work.

Resolve source conflicts in order: safety/security/legal/policy, approved scope,
repo standards, affected contracts, nearby convention, general best practice.
Amend within caller authority; human decision only for changed scope/higher binding source.

Ledger is the only file triage writes. Apply protocol identity/family/status/consolidation
and convergence triggers across epochs before dispatch. Two discovery passes with new
failures from one family/architecture/verification source require architecture reassessment,
not another incremental fix. Two accepted family fix cycles require autonomous continuation,
not a third local variation. The owning loop enforces the five-pass cap after remediation.
Return confirmed requests through `implementation-dispatch.md` with finding/family/ledger
IDs, owner, evidence class/path/proof and focused check; owner independently confirms first.

Early complete responses may unlock isolated provisional fixes only after evidence and
recurrence checks. Keep assessments outside ledger and edits outside reviewer checkout.
After all three substantively complete and mutation checks pass, reconcile once, write
ledger, revise/discard unsupported provisional work, then accept/commit. Skill feedback
and closure observations authorize no ledger entry, fix or additional pass.

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
