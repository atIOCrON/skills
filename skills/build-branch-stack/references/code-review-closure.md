# Code Review Closure

Check closure for code-review findings that this reviewer previously raised
when the orchestrator explicitly requests closure. Do not perform a fresh
review and do not raise new findings.

## Inputs

Require:

- original review artifact path,
- reviewer session artifact path,
- finding IDs selected for closure,
- applied change per finding,
- rejection evidence for any selected rejected material finding,
- verification evidence paths,
- neutral review-pack path,
- original and current review commit SHAs,
- plan path and review phase,
- cross-pass triage ledger path
  (`<feature_dir>/<plan_slug>.reviews/code-review-triage-ledger.md`).

## Scope

- Assess only findings from the original review artifact and phase.
- Assess only IDs named in the closure request. Batch all selected findings from
  this reviewer into one response; do not assess ordinary nits.
- This closure is expected to run in the same reviewer conversation/session that
  produced the original review artifact. If it is not the same conversation,
  report that as `Closure blocked` rather than doing a fresh review.
- For accepted code fixes, compare the original and current review commits
  and decide whether the committed fix resolves the finding while preserving
  its surrounding invariant.
- For rejected findings, decide whether the rejection evidence is sufficient.
- When the commit and base SHAs are unchanged, assess added evidence only. It
  may justify rejecting a finding or confirm an already implemented contract;
  it cannot close a demonstrated code defect that still exists.
- Use evidence from the pinned commit diff, cited docs, cited code, verification
  results, or applicable engineering principles.
- Do not write files. Propose ledger transitions for the orchestrator to apply.
- Do not inspect unrelated files except where needed to validate a changed-code
  contract or cited reader/consumer.
- Do not perform a fresh code review or introduce new findings. New concerns
  noticed during closure are out of scope: surface them as procedural feedback
  under `## Skill Feedback`, not as ledger writes, new findings, or blockers.
- Closure must not extend the review loop beyond the original requested
  concern. Decide only whether the concern is resolved, reasonably rejected, or
  still materially open.
- Do not use findings, summaries, or conclusions from other reviewers.

## Cross-Pass Triage Ledger Updates

Ledger schema and status transitions are defined in
references/orchestration-triage-ledger-protocol.md.

For each selected finding, propose a transition for its existing ledger entry.
Do not create entries. The orchestrator applies these mappings:

- `## Resolved` -> ledger status `resolved`.
- `## Rejection Accepted` -> ledger status `rejected`.
- `## Still Open` -> ledger status remains non-terminal (`accepted-fix-pending`
  if the worker fix is incomplete, `re-opened` if the entry was previously
  `resolved` and the concern recurs, preserve `architecture-review-required`
  when already set, otherwise `open`).
- `## Needs User Decision` -> ledger status remains non-terminal (typically
  `open` or `accepted-fix-pending`); the orchestrator pauses for user
  decision before the next pass.

Cite the `ledger_id` for every proposed transition. If a finding cannot be
matched to an existing ledger entry, treat
that as a procedural failure: do not create a new entry and report the
mismatch under `## Skill Feedback` so the orchestrator can correct triage.

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
