# Operational JSON records

The operator report reads only the following canonical schema-v2 files:

| Kind | File | Owner |
| --- | --- | --- |
| `spec` | `plans/specs/<stage>/<slug>/record.json` | `write-specs`, `write-slices`, stage coordinator |
| `slice` | `plans/slices/<stage>/<slug>/record.json` | `write-slices`, build/stage coordinator |
| `build` | `plans/builds/<build-id>/manifest.json` | build coordinator |
| `release` | `plans/releases/<lifecycle>/<release-id>/preparation.json` | release coordinator |
| `deployment` | `plans/deployments/<deployment-id>/manifest.json` | deployment runner |

Read `operational-records.schema.json` for exact fields, types, enums and null
rules. Every record requires `schema_version: 2`, its exact `kind`, and its
identity. Unknown fields are rejected except inside the explicit `extensions`
object, which stores supplementary workflow evidence and immutable historical
records. The report never interprets extensions. Do not put report state there. Record
known unresolved relationships in the required `unresolved` array; the report
surfaces them directly.
Markdown remains narrative and linked evidence; it supplies no report values.
Historical `release.json` and release-folder `manifest.json` are archives, not
alternate inputs. Producers must not publish another format under canonical paths.

## Creation and validation

Create JSON with the plan or operational record, not at the end of the run.
Use JSON serialization, explicit nulls and atomic replacement. Validate the
proposed record before replacement, then validate its related records in the original project:

```bash
python3 <skill-root>/scripts/validate_operational_records.py <record.json>
python3 <skill-root>/scripts/validate_operational_records.py <record.json> --project-root <original-project>
```

The shared validator checks strict structure, phase accounting, current-tip
results, declared implementation checks, path/folder identity and cross-record
references. Scoped producer validation also checks evidence paths exist and
are nonempty inside `plans/`, without reading Markdown contents. It returns nonzero and field-specific errors. It reads JSON only.
Run the same script with `<original-project>` alone for a whole-project audit.
Unrelated historical errors do not block a scoped producer check.
A valid shape does not prove the truth of evidence; the producing skill must
run its existing checks and review-output validators before recording success.

## Plans and relationships

Spec records hold approval, stage and the machine-readable acceptance ownership
map. Slice records hold approval, stage, `spec_slug` (null for standalone work),
and `current`: null before selection, otherwise the exact build ID, source and
current full tip SHA (null before a candidate exists). `current` selects one
build/source explicitly. Never select one by timestamps or folder names.

Update JSON and narrative together on approval, selection and stage changes.
Move `record.json` with its plan folder; repair `plan` and maintained references.
Keep IDs stable. Validate each acceptance ID has one owner and the slice's
parent matches its spec. Superseded maps remain historical and do not reassign
current ownership. On a source rewrite, update the slice current pin and the
build's qualification together; preserve the prior receipt identities.

## Builds and review phases

Accepted `branches` and `schedule.work` have explicit slice/spec IDs, source,
parent/pins and implementation/review state. Work entries do not imply accepted
branches. Scheduled implementation verification also requires every declared check on
`prepared_sha`. Scheduled clean correctness refers to its matching qualified
accepted branch; queue state alone cannot establish clean review. Keep scheduled work's phases current while workers run; import their
validated receipts through the coordinator. Store supplementary selection,
coordinator, session, disposition and integration evidence in the
record's documented extensions; preserve the existing workflow's gate checks.

Keep `freeze` null until its existing qualification and authorization gates
pass. Frozen and later candidates require verified implementation, proportionate
trim, matching parent heads, and clean correctness or an accepted capped
`human_disposition` on the current SHA. That optional object has a defined
decision and mapping schema; it never changes the displayed exhausted status. Record the authority, UTC time and canonical scope digest; use
`validate_operational_records.py <manifest> --print-scope-digest`. Historical
imports retain the original freeze evidence and record the schema migration's
new digest without changing authority or Git identities. Do not use the v1
scope hash for canonical records.

