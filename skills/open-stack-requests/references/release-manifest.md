# Release Manifest

Use one canonical JSON manifest for release state. Store it at
`plans/releases/<release-id>/manifest.json` unless the repository defines
another stable path. Evidence files may remain elsewhere, but the manifest is
the source of truth for branch order, dependencies, targets, SHAs, checks,
acceptance, exclusions, change requests, candidate state, and deployment.
Spreadsheets and prose summaries are projections: generate or reconcile them
from the manifest, never use them to override it silently.

## Shape

```json
{
  "schema_version": 1,
  "release_id": "release-name",
  "state": "building",
  "base": {"branch": "master", "sha": "<full-sha>"},
  "freeze": {
    "frozen_at": null,
    "authorized_by": null,
    "scope_digest": null
  },
  "branches": [
    {
      "source": "feature/example",
      "plan": "plans/in_progress/example/example.md",
      "target": "master",
      "parent": {"branch": "master", "sha": "<full-sha>"},
      "dependency_reason": "none",
      "tip_sha": "<full-sha>",
      "tree_sha": "<full-tree-sha>",
      "surfaces": ["storefront"],
      "review_progress": {
        "status": "pending",
        "completed_passes": 0,
        "pass_limit": 5,
        "evidence": null
      },
      "human_disposition": {
        "status": "pending",
        "sha": null,
        "decided_by": null,
        "decided_at": null,
        "reason": null,
        "evidence": null,
        "unresolved_findings": [],
        "mappings": []
      },
      "trim_review": {
        "status": "pending",
        "sha": null,
        "evidence": null
      },
      "review_handoff": null,
      "checks": [
        {
          "id": "focused-tests",
          "kind": "agent",
          "status": "passed",
          "sha": "<full-sha>",
          "method": "direct",
          "origin_sha": "<full-sha>",
          "command": "<exact command>",
          "evidence": "<path>"
        }
      ],
      "reviews": [
        {
          "reviewer": "claude",
          "status": "clean",
          "sha": "<full-sha>",
          "method": "direct",
          "origin_sha": "<full-sha>",
          "evidence": "<path>"
        },
        {
          "reviewer": "codex",
          "status": "clean",
          "sha": "<full-sha>",
          "method": "direct",
          "origin_sha": "<full-sha>",
          "evidence": "<path>"
        },
        {
          "reviewer": "cursor",
          "status": "clean",
          "sha": "<full-sha>",
          "method": "direct",
          "origin_sha": "<full-sha>",
          "evidence": "<path>"
        }
      ],
      "change_request": {
        "url": null,
        "state": "none"
      }
    }
  ],
  "exclusions": [
    {"source": "feature/excluded", "reason": "explicitly excluded"}
  ],
  "accepted_gaps": [],
  "integration": null
}
```

Use `building`, `frozen`, `staged`, `accepted`, or `released` for release
state. Use `agent` for checks Codex can run and `external` for human, live, or
third-party acceptance. External checks may remain pending when the candidate
freezes if their procedure and owner are recorded.

For a completed agent check, `sha` is the tip the result verifies and
`origin_sha` is where the command ran. Use `method: "direct"` when they match.
Use `method: "identity_reuse"` when capability-defined evidence maps a prior
passed result to the current tip; then `evidence` must link the originating
result and current-tip identity proof. Leave `method` and `origin_sha` null for
pending agent checks and all external checks.

List branches in integration order. `target` is the change-request target;
`parent` is the demonstrated code prerequisite. They normally match. Use
`dependency_reason: "none"` for an independent branch. A generated-file
conflict alone is not dependency evidence.

Record one review entry for each of `claude`, `codex`, and `cursor`. For a
direct review, set `method` to `direct` and use the reviewed tip for both `sha`
and `origin_sha`. After a proven mechanical restack, set `method` to
`equal_range_diff`, set `sha` to the verified new tip, `origin_sha` to the
directly reviewed old tip, and link the mapping evidence. For either focused
unequal-restack path in the build skill's `code-review-loop.md`, use
`reviewed_restack`, set `origin_sha` to each directly reviewed SHA, and link
intermediate mappings, per-commit comparison, current-tip checks, and the
path's required reviewer confirmations. After an eligible test-only
remediation, set `method` to `test_only_closure` for all three prior
reviews, map each `origin_sha` to the verified new `sha`, and link evidence for
the test-only delta, unchanged production and effective-result identities,
exact-tip verification, and same-session closure by each originating reviewer.
A branch with automation-clean reviews requires all three entries. A capped
branch retains its actual reviewer results and cap marker even when a human
accepts it; human acceptance never changes a reviewer entry to `clean`.

Use optional branch-level `review_progress` to preserve orchestration state
across resumed runs. Its status is `pending`, `clean`, or
`review_cap_reached`; `completed_passes` counts only completed fresh discovery
passes and `pass_limit` is the configured cap. Set `evidence` to the triage
ledger path when the cap is reached. A capped branch remains in the manifest
and may have a verified, pushed tip, but it is not automation-clean. After the
cap, stop fresh discovery passes. A human may make a separate disposition on
the exact verified tip. Record `human_disposition` with `status: "accepted"` or
`"rejected"`, its full `sha`, decision maker, UTC `decided_at`, reason, evidence
path, and `unresolved_findings` as an array of finding IDs or concise finding
descriptions. Use an empty array only when none remain. The decision evidence
must explain the disposition of each unresolved finding and the accepted risk.
For `pending`, keep decision fields null and record known unresolved findings.
The decision's `sha` always stays pinned to the SHA the human assessed. A
direct acceptance applies when it equals `tip_sha`. After a restack, carry it
forward without another human decision only when a chain of `mappings` leads
from that SHA to the new verified `tip_sha`. Each mapping records `from_sha`,
`to_sha`, `method` (`equal_range_diff` or `reviewed_restack`), and an evidence
path. Require the corresponding review-loop mapping proof, unchanged effective
behavior and applicability of every accepted unresolved finding, proportionate
trim, and exact-tip branch verification. The validator checks the SHA chain and
evidence fields; the build skill verifies the proof. An incomplete mapping
leaves the original decision on record but inapplicable to the new tip. A
broken or behavior-changing mapping requires remediation or a new human
decision. Keep `review_progress.status` as
`review_cap_reached`; acceptance does not waive trim,
branch checks, exact-tip verification, or later merge and acceptance gates.
It is a review handoff decision, separate from final human or external
acceptance before `done/`.

