---
name: code-review-closure
description: Check whether previously raised code-review findings are resolved by staged fixes, rejected with sufficient evidence, or still open. Used by code-review-loop after code-review triage and verification.
metadata:
  layer: capability
---

# Code Review Closure

Check closure for code-review findings that this reviewer previously raised
when the orchestrator explicitly requests closure. Do not perform a fresh
review and do not raise new findings.

## Inputs

Require:

- original review artifact path,
- reviewer session artifact path,
- triage summary,
- applied code fixes and rejected findings,
- verification summary,
- plan path,
- cross-pass triage ledger path
  (`plans/<plan_slug>.reviews/code-review-triage-ledger.md`).

## Scope

- Assess only findings from the original code-review artifact.
- Closure is conditional in `code-review-loop`; if a finding was not included
  in the closure request, do not assess it.
- This closure is expected to run in the same reviewer conversation/session that
  produced the original review artifact. If it is not the same conversation,
  report that as `Closure blocked` rather than doing a fresh review.
- For accepted findings, decide whether the staged code fix resolves the
  finding.
- For rejected findings, decide whether the rejection evidence is sufficient.
- Use evidence from the staged diff, cited docs, cited code, verification
  results, or gold-standard data-engineering best practice.
- Do not edit code or doc files. Updating the cross-pass triage ledger to
  transition status for entries this reviewer raised is the only file write
  closure performs and is treated as a closure artifact, not a code change.
- Do not inspect unrelated files except where needed to validate a staged-diff
  contract or cited reader/consumer.
- Do not perform a fresh code review or introduce new findings. New concerns
  noticed during closure are out of scope: surface them as procedural feedback
  under `## Skill Feedback`, not as ledger writes, new findings, or blockers.
- Closure must not extend the review loop beyond the original requested
  concern. Decide only whether the concern is resolved, reasonably rejected, or
  still materially open.
- Do not use findings, summaries, or conclusions from other reviewers unless
  they are included in the triage summary.

## Cross-Pass Triage Ledger Updates

Ledger schema and status transitions are defined in
.agents/skills/orchestration-conventions/references/triage_ledger_protocol.md.

For each finding this reviewer raised in the original review artifact, update
the ledger entry created by triage. Do not create new ledger entries. Closure
maps its output sections to ledger statuses as follows:

- `## Resolved` -> ledger status `resolved`.
- `## Rejection Accepted` -> ledger status `rejected`.
- `## Still Open` -> ledger status remains non-terminal (`accepted-fix-pending`
  if the worker fix is incomplete, `re-opened` if the entry was previously
  `resolved` and the concern recurs, otherwise `open`).
- `## Needs User Decision` -> ledger status remains non-terminal (typically
  `open` or `accepted-fix-pending`); the orchestrator pauses for user
  decision before the next pass.

Cite the `ledger_id` for every entry this closure transitions in the closure
artifact. If a finding cannot be matched to an existing ledger entry, treat
that as a procedural failure: do not create a new entry and report the
mismatch under `## Skill Feedback` so the orchestrator can correct triage.

## Output

```markdown
## Resolved
- [{finding_id}] [{ledger_id}] <why the staged fix resolves it>

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

End with exactly one:

- `Closure confirmed`
- `Closure blocked`
