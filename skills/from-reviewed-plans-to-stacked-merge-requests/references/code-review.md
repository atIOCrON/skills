# Code Review

Review every staged file for in-scope defects and standards violations. Do not
edit files.

## Scope

Use:

```bash
git diff --cached --stat
git diff --cached --name-only
git diff --cached
```

Read the supplied neutral review pack. Use its deterministic evidence for
scope, hashes, ancestry, patch application, and byte comparisons; rerun those
read-only commands when independent confirmation is useful.

If nothing is staged, stop. Ignore unstaged and untracked changes for the main
review. If a file also has unstaged edits, review `git show :<path>` and mention
the unstaged edits exist.

## Review Lenses

Review against:

- The plan's acceptance conditions and scope boundaries.
- `docs/`: project standards. Always read:
  - the docs AGENTS.md labels as code standards and logging standards
- Affected code contracts.
- Dominant nearby or repository patterns where standards are silent.
- Engineering principles relevant to the touched surface.

Use `AGENTS.md` and `docs/*.md` to read standards relevant to the staged diff.
General best practice may support a finding but cannot expand scope or require
new capability by itself. Report a conflict among binding sources under
`Contradictions` unless it is plainly a bug.

Treat the plan as approved intent and scope, not a literal implementation
script. Do not report "does not match the plan" unless the staged diff changes
approved behavior, skips required verification, omits an in-scope deliverable,
or creates a concrete engineering risk.

You may report related pre-existing issues discovered while reviewing nearby
code or readers. Put them under `Related Existing Issues`. They do not block the
staged change unless the staged diff depends on or worsens them, or the plan
requires their correction.

## Review Method

For each staged file:

1. Read the staged content.
2. Apply the relevant docs, especially checklist sections.
3. Compare against established repo patterns before calling convention issues.
4. Flag concrete bugs and risks on the touched surface even when no doc names
   them.
5. Cite the doc section, code pattern evidence, or concrete bug evidence.

Continue after finding a blocker. Inspect every staged file, affected entry
point, reader, state transition, and surrounding invariant, then report all
independent material defects established in this pass. Do not stop at the first
finding or defer an evident defect to a later pass.

A blocker or should-fix finding must establish at least one of:

- a reachable failure under the plan's supported conditions;
- a demonstrated regression in an affected contract; or
- a violation of an applicable binding policy or repository standard.

Hypothetical future use, unsupported inputs, unplanned scale, and architecture
preferences are advisory. Do not present them as defects. Recommend the
smallest fix that closes the established failure. If it requires an unplanned
deliverable, say that user approval is required.

Use `blocker` for safety, security, data loss, or failure of a required outcome.
Use `should-fix` for other material findings. Use `nit` for naming, wording,
formatting, or preferences. Do not demand new tests unless the plan or an
applicable repository standard requires them.

## Output

Use the supplied reviewer slug to create stable finding IDs in the
code-review format defined in
`references/orchestration-finding-ids.md`. If a
section has no findings, write exactly `- None`.

Use only the current staged diff, relevant docs, current code, and command
output you inspect yourself. Do not use findings, summaries, or conclusions from
previous passes. Do not edit files, run destructive commands, change branches,
commit, push, access credentials, or inspect unrelated private files.

```markdown
## Blockers
- [{finding_id}] [path/to/file.py:line] <finding> - In-scope failure: <scenario, affected contract, or binding rule> - Evidence: <citation> - Recommendation: <smallest fix>

## Should-fix
- [{finding_id}] [path/to/file.py:line] <finding> - In-scope failure: <scenario, affected contract, or binding rule> - Evidence: <citation> - Recommendation: <smallest fix>

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

Use `Address findings before next pass` only when `Should-fix` contains a
finding. Nits, related existing issues, and skill feedback are advisory and may
end with `Review pass clean`.

Keep findings machine-actionable: staged-only, specific file and line, no
hedging, no PR summary, no unsolicited refactors, no broader plan edits, and no
unrelated cleanup. Put non-blocking follow-up architecture or nearby cleanup
under `Related Existing Issues` or `Skill Feedback`.

Output only the six required sections and the status line. Do not narrate the
review method or list properties that passed. Keep evidence and recommendations
concise; a clean review uses `- None` in each section.
