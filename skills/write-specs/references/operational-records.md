# Operational JSON Records

Canonical report inputs (schema_version 2, exact kind/identity):

| Kind | Path | Owner |
| --- | --- | --- |
| spec | plans/specs/<stage>/<slug>/record.json | Spec/slice/stage coordinator |
| slice | plans/slices/<stage>/<slug>/record.json | Slice/build/stage coordinator |
| build | plans/builds/<id>/manifest.json | Build coordinator |
| release | plans/releases/<lifecycle>/<id>/preparation.json | Release coordinator |
| deployment | plans/deployments/<id>/manifest.json | Deployment runner |

Read `operational-records.schema.json` for required fields/types/enums/nulls. Unknown
fields are forbidden outside extensions; extensions hold supplementary workflow/
immutable history, never report values. Reports ignore extensions/Markdown/archived
release.json or release-folder manifest.json. Required unresolved array records known
unresolved relationships directly. Producers write no other format at canonical paths.

## Writes and validation

Create JSON alongside plan/state, serialize explicit nulls, validate before atomic
replacement, then validate related records in original project:

```bash
python3 <skill-root>/scripts/validate_operational_records.py <record.json>
python3 <skill-root>/scripts/validate_operational_records.py <record.json> --project-root <original-project>
```

Checks cover shape/accounting/pins/declared checks/folder identity/cross-record links.
Scoped evidence must be safe nonempty files inside plans, not directories. Successful
empty stdout uses execution JSON receipt (command/candidate/exit) while preserving
empty log. Project root alone runs whole-project audit; unrelated historical errors
do not block scoped producers. JSON validation proves consistency, never evidence
truth: execute required checks/output validation before success claims.

## Plans and completion

Specs own approval/stage/acceptance map; slices explicitly select current build/source/
tip, never by dates/names. Use schema null rules for standalone/unselected/unprepared.
Each acceptance ID has one current owner matching parent, unchanged by superseded
maps. Keep narrative/JSON/pins/qualification synchronized through approval/selection/
moves/rewrites; move records, repair paths and retain IDs/original receipts.

Optional fulfilled-slice completion uses schema's accepted kinds/person/UTC decision
and safe nonempty JSON evidence repeating decision with exactly one matching
accepted_slices provenance. Code binds exact merged member of merged/released/
accepted canonical release and matching current/build qualification. Non-code has
null source/tip/parent/release/current. Reopening archives/removes active completion
before stage/source changes; completion changes no review count/outcome or build gate.
Keep bulky history in hashed provenance-linked audits, current fields directly readable
within report's 16 MiB record limit.

Report rules: superseded→Superseded even without current, preserving history/errors;
unselected draft/backlog/to_do→Not Started; hold/merged/fulfilled alone preserve
implementation/review state. Accepted completion→Complete for all kinds, retaining
selected-build counts; missing code history→Not recorded, non-code→N/A. Unknown counts
remain Unclear. Hold records pause/notes/source/history, no completion/waiver.

## Build phases

Branches are accepted placements, schedule.work authoring/planned work. Each carries
explicit slice/spec/source/parent/pins/phases. Implementation not_started/running/
verified/unknown: verified pins tip with nonempty required_check_ids, every listed
agent check passed there (prepared_sha for work). A commit/arbitrary check is insufficient.

Trim ends proportionate. Correctness distinguishes not_started/running/
provisionally_complete/clean/review_cap_reached per schema; terminal results require
current tip/evidence. Clean needs proportionate trim and three clean current-tip
reviewer results. Scheduled clean must match qualified accepted branch.

Prepared provisional completion needs verified implementation, pinned parent,
proportionate trim, three clean current-tip reviews with evidence/direct-or-valid-mapping/
original SHA, correctness provisionally_complete on prepared_sha with ledger evidence.
Work stays prepared (or blocked awaiting acceptance); report Provisionally Complete.
Incomplete correctness uses running/null SHA/ledger. Rewrite clears to running unless
mapping proves new tip; cap records review_cap_reached on verified prepared tip.
Acceptance transfers receipts/counts unchanged, converts provisional to clean only
with valid qualification, otherwise running/null. Accepted branches forbid provisional
status; counts alone establish none. Reconcile older running evidence before completion.

Session metadata: extensions.sessions, schedule.extensions.coordinator and work
extensions.owner (IDs/names/checkout/authoring base/execution lease/pause-resume).
Import handoffs promptly. Work worker_completion preserves original authoring pin,
clean/capped outcome, checks/review receipts/dependencies/handoff, never qualifies
rewrite. Report worker complete separately from acceptance/current coverage; release
readiness is separate. Preserve workflow gates/history in extensions without aliases.

