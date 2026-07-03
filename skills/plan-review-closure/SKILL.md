---
name: plan-review-closure
description: Check whether previously raised plan-review findings are resolved by plan edits, rejected with sufficient evidence, or still open. Used by plan-review-loop after plan-review triage.
metadata:
  layer: capability
---

# Plan Review Closure

Check closure for plan-review findings that this reviewer previously raised. Do
not perform a fresh review and do not raise new findings.

## Inputs

Require:

- original review artifact path,
- reviewer session artifact path,
- triage summary,
- applied plan edits and rejected findings,
- plan path.

## Scope

- Assess only findings from the original plan-review artifact.
- This closure is expected to run in the same reviewer conversation/session that
  produced the original review artifact. If it is not the same conversation,
  report that as `Closure blocked` rather than doing a fresh review.
- For accepted findings, decide whether the applied plan edit resolves the
  finding.
- For rejected findings, decide whether the rejection evidence is sufficient.
- Use evidence from the plan, cited docs, cited code, or gold-standard
  data-engineering best practice.
- Do not edit files.
- Do not assess implementation code or staged diffs.
- Do not inspect unrelated files.
- Do not use findings, summaries, or conclusions from other reviewers unless
  they are included in the triage summary.

## Output

```markdown
## Resolved
- [{finding_id}] <why the plan edit resolves it>

## Rejection Accepted
- [{finding_id}] <why the rejection evidence is sufficient>

## Still Open
- [{finding_id}] <what remains unresolved and what evidence supports that>

## Needs User Decision
- [{finding_id}] <why evidence is insufficient or product intent is required>

## Skill Feedback
- <non-blocking feedback>
```

If there is no skill feedback, write exactly `- None`.

End with exactly one:

- `Closure confirmed`
- `Closure blocked`