Implementation states are `not_started`, `running`, `verified`, or `unknown`.
A verified result pins the tip and declares a nonempty `required_check_ids` list;
every listed agent check must have passed at that tip. Do not infer completion
from one arbitrary passed check or a commit existing.

Phase states distinguish `not_started` from `running`; trim ends at
`proportionate`, correctness at `clean` or `review_cap_reached`. `waived` and
`unknown` require reasons and never display as clean completion. Terminal
results require the current tip and an evidence path. Clean correctness also
requires three clean current-tip reviewer results and proportionate trim.

`accounting: "receipts"` requires integer `completed_passes` and
`historical_completed_passes`, equal to the immutable imported baseline plus completed receipts in each
disjoint period. The baseline is null for new phases. Historical import may
carry explicit valid JSON counts into a baseline with an immutable audit JSON
evidence path; it never synthesizes reviewer receipts or parses prose counts.
The baseline and new receipts must cover disjoint passes. Each completed receipt contains a stable ID, UTC completion time,
reviewed SHA, triage path and three distinct validated reviewer outputs on that
SHA. Disqualified receipts retain a reason and do not count. Incomplete launches,
repairs, closures and mechanical mappings do not add receipts. Historical
receipt SHAs stay immutable; current reviewer mappings establish applicability.
Use `applicability: "zero_diff"` for a documented zero-pass trim exemption.

If historical receipts cannot be established, use `accounting: "unknown"`,
null counts, an empty receipt array, a null baseline and an explicit reason. This means unknown,
not zero. A separately established current clean result may still be recorded;
it does not manufacture historical receipts. Never use unknown accounting for
new completed passes. Preserve historical counts in immutable import evidence.

## Releases and deployments

Release `changes` contain explicit slice/build identities, source heads,
original parents and PRs. Current PR destinations live in the PR record, separate
from stack parents. Store the candidate commit/tree, final PR, lifecycle,
assembly state, acceptance and staging receipt in their defined fields.
Lifecycle is `active`, `released`, `superseded` or `cancelled`; it is distinct
from assembly state. Preserve publication authorization and merge journals in
extensions; existing mutation gates still apply.

Deployment receipts use `deployment_id`, explicit environment, optional
originating release ID, candidate commit/tree, `outcome`, evidence and
`included_slices`. Outcomes are `pending`, `verified`, `failed`, or `unknown`.
Only record `verified` after checking the deployed candidate and existing
pipeline/smoke requirements. Acceptance remains separate on the release.

The deployment producer records exact included slice/source/tip memberships,
using validated release membership or Git ancestry when preparing its receipt.
The report performs neither ancestry queries nor environment/outcome inference.
When deploying a release integration branch, carry its included slices into the
receipt; recording just the integration input loses operator membership.
Keep base, selected integration inputs, backup, old staging pointer, pipeline,
recovery commands and failure details in extensions as deployment evidence.

## Historical import

Only `migrate_operational_records.py` may inspect historical formats, Markdown
metadata or local Git to propose canonical records. It is never imported or
run by the dashboard. Preview first:

```bash
python3 <skill-root>/scripts/migrate_operational_records.py <original-project>
```

`--apply` saves byte-for-byte originals and hashes under `plans/audits/`, checks
for concurrent input changes, then atomically replaces records. Preserve all
historical detail in extensions. Resolve explicit import warnings; do not
invent missing receipts, parents or release membership. The imported record
becomes authoritative; dated originals remain immutable evidence. Active
coordinators must adopt the contract before their next write. Existing v1
qualification tools apply only to their historical records, never as dashboard
fallbacks or as substitutes for v2 validation.

For adopted v2 records, `--reconcile-json-counts` imports any remaining explicit
historical JSON counters into audit-backed baselines. It never changes source
pins or reviewer results. Preview without `--apply` first.

For records adopted by an earlier import, `--reconcile-plan-metadata` explicitly
restores missing approvals, ownership maps and spec IDs from the original plans
and archived JSON. It leaves current selection, pins and review results intact;
original JSON and replacement hashes are saved in the migration audit. This
option belongs to the one-time importer, never the dashboard or normal writers.
