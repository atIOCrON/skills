# Patch-Mechanics Review

Review the final delivery mechanics for one behavior-approved Composer patch.
Do not repeat semantic code review or request behavioral coverage.

## Scope

Read the mechanics review pack. Confirm the pinned parent and review SHAs, the
clean behavior-review evidence, and the reviewed effective-tree identity.
Inspect only:

- package version and correct pristine or preceding-patch baseline;
- patch ownership, paths, hunk scope and context;
- registration, description, classification and order;
- strip level, tool identity, fuzz, offsets and rejects;
- strict replay and effective-tree equality; and
- unintended files, permissions, generated content or metadata.

An effective-tree mismatch is a blocker that returns the branch to behavior
review. Otherwise do not report semantic defects already represented by the
clean-reviewed effective tree. If a newly observed reachable behavioral defect
is independently established, report one blocker requiring behavior review;
do not expand this mechanics pass into a behavioral scan.

## Output

Use IDs `mechanics-p<pass>-<reviewer>-NN`. Write `- None` under empty sections.

```markdown
## Blockers
- [{finding_id}] [path:line] <mechanics defect> - In-scope failure: <delivery rule> - Evidence: <citation> - Recommendation: <smallest fix>

## Should-fix
- [{finding_id}] [path:line] <mechanics defect> - In-scope failure: <delivery rule> - Evidence: <citation> - Recommendation: <smallest fix>

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
