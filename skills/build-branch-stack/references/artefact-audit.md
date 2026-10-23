# Artefact Audit at Branch Handoff

After selected slices pass branch gates and review artifacts/manifest pin their tip,
read plan/reviews/execution/evidence/ledger/latest triage/worker notes for related
issues/follow-ups/deferrals/rejections. Advisory notes are candidates, not findings;
deduplicate by problem. Use targeted read-only checks at tested chain/integration
snapshot or exact feature tip, recording actual SHA. Defer intrinsically cross-branch
questions until tested candidate exists; never call unmerged code merged. Re-audit
repair-affected code/evidence, without repeating resolved decisions. External acceptance
is separate. Search specs/maps/slices across all stages/legacy paths in snapshot and
primary checkout for coverage before planning concrete substantial still-needed work.
Rejected notes alone justify no plan; insufficient evidence stays unknown.

Current acceptance failure/missing requirement/confirmed defect is current-plan fix:
return owner in_progress, reconcile parent, fix/check/restack descendants in current
stages and re-audit. Cap disposition alone does not demote review. Pending external/
candidate checks alone are no fix; send invalidated candidate proof to release owner,
never backlog it.

Maintain primary `<feature_dir>/<slug>.reviews/artefact-audit-ledger.md` with verified
tip/audit snapshot/date/sources and one distinct candidate row:

```text
| Candidate | Source artefact | Current-code evidence | Decision | Reason | Planning reference |
```

Use planned/not planned/current-plan fix/pending; explain resolved/duplicate/covered/
advisory/vague/minor decisions, existing spec/slice slugs or none. No candidates still
records sources. Reruns reconcile, no duplicates; feature-relative artifact links/plan slugs.

Planned outcomes use write-specs saved draft/approval, then write-slices saved map/
children/decomposition approval. One cohesive slice still needs map; separable outcomes
need distinct drafts. Trace source candidate/feature/tip/snapshot, translate suggested
mechanism to outcome unless binding. Approved children stop backlog, unapproved draft.
Audit grants no approval/implementation/push/CR. Keep files out of verified tips/temporary
worktrees; preserve unrelated work. Unsafe writes/collisions stay pending. Reconcile
obsolete generated plans only if untouched draft/backlog, else report scope decision.
Audit failure leaves branch readiness intact but incomplete until every selected ledger/
warranted plan exists.
