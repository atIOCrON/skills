# Cross-Pass Triage Ledger Protocol

The code-review orchestration run maintains a single cross-pass ledger of
material concerns at `<feature_dir>/<plan_slug>.reviews/code-review-triage-ledger.md`
with one row per distinct material concern:

```text
| ledger_id | phase | first_pass | last_pass | reviewers | concern (one line) | files | architecture source | status | resolution evidence |
```

The orchestrator owns ledger writes. It applies entry changes from
`code-review-triage` and status transitions proposed by `code-review-closure`.
Reviewers never write the ledger.

## Status Vocabulary

- Non-terminal statuses: `open`, `accepted-fix-pending`, `re-opened`,
  `recurring-escalation`, `architecture-review-required`. Any non-terminal
  entry blocks loop completion.
- Terminal statuses: `resolved`, `rejected`, `deferred-by-user`.

`ledger_id` values are shaped `ledger-NN`, assigned as the next sequential
integer when an entry is created.

Use `code`, `behavior`, or `patch_mechanics` for `phase`. Existing ledgers
without the column are `code`; add the column while preserving their values.

## Identity Matching

Before creating a new ledger entry for any material finding accepted or marked
as a contradiction in a pass, match against existing ledger entries by file
overlap and concern semantics -- the same root cause, not just overlapping
wording within the same phase. Reviewer identity, finding ID, and prose
differences do not break a match. A mechanics finding that establishes a
behavioral defect is routed to `behavior` before matching. Do not create ledger
entries for rejected nits, advisory comments,
non-material plan mismatches, or non-blocking related existing issues.

- On match: append the current pass number to `last_pass`, add the reviewer to
  `reviewers` if not already present, and update `concern` or `files` only if
  the new evidence broadens scope. Do not create a duplicate row.
- On no match: create a new entry with the next sequential `ledger_id`,
  `phase` equal to the current phase, `first_pass` and `last_pass` equal to the current pass, status `open`, and
  the smallest concern phrasing that captures the root cause.

Set `architecture source` to the branch-introduced coordinator, state machine,
retry system, lifecycle interception, or other architectural layer that caused
the finding; otherwise use `-`. When updating an older ledger without this
column, add it and preserve every existing value.

## Recurrence And Re-opening

If a matched entry's existing status is `resolved` or `rejected`, transition
it to `re-opened` and surface it in the current pass's triage output.
`re-opened` is non-terminal and blocks completion.

After applying identity matching for a pass, inspect every non-terminal entry.
Any non-terminal entry whose same-phase `last_pass - first_pass >= 2` (it
appeared in three or more passes in that phase) must be set to status
`recurring-escalation` and
surfaced in the triage output with a one-line user-decision prompt (resolve,
reject with evidence, defer, or continue investigating). The orchestrator
pauses for the user before the next pass starts.

Independently, if one architecture source causes newly discovered material
failure modes in two successive fresh discovery passes, set its non-terminal
entries to `architecture-review-required`. Stop local fixes before another
worker dispatch. Return to the design checkpoint and decide whether to remove
or simplify the machinery, split the slice, upgrade, use an upstream fix, or
choose another extension mechanism. This two-pass ratchet applies across
distinct findings with the same source; it does not wait for one concern to
recur in three passes.

## Consolidation

Create a consolidation group when three or more entries currently in status
`open` or `re-opened` cite the same module/file set or the same `docs/`
standard. Name the group after that module or standard. Produce a single
consolidated fix request that resolves the grouped entries together rather
than per-finding fix requests, and tag those entries in the
`resolution evidence` column with a shared `consolidation_group: <short-name>`
note.
