# Behavior Review

Review one pinned Composer-patch branch for behavior. Do not edit files or
review patch-delivery mechanics.

## Scope

Read the behavior review pack. Confirm the pinned parent and review SHAs, then
inspect:

- the baseline-to-effective package source diff;
- relevant project runtime code and contracts;
- existing or approved verification evidence; and
- affected entry points, state transitions and consumers.

The committed patch must strictly replay to the effective tree. Stop if that
identity proof is missing or mismatched. Otherwise do not review patch format,
hunk context, registration, descriptions, ordering, strip level or replay-log
quality; the later patch-mechanics phase owns them.

## Method

Assess correctness, supported failure paths, and proportionality against the
approved plan and affected contracts. Continue after the first blocker. A
material finding must establish a reachable supported failure, contract
regression, or binding-policy violation. Keep unsupported inputs, preferences,
and future concerns advisory.

Require the smallest sufficient evidence. Prefer an existing test or fixture.
Do not require a new custom harness unless the plan records the user's explicit
approval; recommend external acceptance or a smaller reliable seam otherwise.

## Output

Use IDs `behavior-p<pass>-<reviewer>-NN`. Write `- None` under empty sections.

```markdown
## Blockers
- [{finding_id}] [path:line] <finding> - In-scope failure: <scenario or contract> - Evidence: <citation> - Recommendation: <smallest fix>

## Should-fix
- [{finding_id}] [path:line] <finding> - In-scope failure: <scenario or contract> - Evidence: <citation> - Recommendation: <smallest fix>

## Nits
- [{finding_id}] [path:line] <finding> - Evidence: <citation> - Recommendation: <fix>

## Contradictions
- [{finding_id}] [path:line] <source conflict> - Evidence: <evidence> - Recommendation: <resolution>

## Related Existing Issues
- [{finding_id}] [path:line] <issue> - Evidence: <evidence> - Recommendation: <follow-up>

## Proportionality
- <Proportionate, or finding IDs and concise reason>

## Skill Feedback
- <non-blocking workflow feedback>
```

End with exactly one: `Fix blockers before next pass`, `Resolve contradictions`,
`Address findings before next pass`, or `Review pass clean`.