Move a slice to `review/` after its own implementation is committed, pushed,
and verified; trim is proportionate; and correctness reviews are clean or the
five-pass cap is exhausted after accepted fixes and closure. Do not wait for
ancestor review decisions, human disposition on this slice, or descendants.
Record the durable transition as `review_handoff: {"sha": "<full-sha>",
"outcome": "clean|review_cap_reached", "evidence": "<path>"}`. Its evidence
links the terminal trim and correctness ledgers and exact-tip verification.
Keep `review_handoff` pinned to that transition SHA through later restacks.
The current `trim_review`, `review_progress`, reviews, and checks separately
describe readiness on the latest `tip_sha`. A changed ancestor requires a
restack and exact-tip re-verification; retain reviews, trim, and an accepted
human disposition only through valid mappings. Pending or stale current-tip
evidence blocks ready change requests and release progression without moving
an otherwise complete slice out of `review/`.

For ready change requests and release states, each branch and required
ancestor must have proportionate trim, passed agent checks, and automation-clean
reviews or an accepted capped disposition on its current pinned SHA. Each
parent head must equal its child's pin. These lineage gates do not control
`review/` stage moves. A verified ancestor may support a provisional dependent
wave while its reviews or human disposition remain pending. A failed check or
change needing implementation returns the affected slice to `in_progress/`;
archive its old `review_handoff` as evidence and clear the active field until
reviews finish again.

For a new build, record `trim_review` separately from correctness reviews.
Set `status` to `pending` or `proportionate`, `sha` to the current verified tip
when proportionate, and `evidence` to the trim ledger with reviewer outputs and
any restack mapping. Add this field to older manifests before further branch
review. A trim result does not increment `completed_passes` or fill `reviews`.
Do not mark a branch ready when its trim result is pending or applies to an
unmapped old tip.

Use `waived` when the user explicitly cancels a review phase for an already
merged change. It means the review was not performed; never label it `clean`
or leave it `pending`. Set each waived reviewer entry's `sha` to the verified
tip, `method` and `origin_sha` to null, and `evidence` to the waiver record.
Set `review_progress.status` to `waived` with the same evidence. For a waived
trim phase, set `trim_review.status` to `waived`, its `sha` to the tip, and its
`evidence` to the waiver record.

An already merged release may use `state: "released"` with a null `freeze`
when its only unfinished gate was explicitly waived. Keep the authorized gap,
merged change request, exact-tip checks, and landed SHA. Add
`completion: {"mode": "authorized_waiver", "authorized_by": "user",
"recorded_at": "<UTC time>", "evidence": "<waiver path>"}`. This records
administrative completion after the merge; it does not claim a pre-merge
freeze or a clean review. Ready, frozen, staged, and accepted candidates require
automation-clean reviews or an accepted capped disposition on each exact tip.

Keep integration results under `integration`, including ordered input SHAs,
candidate commit and tree SHAs, toolchain identity, clean-install evidence,
conflict-resolution report, checks, staging pipeline and deployed release,
rollback release, and acceptance result. Link evidence; do not copy large logs
into the manifest. Keep checks that intrinsically require a complete release
candidate under `integration`, not a branch's `checks`. Before every planned
branch exists, record integration as pending with the missing branch or other
prerequisite for each deferred check; do not attach a partial-stack result as
evidence for the eventual candidate.

## Freeze

Freeze only after every branch and its pinned ancestors meet the per-slice
handoff gate, including exact-tip checks and automation-clean reviews or an
accepted capped disposition. Complete release-candidate checks still apply.
Compute `freeze.scope_digest` with:

```bash
python <skill-root>/scripts/validate_release_manifest.py \
  <manifest> --print-scope-digest
```

Set `frozen_at`, `authorized_by`, and the printed digest, then validate the
manifest. A frozen candidate has no default branch-count limit. Scope follows
release need, not size. When the graph or acceptance cost is high, recommend a
smaller split with concrete reasons, but do not impose it.

Do not add late scope silently. An authorized critical addition requires a
recorded thaw decision, new branch/check data, a new freeze digest, and
invalidation of integration, pipeline, and acceptance results affected by the
change. Send noncritical additions to a later release unless the user
explicitly changes the frozen scope.

## Validation

Run:

```bash
python <skill-root>/scripts/validate_release_manifest.py <manifest>
```

The validator checks required fields, full SHAs, unique ordered branches,
parent order, branch review and check identity, SHA-pinned human dispositions,
durable `review/` handoff records, ready CR ancestry, merged CRs for `done/`,
exclusions, and freeze digest. Final acceptance before `done/` remains an
evidence gate owned by the merge workflow.
Validation proves manifest consistency, not that referenced evidence is true;
the owning skill must verify those files and Git objects.
