# Code Review Triage

Turn commit-pinned review feedback into accepted fix requests or concise
rebuttals. Do not edit implementation files.

## Inputs

Require reviewer responses, plan path, pass number, intended implementation
scope, review base and commit SHAs, neutral pack, and cross-pass ledger path:
`plans/<plan_slug>.reviews/code-review-triage-ledger.md`.

## Read First

1. Confirm the pack's SHAs, ancestry, diff, verification evidence, and branch
   identity checks.
2. Read `git diff <base-sha>...<review-sha>` and committed content at
   `<review-sha>`; ignore the index and working tree.
3. Read applicable standards and nearby patterns.
4. Read or initialize the ledger using
   `references/orchestration-triage-ledger-protocol.md`.

## Rules

- Treat comments as hypotheses; deduplicate them before acting.
- Accept only findings that meet the material-finding definition.
- Reject claims based only on unsupported inputs, hypothetical scale, future
  use, or architecture preference.
- General best practice cannot establish a defect alone.
- A pre-existing issue blocks only when this commit depends on or worsens it,
  or the plan requires its correction.
- Recommend the smallest in-scope fix. Ask the user before adding an unplanned
  deliverable or complexity.
- Batch material findings for one implementer. Do not routinely fix nits.
- Do not stage, commit, push, or inspect unrelated dirty work.

Resolve source conflicts in this order: safety, security, legal, and policy;
approved scope; repository standards; affected contracts; nearby conventions;
general best practice. Ask the user when a higher-ranked conflict or scope
expansion remains.

## Ledger And Handoff

The ledger is the only file triage may write. Apply its canonical identity,
status, recurrence, and consolidation rules. Send accepted fixes through
`implementation-dispatch`, including finding ID, owner, required change,
evidence, and the verification check. The worker must produce a new candidate
commit; fixes never mutate the reviewed SHA.

## Output

```markdown
## Accepted Fix Requests
- [{finding_id}] [{ledger_id}] <owner> - <required change> - In-scope failure: <scenario, contract, or rule> - Evidence: <citation> - Verify: <check>

## Rejected
- [{finding_id}] [{ledger_id}] <reason with evidence>

## Contradictions
- [{finding_id}] [{ledger_id}] <conflict> - <evidence/resolution>

## Re-opened Concerns
- [{ledger_id}] <prior status> - <reason>

## Recurring Escalations
- [{ledger_id}] first_pass=<p> last_pass=<p> - <user-decision prompt>

## Ledger Writes This Pass
- added: <ledger_id>, ...
- updated: <ledger_id> (<old_status> -> <new_status>), ...

## Worker Handoff
- <concise fix payload, or None>
```

Use `- None` for empty sections and `[no-ledger]` for non-material items. End
with exactly one: `Resolve contradictions`, `Ready for worker fixes`,
`Partial - blocker encountered`, `Recurring escalations - user decision
required`, or `No code changes needed`.
