---
name: code-review
description: Review staged changes only before branching against docs/, codebase conventions, and data-engineering best practice. Use for code review, standards review, or pre-branch review. Do not modify code. Not for running the multi-pass review loop; use code-review-loop for that.
metadata:
  layer: capability
---

# Code Review

Review the git index first. Report defects and standards violations; do not edit files.

## Scope

Use:

```bash
git diff --cached --stat
git diff --cached --name-only
git diff --cached
```

If nothing is staged, stop. Ignore unstaged and untracked changes for the main
review. If a file also has unstaged edits, review `git show :<path>` and mention
the unstaged edits exist.

## Review Lenses

Review against:

- `docs/`: project standards. Always read:
  - the docs AGENTS.md labels as code standards and logging standards
- Codebase conventions: dominant nearby/repo patterns, especially where docs are silent or drifted.
- Data-engineering best practice: correctness, lineage, idempotency, performance, transactions, schema quality, data quality.

Then use `AGENTS.md` and `docs/*.md` to read any standards relevant to the staged diff. If docs, code conventions, or best practice conflict, cite the conflict under `Contradictions` unless the issue is plainly a bug.

Treat the plan as approved intent and scope, not a literal implementation
script. Do not report "does not match the plan" unless the staged diff changes
approved behavior, skips required verification, omits an in-scope deliverable,
or creates a concrete engineering risk.

You may report related pre-existing issues discovered while reviewing nearby
code or readers. Put them under `Related Existing Issues`. They do not block the
staged change unless the staged diff depends on, worsens, or should reasonably
fix that issue as part of the approved plan.

## Review Method

For each staged file:

1. Read the staged content.
2. Apply the relevant docs, especially checklist sections.
3. Compare against established repo patterns before calling convention issues.
4. Flag real bugs and data-engineering risks even when no doc names them.
5. Cite the doc section, code pattern evidence, or concrete bug evidence.

Severity: `blocker` for real bugs/safety/critical violations. Use
`should-fix` only for concrete defects, clear standards violations, missing
reader propagation, schema or contract risks, required verification gaps,
performance risks, or data-quality risks. Use `nit` for minor naming, wording,
formatting, or preference comments. Do not demand new tests unless a plan or
repo standard requires them.

## Output

Use the supplied reviewer slug to create stable finding IDs in the
code-review format defined in
`.agents/skills/orchestration-conventions/references/finding_ids.md`. If a
section has no findings, write exactly `- None`.

Use only the current staged diff, relevant docs, current code, and command
output you inspect yourself. Do not use findings, summaries, or conclusions from
previous passes. Do not edit files, run destructive commands, change branches,
commit, push, access credentials, or inspect unrelated private files.

```markdown
## Blockers
- [{finding_id}] [path/to/file.py:line] <finding> - Evidence: <citation> - Recommendation: <fix>

## Should-fix
- [{finding_id}] [path/to/file.py:line] <finding> - Evidence: <citation> - Recommendation: <fix>

## Nits
- [{finding_id}] [path/to/file.py:line] <finding> - Evidence: <citation> - Recommendation: <fix>

## Contradictions
- [{finding_id}] [path/to/file.py:line] <docs/convention/best-practice conflict> - Evidence: <evidence> - Recommendation: <resolution>

## Related Existing Issues
- [{finding_id}] [path/to/file.py:line] <pre-existing issue> - Evidence: <evidence> - Recommendation: <follow-up or why it blocks this staged change>

## Skill Feedback
- <non-blocking feedback about unclear instructions, output format, command friction, missing constraints, or confusing workflow>
```

If there is no skill feedback, write exactly `- None`.

End with exactly one final status line, in priority order:

- `Fix blockers before next pass`
- `Resolve contradictions`
- `Address findings before next pass`
- `Review pass clean`

Keep findings machine-actionable: staged-only, specific file and line, no
hedging, no PR summary, no unsolicited refactors, no broader plan edits, and no
unrelated cleanup. Put non-blocking follow-up architecture or nearby cleanup
under `Related Existing Issues` or `Skill Feedback`.
