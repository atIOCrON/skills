# Code Review

Independently review one immutable plan-branch commit against pinned parent; no edits.
Read neutral pack and confirm:

```bash
git diff --stat <base-sha>...<review-sha>
git diff --name-only <base-sha>...<review-sha>
git diff <base-sha>...<review-sha>
git rev-parse <review-sha>^{commit}
git merge-base --is-ancestor <base-sha> <review-sha>
```

Read committed content via `git show "${R}:path/to/file"` with full review SHA in R;
quote object expressions in zsh. Ignore index/worktree. Stop on empty diff, unresolved
SHA, bad ancestry or pack/object mismatch. Inspect every changed file and affected
entry point/reader/transition/invariant; exhaust independent defects after first blocker.

Use approved slice intent, relevant AGENTS/repo docs/config/tests/contracts and nearby
patterns. Best practice informs, never expands scope or establishes binding policy.
Plan mismatch is material only for changed approved behavior, missing deliverable/
verification or concrete risk. Report binding conflicts as Contradictions; existing
issues separately, blocking only if depended on/worsened or required by plan.

Judge correctness and proportionality separately. Material excess includes unauthorized
layers, duplicate native ownership, separable outcomes, checkpoint excess, disproportionate
harnesses or structural-only proof of newly owned runtime behavior. Distinguish routing/
config/reachability from unchanged upstream lifecycles; fake state transitions prove no
production lifecycle. Prefer removal/simplification/split/upgrade/narrow extension to guards.

Respect the pack's verification phases. Focused branch implementation proof gates
this review; pending assembled-runtime, cross-feature, deployed-asset or full
storefront/Admin/cache/provider acceptance belongs to release/staging, even when
agent-run. Missing later evidence alone is no code defect. Report proven defects
normally, preserve explicit user/repository branch gates, and justify any demand
for a full environment over cheaper sufficient implementation proof.

Blocker/should-fix needs `reproduced` (pinned SHA, supported production-like path using
existing facilities) or `binding-proof` (committed code plus binding contract/policy/
standard deductively proves failure). Static plausibility, unsupported inputs, imagined
sequences/scale/future needs and architecture preferences are no findings; nonblocking
workflow advice belongs in feedback. Allow one bounded existing-facility reproduction
cycle; never require new provider simulators, generalized delay/lifecycle machinery,
production guards or substantial harness to establish a hypothesis.

Recommend smallest sufficient fix; identify new surface as prerequisite versus independent
capability. Blockers mean security/safety/data loss/required-outcome failure; other material
defects are should-fix, preferences nits. Require proportionate regressions for owned
behavior, never unrelated coverage or local reconstruction of unchanged dependency lifecycles.

## Output

Use the supplied reviewer slug and canonical finding IDs. Write `- None` under
empty sections.

```markdown
## Blockers
- [{finding_id}] [path/to/file.py:line] <finding> - Failure family: <invariant / runtime owner / supported path / observable failure> - Evidence class: <reproduced|binding-proof> - Pinned SHA: <40-character review SHA> - Supported path: <normal supported operation> - Existing facilities only: yes - Evidence: <Reproduction: command or procedure; Artifact: path; Observed: result | Proof: binding source; Chain: deduction> - Recommendation: <smallest fix>

## Should-fix
- [{finding_id}] [path/to/file.py:line] <finding> - Failure family: <invariant / runtime owner / supported path / observable failure> - Evidence class: <reproduced|binding-proof> - Pinned SHA: <40-character review SHA> - Supported path: <normal supported operation> - Existing facilities only: yes - Evidence: <Reproduction: command or procedure; Artifact: path; Observed: result | Proof: binding source; Chain: deduction> - Recommendation: <smallest fix>

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
