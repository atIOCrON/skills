# Code Review

Review one pinned plan-branch commit against its pinned dependency-parent SHA.
Do not edit files.

## Scope

Read the neutral review pack, then independently confirm:

```bash
git diff --stat <base-sha>...<review-sha>
git diff --name-only <base-sha>...<review-sha>
git diff <base-sha>...<review-sha>
git rev-parse <review-sha>^{commit}
git merge-base --is-ancestor <base-sha> <review-sha>
```

Use only explicit SHAs. Ignore the index and working tree. Read committed file
content with `git show "${R}:path/to/file"` after setting `R` to the full review
SHA; quote the entire object expression in zsh. Stop if the diff is
empty, either SHA is unresolved, ancestry is wrong, or the pack does not match
the resolved objects.

## Review Lenses

Review against the approved plan, applicable repository standards, affected
contracts, established nearby patterns, and engineering principles relevant to
the touched surface. Read applicable `AGENTS.md` files when present. Otherwise
use the plan, repository docs and configuration, tests, and affected contracts
as sources of project-specific standards.

General best practice may support a finding but cannot expand scope. Report a
binding-source conflict under `Contradictions`. Treat the plan as approved
intent, not a literal script. A plan mismatch is material only when it changes
approved behavior, omits an in-scope deliverable, skips required verification,
or creates a concrete risk.

Place nearby pre-existing issues under `Related Existing Issues`; they block
only when this change depends on or worsens them, or the plan requires them.

## Review Method

Inspect every changed file, affected entry point, reader, state transition, and
surrounding invariant. Continue after the first blocker and report every
independent material defect established in this pass.

Assess two questions separately:

1. Is the implementation correct for the approved slice and its contracts?
2. Is it proportionate and aligned with the platform's native ownership model?

A proportionality problem is material when the branch introduces an
unauthorized architectural layer, duplicates upstream or platform ownership,
combines independently releasable responsibilities, materially exceeds its
design checkpoint, or relies on source-shape assertions for runtime behaviour.
Do not treat mere style or architecture preference as a defect. Recommend
simplifying, splitting, upgrading, or using a narrower extension mechanism
before adding guards to new machinery.

A blocker or should-fix must establish a reachable supported failure, an
affected-contract regression, or a binding policy or repository-standard
violation. Unsupported inputs, hypothetical scale, future use, and architecture
preferences are advisory. Recommend the smallest sufficient fix; identify any
unplanned deliverable that needs user approval.

Use `blocker` for safety, security, data loss, or failure of a required outcome;
`should-fix` for other material defects; and `nit` for preferences. Require
proportionate regression tests for changed behavior even when the plan omits
them; do not demand unrelated coverage expansion.

## Output

Use the supplied reviewer slug and canonical finding IDs. Write `- None` under
empty sections.

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
- <Proportionate - native owner, extension mechanism, and behavioural evidence; or Not proportionate - finding IDs and concise reason>

## Skill Feedback
- <non-blocking workflow feedback>
```

End with exactly one:

- `Fix blockers before next pass`
- `Resolve contradictions`
- `Address findings before next pass`
- `Review pass clean`

Use `Address findings before next pass` only for should-fix findings. Keep the
response machine-actionable, commit-pinned, specific, and concise. Output only
the seven sections and status line. Use exactly one proportionality line.
