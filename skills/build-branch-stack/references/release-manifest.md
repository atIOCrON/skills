# Build and Release Manifests

New/adopted canonical JSON uses `operational-records.md` and schema-v2 validation.
Keep one build at existing stable path (default plans/builds/<id>/manifest.json),
separate linked release preparation and deployment records. Resume existing paths,
never duplicate/move build evidence into releases. JSON owns state; Sheets/prose
are projections. Sessions preserve provenance, not proof of checks/reviews.
Build completion is branch checks/trim/correctness/placement; release preparation
owns selected candidate checks, acceptance and freeze.

## Current build metadata

Use extensions, not schema aliases:

| Location | Metadata |
| --- | --- |
| extensions.sessions | Coordinator/owner/reviewer history |
| schedule.extensions | Selection/layout/coordinator, spec order/rationale/current, accepted tail, capacity, pauses/exclusions |
| schedule.work[].extensions | Owner/checkout, authoring_base {branch,sha}, execution/publication lease, pause/resume, evidence, worker_completion, accepted pin |

Work statuses queued/implementing/prepared/stacked/complete/blocked remain distinct:
prepared = verified authoring pin, stacked = accepted verified pushed placement,
complete = own qualified/capped handoff too. Pause adds reason/condition without
changing status. `work.parent` pins review base, `prepared_sha` authoring result.
Worker completion records original branch/commit/parent, clean/capped outcome,
time, receipts/checks, handoff and dependencies; preserve it through rewrites,
separate from current qualification. Promptly import owner/operator receipts.
Transfer counts unchanged at acceptance; use valid mappings or send necessary
work back to same owner. Prepared work advances no tail or release. Follow caller's
queue/scheduling rules for contiguous blocks and real prerequisites versus placement.

Publication needs stable pins/ownership handoff; prefix testing waives no release
gate or unfinished-scope freeze. Scheduling extensions are excluded from scope
digest; accepted lineage/prerequisites/qualification remain included. Exact v2
phases, receipts and operator fields are in operational-records.

## Historical v1 only

Keep historical release_id/schedule/sessions until explicit import reconciles them.
Never create canonical v1 or use legacy evidence as dashboard fallback. Validate
historical records with:

```bash
python <skill-root>/scripts/validate_release_manifest.py <manifest>
python <skill-root>/scripts/validate_review_records.py <manifest> --project-root <original-project>
```

Allow-legacy inspects unreconciled records, never certifies missing counts. V2 uses
validate_operational_records with project-root/operator checks. Validators are
read-only consistency checks, not proof of evidence truth.

Use retained validators as exact v1 field/type/null contract; inspect existing
records rather than generate new v1 templates. Preserve ordered source/parent/target/
tip/tree pins, checks/reviews/trim/correctness, exclusions, CRs, freeze/integration and
historical sessions. Real prerequisites remain separate from placement (independent
means dependency_reason none); generated conflicts create no dependency.

Historical qualification preserves the same branch/ancestry/trim/review/verification
and stage gates as current workflows: exact check/review pins and direct/reuse/mapping
proof, immutable review_handoff transition versus current coverage, no ancestor barrier
for own review handoff, matched qualified chain for ready CR/freeze. Build code-review-loop
owns equal_range_diff/reviewed_restack/test_only_closure proof; plans layout owns
implementation-needing stage regression versus routine restack. Human acceptance
never fabricates clean automation. External checks retain owner/procedure and their
allowed pending state at freeze.

Capped human_disposition has accepted/rejected status, original full decision sha,
decided_by, UTC decided_at, reason/evidence and unresolved_findings, empty only if
none. Evidence disposes each finding/risk; pending decision values stay null.
Carry acceptance only through valid {from_sha,to_sha,method,evidence} chains using
equal_range_diff/reviewed_restack, unchanged effective behavior/finding risk and
current checks/trim. Keep original decision and review_cap_reached. Missing/broken/
behavior-changing proof requires remediation/new decision, never waived branch
checks/final acceptance or fabricated clean automated reviews.

Merged-only user-authorized review cancellation uses waived, not pending/clean:
reviewer SHA=current verified tip, method/origin=null, evidence=waiver; phase status/
evidence likewise (trim SHA too). If this was the only unfinished gate, already
merged release may be released with null freeze, retaining authorized gap/merged CR/
landed SHA/checks and completion {mode:authorized_waiver,authorized_by:user,
recorded_at:<UTC>,evidence:<path>}. It asserts no pre-merge clean review/freeze.

### Receipt accounting

Reconciled review_records_version 1 requires both phases' completed_passes,
historical_completed_passes and passes. Derive disjoint counts from receipts;
sum is displayed/cap total. Terminal phase SHA=current tip; pending null. Preserve
receipt identities; resumes/restacks/closures/retries/normalization add no pass.
Import only after three substantive phase-validated outputs and triage. Preserve
receipt pass_id/period/status/completed_at/reviewed_sha/triage_evidence and three
reviewers (claude/codex/cursor, validated true, matching SHA, evidence). V1 adds no
baseline; use exact shape in validate_review_records.py, with complete UTC evidence.
IDs unique per phase; disqualified receipts retain reason uncounted, incomplete
launches stay execution records. Zero-pass trim needs applicability zero_diff and
evidence; waivers need authority. Coordinator publishes receipts/counts/pins together
and validates safe nonempty files in original plans at every pass/disqualification/
restack. Adopt version only with proof for every accepted branch; unprovable counts
stay unknown, never invented/reset. Historical reconciliation uses explicit importer,
not browser ledger parsing.

### Candidate, freeze and delivery

Integration, not branch checks, owns complete-candidate proof: ordered inputs,
candidate commit/tree, toolchain/clean install/conflict report, checks/staging pipeline,
deployed/rollback releases and acceptance with linked logs. Missing inputs leave
checks pending with prerequisites; partial snapshots do not qualify eventual scope.
Freeze requires qualified branches/ancestors and candidate checks; external gates
retain separate pending policy. Compute v1 scope digest with
validate_release_manifest.py <manifest> --print-scope-digest, set authority/time/
digest and validate. No branch cap; concrete graph/cost evidence can recommend split.
Late critical scope needs authorized thaw/new data/digest/invalidation of affected
integration/pipeline/acceptance; noncritical scope waits unless user changes freeze.

Retain plans-layout delivery gates: confirmed final merge/landed commit before
merged, required acceptance before fulfilled (including legacy done), no intermediate
assembly equivalence. In_release requires fully assembled inclusion proof and
release_candidate release_id/preparation_record/candidate_sha/included_tip_sha.
Rewritten historical sources retain build pins/reviews, with build_tip_sha, matching
source and evidence linking selected preparation entry; separately qualify selected
source. Preserve parent/source pins. Path-only digest repairs retain freeze authority
and migration proof. Active release rejects draft/superseded; merge owner verifies
acceptance. Validators also check selection/unique assignments/tail/linear blocks,
full unique ordered pins, review/check/disposition identity, handoffs/ancestry,
exclusions and digest; producing workflows verify actual evidence/Git objects.
