# Cross-Pass Triage Ledger Protocol

The code-review orchestration run maintains a single cross-pass ledger at
`<feature_dir>/<plan_slug>.reviews/code-review-triage-ledger.md`. Its concern
table has one row per distinct material concern:

```text
| ledger_id | first_pass | last_pass | reviewers | concern (one line) | files | architecture source | status | resolution evidence |
```

Its family table tracks recurrence across implementation shapes and epochs:

```text
| family_id | invariant / runtime owner / supported path / observable failure | first_pass | last_pass | accepted_fix_cycles | epochs | disposition |
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

## Identity Matching

Before creating a ledger entry, match the finding against every concern and
failure family from every prior pass and epoch. Match a family by its invariant,
runtime owner, supported path, and observable failure. Reviewer identity,
finding ID, wording, files, implementation shape, and epoch do not break a
match. Match a concern by root cause within that family. Do not create entries
for static hypotheses, rejected nits, advisory comments, non-material plan
mismatches, non-blocking related issues, closure observations, or skill
feedback.

- On match: append the current pass number to `last_pass`, add the reviewer to
  `reviewers` if not already present, and update `concern` or `files` only if
  the new evidence broadens scope. Do not create a duplicate row.
- On no match: create a new entry with the next sequential `ledger_id`,
  `first_pass` and `last_pass` equal to the current pass, status `open`, and
  the smallest concern phrasing that captures the root cause.

Assign `family_id` values as `family-NN`. On an accepted worker dispatch,
increment that family's `accepted_fix_cycles`. Record every architecture epoch
used to address it. Changing files or design does not reset either count.

Set `architecture source` to the branch-introduced coordinator, state machine,
retry system, lifecycle interception, verification model, or other architectural
layer that caused the finding; otherwise use `-`. When updating an older ledger
without this column, add it and preserve every existing value.

## Recurrence And Re-opening

If a matched entry's existing status is `resolved` or `rejected`, transition
it to `re-opened` and surface it in the current pass's triage output.
`re-opened` is non-terminal and blocks completion.

After applying identity matching for a pass, inspect every non-terminal entry.
Any non-terminal entry whose `last_pass - first_pass >= 2` (it appeared in
three or more passes) must be set to status `recurring-escalation` and
surfaced in the triage output with a one-line root-cause or architecture action.
This is an internal escalation to the orchestrator and design checkpoint. It
blocks review completion, not further work: reassess the root cause and continue
unless the decision changes approved product scope or needs external authority.

Independently, if one failure family or architecture source causes newly
discovered material failure modes in any two fresh discovery passes recorded
in the ledger, set its non-terminal entries to `architecture-review-required`.
Stop incremental fixes before
another worker dispatch. Return to the design checkpoint; group failures by
invariant; compare removal, simplification, native ownership, upgrade, narrow
dependency correction, and prerequisite splitting; then record the selected
design as a new architecture epoch and continue. Record the epoch number and
prior failure class in `resolution evidence`. This two-pass ratchet applies
across distinct findings, implementation shapes, and epochs; it does not wait
for consecutive passes or one concern to recur three times.

If two epochs fail for the same underlying reason, do not try a third variation
of that mechanism. Select a fundamentally different owner or mechanism, or
block the affected chain when no option can satisfy the approved outcome and
hard constraints.

## Autonomous Continuation Decision

Record a decision after two accepted fix cycles in one family. Include the
trigger, confirmed evidence, rejected hypotheses, related fixes and epochs,
removal or simplification options, native owner, upgrade, narrow dependency
correction, prerequisite split, decision, and one authorized next action.

After two family fix cycles, do not authorize another local variation. Choose
`reject`, `complete`, `redesign`, `change-owner`, `upgrade`,
`dependency-correction`, `split`, or `blocked-authority`. Continue only for a
confirmed material defect with a viable, non-repeated disposition. Ask the user
only when every viable option crosses the calling skill's authority boundary.
One decision authorizes at most one edit-and-pass cycle for that failure family.

## Review Pass Cap

After the fifth completed discovery pass, add a durable marker to the ledger:

```text
## Review Cap
- status: review_cap_reached
- limit: 5
- completed_passes: 5
- last_reviewed_sha: <full SHA>
- current_verified_sha: <full SHA>
- remaining_review_requirement: <why completion still needs another discovery pass>
```

The cap marker is a plan-level workflow outcome, not a finding status or a
whole-run blocker. Keep non-terminal concern rows unchanged and do not start
pass 6. The caller finishes accepted fixes and closure, verifies and pushes the
tip, then moves the slice to `review/` if trim is proportionate and branch
checks pass. Record unresolved findings for a separate human disposition.
Dependent work may continue on the verified pinned tip.

## Consolidation

Create a consolidation group when three or more `open` or `re-opened` entries
share a failure family or binding standard. Name the group after that family or
standard. Produce one fix request for the group, and tag its entries in the
`resolution evidence` column with a shared `consolidation_group: <short-name>`
note.
