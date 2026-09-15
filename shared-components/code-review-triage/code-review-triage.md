# Code Review Triage

Turn staged-diff review feedback into accepted fix requests or concise
rebuttals. Use this during `code-review-loop` passes. Do not edit
files.

## Inputs

Expect one or more review responses, the plan path when available, the current
pass number, the list of intended implementation files, and the cross-pass
triage ledger path
(`plans/<plan_slug>.reviews/code-review-triage-ledger.md`). If review responses
or the pass number are missing, ask for them.

Material finding and root cause are defined in
references/orchestration-definitions.md.

## Read First

1. Read the staged review scope:
   - `git diff --cached --stat`
   - `git diff --cached --name-only`
   - `git diff --cached`
2. Run `git status --short` and identify unrelated dirty files.
3. Read changed staged content with `git show :<path>` when a staged file also
   has unstaged edits.
4. Read the docs AGENTS.md labels as code standards and logging standards, and
   any `docs/` files directly relevant to the feedback.
5. Inspect nearby code patterns before accepting style or architecture claims.
6. Read the cross-pass triage ledger when it exists. On the first code-review
   pass of an orchestration run the ledger may not yet exist; in that case,
   create it with the schema header defined in
   `references/orchestration-triage-ledger-protocol.md`
   before adding entries.

Primary evidence is the staged diff. Do not inspect unstaged work unless the
user explicitly included it in the handoff or it is one of the intended
implementation files that may need an implementation-worker fix request.

## Triage Rules

- Treat reviewer comments as hypotheses, not instructions.
- Deduplicate overlapping comments before acting.
- Accept a finding only when its evidence meets the material-finding definition
  in `references/orchestration-definitions.md`.
- Reject findings that depend only on hypothetical future use,
  unsupported inputs, unplanned scale, or architecture preference.
- Cite conflicts among binding sources under `Contradictions` unless the
  finding is plainly wrong.
- Treat `Related Existing Issues` as non-blocking follow-ups unless the staged
  diff depends on, worsens, or should reasonably fix the issue as part of the
  approved plan.
- The plan's scope does not excuse a concrete defect in changed code, but a
  finding cannot add requirements beyond the approved acceptance conditions,
  binding rules, or affected contracts.
- General best practice may support a finding but cannot establish one alone.
- Do not add backward-compatibility shims, fallback defaults, speculative
  refactors, or unrelated cleanup.
- For accepted findings, write the smallest fix request that resolves the issue
  and preserves the implementer's intent.
- If a fix needs an unplanned deliverable or unauthorized complexity, pause for
  a user decision instead of sending it to the worker.
- Batch all accepted material findings for the same implementer into one
  handoff. Do not routinely accept, fix, or close nits.
- Leave unrelated dirty files unstaged.

Resolve contradictions in this order: binding safety, security, legal, and
policy requirements; approved acceptance conditions and scope; applicable
repository standards; affected contracts; nearby conventions. General best
practice is advisory. Ask the user when higher-ranked sources conflict or a
resolution would expand scope.

## Cross-Pass Triage Ledger

Create or update the ledger at
`plans/<plan_slug>.reviews/code-review-triage-ledger.md` every pass. The
ledger schema, status vocabulary, identity matching, recurrence,
consolidation, and writer rules are defined in
`references/orchestration-triage-ledger-protocol.md`;
surface re-opened entries under `## Re-opened Concerns` and recurring escalations under
`## Recurring Escalations` in this pass's triage output.

## Handoff

Do not apply fixes, edit code or doc files, run formatters, stage files, or
restage files. The cross-pass triage ledger
(`plans/<plan_slug>.reviews/code-review-triage-ledger.md`) is the only file
triage may write; treat that as a triage artifact, not a code change. Accepted
fixes are sent to the implementation worker through `implementation-dispatch`.

For each accepted finding, identify:

- finding ID and reviewer,
- intended file or module owner,
- required change,
- evidence that the change is needed,
- verification or focused check that should run after the worker applies it.

## Output

Keep it short.

```markdown
## Accepted Fix Requests
- [{finding_id}] [{ledger_id}] <file/module owner> - <required worker change> - In-scope failure: <scenario, affected contract, or binding rule> - Evidence: <citation> - Verify: <command/check>

## Rejected
- [{finding_id}] [{ledger_id}] <reason/counter-argument with evidence>

## Contradictions
- [{finding_id}] [{ledger_id}] <docs/convention/best-practice conflict> - <evidence/resolution>

## Re-opened Concerns
- [{ledger_id}] <prior terminal status> - <why this pass re-opened it>

## Recurring Escalations
- [{ledger_id}] first_pass=<p> last_pass=<p> - <one-line user-decision prompt>

## Ledger Writes This Pass
- added: <ledger_id>, ...
- updated: <ledger_id> (<old_status> -> <new_status>), ...
- consolidation groups: <name>: <ledger_id>, ...
- recurring escalations: <ledger_id>, ...

## Worker Handoff
- <concise payload to send through references/implementation-dispatch-fix-request.md, or None>
```

Use `- None` under any section that has no entries this pass. Use
`[no-ledger]` in place of `[{ledger_id}]` for rejected nits, advisory
comments, non-material plan mismatches, and non-blocking related existing
issues. Do not edit files other than the
cross-pass triage ledger; ledger updates are the only file write triage
performs.

End with exactly one:

- `Resolve contradictions`
- `Ready for worker fixes`
- `Partial - blocker encountered`
- `Recurring escalations - user decision required`
- `No code changes needed`