Freeze stays null until authorized/qualified: verified implementation, proportionate
trim, matched parent heads, clean correctness or current-tip accepted capped
human_disposition (schema decision/mappings; display remains exhausted). Record authority,
UTC time and v2 digest from validate_operational_records.py <manifest> --print-scope-digest.
Migration retains original freeze proof/authority/Git identities with new digest, not v1 hash.

Waived/unknown require reason; current waiver→Review waived, unknown→Review status
unknown with phase/reason. Neither clean nor release-qualified; waiver adds no passes.
Missing/invalid/conflicting qualification→Unclear with problem. Correctness status
precedes trim unless not_started; unknown counts independently stay Unclear. Reports
are read-only, checking waiver file safety/size/existence, never narrative proof.

## Receipts and history

Accounting receipts requires integer completed_passes/historical_completed_passes
equal to baseline plus completed receipts in disjoint periods. New baseline=null.
Completed receipt: stable unique ID, UTC completion, original reviewed SHA, triage
path, three distinct validated reviewers on same SHA. Keep old identities; mappings
prove current applicability. Disqualified receipts retain reason uncounted. Incomplete
launches/closures/repairs/mappings add none. Zero-pass trim requires zero_diff applicability
and evidence.

Historical valid JSON counts may enter immutable audited baselines. Separately
authorized missing-count reconciliation audits each pass's triage/outputs/qualification,
recording included/disqualified attempts, original pins/paths/input hashes. Baseline
and receipts cannot overlap. Directory/prose totals are insufficient; never invent
receipts. Unprovable history uses accounting unknown, null counts, empty passes/null
baseline/reason, never zero; independently proven clean result may coexist. New completed
passes always require receipts. Reports derive nothing from narrative/audit contents.

## Operator handoff

New/adopted branches/work require schema-defined operator_handoff; optional only for
untouched old records. Add --require-operator-handoff with project-root. Use explicit
nulls, unique classification/package/evidence arrays and exact schema enums, primary
type first. Ready requires current pin/four descriptions/types/surfaces/evidence;
packages may be empty, unknown needs reason. Identify touched Composer metadata/
registered first-party Magento modules only, excluding inherited/untouched packages.

Draft before implementation. Owner returns data/proof; coordinator writes. Verified
producer entries need ready text reconciled to branch-only outcome, operator staging
steps/prerequisites/pass observations and separate developer/third-party checks.
Follow plan-implement operator wording rules after fixes/restacks; refresh SHA only
after applicability proof. Suggested tests claim no execution/acceptance; archive
superseded text immutably. Reports/exports use selected build/source object only,
never Markdown/extensions/Sheets/another build. Missing old text is not recorded;
draft/unknown/pin conflicts stay explicit. Pass condition describes proof; types purpose.

## Releases and deployments

Release fields pin memberships/source/original parent/PR/candidate/staging/acceptance;
PR destination differs from stack parent, lifecycle from assembly. Session extensions
record acceptance owners/scope/environment/pins/evidence for coordinator aggregation;
preserve publication authority/merge journals and existing mutation gates.

Deployment schema pins identity/environment/candidate/outcome/evidence/membership.
Verified needs deployed/pipeline/smoke proof; acceptance remains on release. Producer
records exact members from validated release/Git ancestry, including integration
members; report infers no membership/environment/outcome or ancestry. Extensions
retain base/inputs/backup/old staging pointer/pipeline/recovery/failures.

## Conditional historical import

Only migrate_operational_records.py reads old formats/Markdown/Git; dashboard never
runs/imports it. Preview without writes:

```bash
python3 <skill-root>/scripts/migrate_operational_records.py <original-project>
```

--apply saves byte-identical originals/hashes under plans/audits, checks concurrent
changes and atomically replaces, preserving detail in extensions. Resolve warnings;
invent no receipts/parents/membership. Imported record becomes authoritative, originals
immutable; coordinators adopt before next write. V1 tools apply only to historical
records, never dashboard fallback/v2 substitutes.

Preview --reconcile-json-counts for earlier imports' explicit counters→audited baseline
without pin/review changes. Preview --reconcile-plan-metadata for original-plan/archive
approval/map/spec IDs without selection/pin/review changes, retaining original/replacement
hashes. These are one-time importer modes, not dashboard/normal writers.
