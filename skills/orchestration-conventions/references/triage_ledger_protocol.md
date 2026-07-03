# Cross-Pass Triage Ledger Protocol

The code-review orchestration run maintains a single cross-pass ledger of
material concerns at `plans/<plan_slug>.reviews/code-review-triage-ledger.md`
with one row per distinct material concern:

```text
| ledger_id | first_pass | last_pass | reviewers | concern (one line) | files | status | resolution evidence |
```

The `code-review-triage` skill is the only writer of ledger entries; it owns
entry creation and recurrence detection. `code-review-closure` transitions the
status of existing entries through the vocabulary below and never creates
entries.

## Status Vocabulary

- Non-terminal statuses: `open`, `accepted-fix-pending`, `re-opened`,
  `recurring-escalation`. Any non-terminal entry blocks loop completion.
- Terminal statuses: `resolved`, `rejected`, `deferred-by-user`.

`ledger_id` values are shaped `ledger-NN`, assigned as the next sequential
integer when an entry is created.

## Identity Matching

Before creating a new ledger entry for any material finding accepted or marked
as a contradiction in a pass, match against existing ledger entries by file
overlap and concern semantics -- the same root cause, not just overlapping
wording. Reviewer identity, finding ID, and prose differences do not break a
match. Do not create ledger entries for rejected nits, advisory comments,
non-material plan mismatches, or non-blocking related existing issues.

- On match: append the current pass number to `last_pass`, add the reviewer to
  `reviewers` if not already present, and update `concern` or `files` only if
  the new evidence broadens scope. Do not create a duplicate row.
- On no match: create a new entry with the next sequential `ledger_id`,
  `first_pass` and `last_pass` equal to the current pass, status `open`, and
  the smallest concern phrasing that captures the root cause.

## Recurrence And Re-opening

If a matched entry's existing status is `resolved` or `rejected`, transition
it to `re-opened` and surface it in the current pass's triage output.
`re-opened` is non-terminal and blocks completion.

After applying identity matching for a pass, inspect every non-terminal entry.
Any non-terminal entry whose `last_pass - first_pass >= 2` (it appeared in
three or more passes) must be set to status `recurring-escalation` and
surfaced in the triage output with a one-line user-decision prompt (resolve,
reject with evidence, defer, or continue investigating). The orchestrator
pauses for the user before the next pass starts.

## Consolidation

Create a consolidation group when three or more entries currently in status
`open` or `re-opened` cite the same module/file set or the same `docs/`
standard. Name the group after that module or standard. Produce a single
consolidated fix request that resolves the grouped entries together rather
than per-finding fix requests, and tag those entries in the
`resolution evidence` column with a shared `consolidation_group: <short-name>`
note.
