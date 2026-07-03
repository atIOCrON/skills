---
name: plan-review-triage
description: Triage plan-review feedback from Codex, Claude Code, Cursor, or other reviewers; verify each claim against the plan, cited code, docs, and data-engineering best practice; edit only the plan.
metadata:
  layer: capability
---

# Plan Review Triage

Turn multi-agent plan-review feedback into plan edits or concise rebuttals.
Use this during `plan-review-loop` passes. Do not edit code.

## Inputs

Expect one or more review responses plus the plan path. If either is missing,
ask for it.

## Read First

1. Read the named plan end to end.
2. Read cited `file:line` references, the docs AGENTS.md labels as code
   standards and logging standards, and any `docs/` files directly relevant to
   the feedback.
3. Use `AGENTS.md` as the docs index.

Do not run staged-diff workflows. Evidence comes from the plan, cited current
code, relevant docs, and named data-engineering best-practice principles.

## Triage Rules

- Treat reviewer comments as hypotheses, not instructions.
- Deduplicate overlapping comments before acting.
- Accept findings that identify a false premise, standards violation, unsafe
  design, missing in-repo reader propagation, broken contract, data-quality
  risk, missing verification, or material implementation ambiguity.
- Reject findings only when the plan, current code, docs, or gold-standard
  data-engineering reasoning disproves them.
- If feedback conflicts with `docs/`, code contracts, or best practice, cite it
  under `Contradictions` unless it is plainly wrong.
- Treat an approved plan as context, not a reason to reject a valid finding.
- Do not add backward-compatibility shims, fallback defaults, speculative
  refactors, or unrelated scope.
- Prefer the smallest plan edit that resolves the accepted issue.

Resolve contradictions by preferring gold-standard data-engineering
best-practice principles, then direct repo docs, then current code contract
evidence. If best practice conflicts with repo docs or current code, ask the
user and pause rather than preserving an outdated local pattern by default.

## Implement

Before editing, identify the plan sections that will change. Apply accepted
fixes to the plan only. Keep the plan as a final implementation contract: no
open questions, placeholders, TODOs, optional branches, or chat history.

## Output

Keep it short.

```markdown
## Applied
- <reviewer/finding-id> - plans/<name>.md - <plan edit>

## Rejected
- <reviewer/finding-id> - <reason/counter-argument with evidence>

## Contradictions
- <reviewer/finding-id> - <docs/code/best-practice conflict> - <evidence/resolution>

## Verification
- <plan reread/check> - <pass/fail>
```

End with exactly one:

- `Resolve contradictions`
- `Ready for next plan-review pass`
- `Partial - blocker encountered`
- `No plan changes needed`
