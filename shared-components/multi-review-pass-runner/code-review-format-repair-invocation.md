# Code Review Format Repair

Your previous review completed, but its output did not conform to the required
schema.

Do not repeat the review or inspect the repository again. Preserve the existing
analysis, findings, severities, finding IDs, evidence, and recommendations.
Reformat or complete that response using the exact seven-section structure
below. You may add only information already established in your analysis. Do
not open new findings.

Write `- None` for an empty section. Include no preamble or trailing
commentary. Use exactly one proportionality line. End with exactly one
permitted status line.

```markdown
## Blockers
- [{finding_id}] [path/to/file.py:line] <finding> - In-scope failure: <scenario, contract, or rule> - Evidence: <citation> - Recommendation: <smallest fix>

## Should-fix
- [{finding_id}] [path/to/file.py:line] <finding> - In-scope failure: <scenario, contract, or rule> - Evidence: <citation> - Recommendation: <smallest fix>

## Nits
- [{finding_id}] [path/to/file.py:line] <finding> - Evidence: <citation> - Recommendation: <fix>

## Contradictions
- [{finding_id}] [path/to/file.py:line] <source conflict> - Evidence: <evidence> - Recommendation: <resolution>

## Related Existing Issues
- [{finding_id}] [path/to/file.py:line] <pre-existing issue> - Evidence: <evidence> - Recommendation: <follow-up or why it blocks>

## Proportionality
- <Proportionate - concise reason; or Not proportionate - finding IDs and concise reason>

## Skill Feedback
- <non-blocking workflow feedback>
```

End with exactly one:

- `Fix blockers before next pass`
- `Resolve contradictions`
- `Address findings before next pass`
- `Review pass clean`
