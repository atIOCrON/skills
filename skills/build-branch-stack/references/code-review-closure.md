# Code Review Closure

Assess only this reviewer's named prior findings when requested; no fresh review,
new findings or file writes. Require original review/session artifacts, selected IDs,
applied changes/rejection evidence, checks, neutral pack, old/current SHAs, plan and
cross-pass ledger. Batch selected findings, excluding ordinary nits. Same originating
session is required; otherwise `Closure blocked`, never substitute fresh discovery.
Use current-stage artifact paths and only pinned diff/cited code/docs/checks/contracts;
no other reviewer's conclusions or unrelated files beyond needed consumers/contracts.

Compare committed fixes against original invariant, or test rejection evidence. With
unchanged commit/base assess added proof only; it cannot resolve an existing demonstrated
defect. New observations belong solely in Skill Feedback, never findings/blockers,
implementation/test expansion, ledger entries or another pass. Stay within requested concern.

Propose existing-ledger transitions under `orchestration-triage-ledger-protocol.md`:
Resolved→resolved; Rejection Accepted→rejected; Still Open retains accepted-fix-pending
for incomplete fix, re-opened for failed prior resolution, architecture-review-required
if already set, otherwise open. Needs User Decision remains non-terminal, only for
product intent or authority outside caller; insufficient proof stays Still Open.
Cite ledger_id for every transition. Unmatched finding is procedural feedback, not
a new entry. Orchestrator applies changes. End Closure confirmed or Closure blocked.

## Output

```markdown
## Resolved
- [{finding_id}] [{ledger_id}] <why the committed fix resolves it>

## Rejection Accepted
- [{finding_id}] [{ledger_id}] <why the rejection evidence is sufficient>

## Still Open
- [{finding_id}] [{ledger_id}] <what remains unresolved and what evidence supports that>

## Needs User Decision
- [{finding_id}] [{ledger_id}] <why evidence is insufficient or product intent is required>

## Ledger Transitions This Closure
- {ledger_id}: <old_status> -> <new_status>

## Skill Feedback
- <non-blocking feedback>
```

If there is no skill feedback, write exactly `- None`. Use `- None` under any
output section with no entries.

Keep the response findings-only. Cite concise evidence and artifact paths; do
not restate the implementation, transcript, or successful checks unrelated to
the selected findings.

End with exactly one:

- `Closure confirmed`
- `Closure blocked`
