# Artefact Audit at Branch Handoff

Audit the selected features after their agent-run branch and stack checks pass,
their artefacts are preserved under `plans/review/<slug>/`, and the stack
manifest records the reviewed and tested SHAs. On a repair run, re-audit
affected features and descendants whose evidence or code snapshot changed.
Human or external acceptance may still be pending; record it separately from
the audit's follow-up planning decisions.
The audit creates planning files in the user's primary checkout; it does not
change verified commits, push branches, or open change requests.

## Find and verify candidates

For each feature, read its plan and available `<slug>.reviews/`,
`<slug>.execution/`, and `<slug>.evidence/`. Inspect the cross-pass
`code-review-triage-ledger.md`, latest `triage.md`, and reviewer or worker notes
about related existing issues, follow-ups, out-of-scope work, deferrals,
rejections, or open concerns. The review triage ledger records review-pass
status; it is not the follow-up planning ledger. Advisory notes are candidates,
not accepted findings. Group repeated notes by underlying problem.

Verify each candidate with targeted reads and small read-only checks against
the tested stack state: the latest verified chain head for a dependency chain,
or the tested temporary integration commit for an ordered independent batch.
Use an exact verified feature tip when no combined snapshot exists. Record the
SHA actually checked and mark a cross-branch question pending if no tested
snapshot can resolve it. Do not describe unmerged branch code as merged code.
Check existing plans across all stages and legacy `plans/<slug>.md` files in
the tested snapshot and primary checkout for an equivalent outcome.

Create a new plan only when the work is still needed, specific enough to
define an outcome, substantial enough for the planning workflow, and not
already covered. Do not turn a rejected or deferred review finding into a plan
solely because it appears in an artefact. If evidence is insufficient, record
what remains unknown rather than inventing a plan. A demonstrated acceptance
failure, an unimplemented acceptance condition, or an unresolved material
review finding is a current-plan fix:
return the affected feature and descendants to `in_progress/` for verification
and review, then repeat final checks, manifest refresh, and audit before
handoff. Do not move that gap to the backlog. A pending external check alone is
not a current-plan fix.

## Decision ledger and plans

Use `<feature_dir>/<slug>.reviews/artefact-audit-ledger.md` for each feature.
Create it on that feature's first audit if absent. Record its verified tip SHA,
audit snapshot SHA, audit date, artefact paths reviewed, and one row per
distinct candidate:

```text
| Candidate | Source artefact | Current-code evidence | Decision | Reason | Plan slug |
```

Use `planned`, `not planned`, `current-plan fix`, or `pending` for the decision.
Explain why each candidate received that decision, including resolved issues,
duplicates, existing-plan coverage, advisory-only notes, and work too vague or
minor to plan. Record an existing plan's slug when it already covers the
candidate; use `none` when no plan covers it. If no candidates were found,
record that fact and the artefacts checked. On a rerun, update that feature's
ledger and reconcile existing plans; do not append duplicate rows or plans.
Refer to source artefacts by feature-relative path so later stage moves preserve the
references. Refer to a follow-up plan by its slug.

For each `planned` candidate, create a unique lowercase snake_case feature at
`plans/backlog/<slug>/<slug>.md`, following the repository's plan conventions.
State the observed problem and evidence, minimum outcome, scope and non-goals,
and observable acceptance conditions. Include the source feature, candidate,
verified tip SHA, and audit snapshot SHA so the plan can be traced to the
decision. Translate review suggestions into required outcomes unless a
mechanism is itself a binding constraint. Do not implement these plans or
move them out of `backlog/` here.

Write the ledgers and plans in the user's primary checkout, not a temporary
verification worktree. Preserve unrelated work and keep these new files out
of the already verified branch tips. If a destination collides or cannot be
written safely, record the candidate as pending and report the blocker. If a
repair makes a previously generated plan obsolete, reconcile only a plan
still in `backlog/` and untouched since the audit; otherwise report that the
plan needs a scope decision. Branch readiness survives an audit write failure,
but report the audit as incomplete until every selected feature has a ledger
and warranted plans exist.
