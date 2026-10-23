# Trim Review

Existing owner trims verified pushed pinned parent-to-tip diff before correctness.
Prepared work stays schedule.work/in_progress until acceptance. Run branches to
reviewer capacity; moving ancestors leave reviews provisional, not blocked.
Apply queue/scheduling for leases/isolation and git-sync-branch for provisional
expected-state push/parent ancestry. Restack after upstream settles/intended parent
available.

Read plan/checkpoint/pack/AGENTS/testing/CI policy/nearby tests. Nearby patterns are
not binding. Keep required tests and smallest owned-behavior proof. Fresh parallel
Claude/Codex/Cursor use matching native host/preflighted other CLIs and runner
artifact/mutation rules, no reused correctness verdict. Trim has its own format;
correctness serialization helper does not validate it. Check sections/pins/evidence,
repair omissions same session. Save prompts/raw/accepted/session data under
`<feature_dir>/<slug>.reviews/trim-review-pass<N>/`.

## Reviewer prompt

```text
Review phase: trim. Reviewer: <slug>. Trim pass: <N>.
Repository: <root>. Plan: <path>. Neutral pack: <path>.
Pinned parent SHA: <full SHA>. Verified branch tip: <full SHA>.

Confirm SHAs/ancestry/diff agree with pack; stop on failure. Review only pinned diff
under project/testing policy. Find removable complexity retaining approved behavior,
binding checks and meaningful owned-behavior proof: duplicate/low-signal tests,
oversized fixtures, fake provider/server/persistence lifecycles, broad mocks,
redundant abstractions, speculative compatibility or disproportionate harnesses.
Shorter code/test counts alone justify nothing. Do not review correctness or mark
it clean; separate obvious concerns for later. Cite changed path and policy/
duplication/ownership evidence, smallest reduction and remaining proof; say if none.

## Trim findings
- [<slug>-trim-p<N>-<NN>] [path:line] <removable complexity> - Evidence: <specific source or comparison> - Reduction: <smallest change> - Retained proof: <test, check, or binding policy evidence>
## Policy conflicts
- <conflict and sources, or None>
## Correctness observations
- <observation for later review, or None>
## Trim result
- <Proportionate | Changes advised | Policy conflict>
```

Empty findings/observations use - None. Triage all three at pin into
`<feature_dir>/<slug>.reviews/trim-review-ledger.md`, accepting only concrete
in-scope reductions retaining required proof, recording rejections/reasons.
Leave proportionate code; correctness observations approve neither phase.

Existing owners fix earliest branch first via normal selective-stage/new-commit/
exact-check/coordinator-or-lease-push/remote-confirm/pack-refresh route. Within branch
finish triage/fix/push N before next trim; don't wait solely for ancestor restack.
Continue until no accepted reduction; same concern after two passes requires
root-cause/design reassessment. Trim adds no correctness pass.

Record UTC triage/reviewed pin/fix pin (pending until pushed, null only if none)/
next-pass reason (null if none)/current-mapped result/ledger path. Verified/pushed
pin, integrity or capacity may block, never ancestor movement alone. Return
operational-record receipts; coordinator imports/counts/validates, preserving
uncounted disqualifications. V1 tools apply only to historical records.

Carry proportionate trim through valid review-loop restack proof, or inspect every
resolved hunk/full old-new diff proving no added/reworked owned code/tests/config/
patch content, no new redundancy and unchanged effective identity. Record ranges/
hunks/pins/proof/conclusion and current trim pin. This preserves no correctness
review. Unexplained/change/uncertainty requires fresh trim, SHA change alone doesn't.
Start correctness when own trim qualifies; retain provisional parent coverage.
Later fixes repeat trim only for substantial new machinery/invalid carry-forward.
