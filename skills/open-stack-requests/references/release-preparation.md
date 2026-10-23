# Release Preparation Record

Use `operational-records.md` and its strict schema-v2 release contract for new
or adopted `preparation.json` files. Validate with
`scripts/validate_operational_records.py`; narrative historical field lists
below are context, not alternate JSON formats.

## Upfront Choices

Resolve the user's strategy (`merge-commit` or `squash`) and approval preference
(`pause` or `proceed`) before release work. Ask for missing answers together and
wait; neither has a default. Reuse explicit answers for this release on resume.
Store `strategy`, `approval`, and direct user `evidence` in
`extensions.merge_options`. A legacy default does not establish a user choice.
`pause` requires one confirmation after PR publication; `proceed` authorizes
assembly of the selected scope without that pause. Both cover verified squash
restacks under the authorization below. Staging and the final base merge retain
their own authorization boundaries.

Use `plans/releases/active/<release-id>/preparation.json` for PR assembly state. This
operational record does not replace a build manifest or change its dependency
pins or review evidence. Confirmed assembly advances selected plans to
`in_release` under the shared layout; path-only repairs may update the freeze
digest with a recorded migration, preserving freeze authority and Git identities.
When a build manifest exists, link this record under `integration.release_preparation` and retain its
original targets; release PR destinations belong here. If its coordinator is
active, return the link and publication results for coordinator import rather
than writing the live build manifest yourself.

## Concurrent Build Snapshot

Select a qualified, ancestry-closed prefix of an ongoing linear build. Pin its
build ID/path, source/parent SHAs, and verification/review links here; do not copy
or freeze the unfinished manifest. Planned names and prepared candidates are
not release inputs. Selected branches and inherited unmerged work must meet
branch verification, review and repository gates. Candidate-wide checks belong
to release assembly and staging verification; build completion does not imply
they ran. Later unselected work does not block a complete prefix.

Import selected branches' deferred release integration and activation checklist
under the operational-records phase contract, including agent-run checks. Preserve
acceptance IDs, phase, executor, owner, procedure, prerequisites, status/evidence
and blocking milestone. Staging rebuild owns assembled pre-deployment checks,
pipeline/deployment health and smoke checks; acceptance owners test deployed
runtime and external/activation requirements. The release coordinator reconciles
every obligation against fresh/reused evidence or an explicit pending owner and
procedure. A pending later check blocks its assigned release/activation milestone,
not branch review completion. Reuse applicable completed proof; source repairs
return to the build owner with focused regressions, without resetting prior reviews
or rerunning unrelated checks solely because release testing found a defect.

Before ready publication or release mutation, obtain a coordinator handoff
pinning source heads, permitted verified squash restacks and a return condition.
Other source rewrites wait; other work continues. The release agent owns this
record and its isolated integration
branch, not build sources or review evidence. Return candidate membership and
stage results to the active coordinator for shared moves and manifest repair.
Return source repairs to the coordinator. Source drift invalidates affected snapshots/approvals under existing
rules. Preserve release/deployment authorization boundaries. After a final base
merge, return landed identities for coordinator reconciliation of plans and
remaining descendants.

Record `lifecycle: "active"` separately from assembly state. After confirmed
final merge and required acceptance, record `released` and move the whole folder
to `plans/releases/released/<release-id>/`. For an established replacement or
explicit cancellation, record `superseded` or `cancelled`, the reason and evidence,
and replacement links when applicable, then move to the matching stage folder.
Repair maintained build, release, deployment, and handoff paths after each move;
preserve dated evidence and retain the path map. Resume a supplied legacy record
in place until an authorized move, never create a duplicate. A historical mixed
release/deployment folder may move intact; add a linked summary only when no
whole-release record exists.

Record:

- `kind: "release"`, `schema_version: 2`, release ID, repository,
  remote, and provider;
- base branch and full SHA; integration branch and starting SHA;
- ordered changes: source, full head SHA, original parent branch and SHA,
  title, description-file path, verification references, and PR ID, URL,
  author UUID, current destination, state, and landed SHA;
- an append-only merge journal path outside the repository;
- candidate commit and tree SHA, staging receipt and acceptance evidence;
- acceptance owners, assigned requirements, candidate/environment pins and
  evidence links in `extensions.sessions`;
- publication owners, assigned PRs/pins, persistent IDs/names, status and private
  intent/result evidence paths in `extensions.sessions`;
- final PR identity and current state.

Pin all inputs before publication. Preserve original source/parent pins and
record verified squash mappings separately in `extensions.restacks`, including
old/new heads, parent, target and proof. Other source changes invalidate recorded
verification and merge authorization; stop for disposition without launching
reviewers or editing code. A target change requires refreshing its diff and
configured checks, not automatically rebasing the source.

Initially, each independent root targets integration; each stacked change
targets its nearest selected unmerged predecessor. Use the input dependency
map and Git ancestry together. Reject unlisted inherited work, cycles, and a
parent that is not an ancestor. Do not turn independent roots into a chain.
Represent Git ordering, including explicit linear placement, separately from
functional dependency. For mixed stacks, preserve user order when predecessors
come first; otherwise report the conflict.

Fresh runs create new non-draft PRs. Before each creation, record its source,
destination, both SHAs, author, and intended metadata. Immediately record the
returned ID and URL. After interruption, reconcile only a PR from this run:
require the same author, branches, full source SHA, and intended metadata.
An unrecorded but matching creation may be recovered only from its recorded
intent and a unique provider match. Stop for unrelated or duplicate PRs.
Never retry a mutation with an unknown outcome before reconciliation.
For concurrent publication, the coordinator alone writes this record. Each
persistent ` - Publishing` owner prepares one PR's metadata, waits for its recorded
intent, then creates and saves the result in its private path for prompt import.
Existing destination branches allow stacked PRs to open concurrently; assembly
retains the recorded merge order. Reuse owner IDs and intents during recovery.

## Merge Authorization

Create all individual PRs and present their links, descriptions, pinned heads,
order and proposed squash messages before merging. With `approval: pause`, obtain
one confirmation covering assembly and verified squash restacks. With `proceed`,
use the user's upfront instruction. Bind that permission to the resolved scope
before mutation; creation or invocation alone gives no merge permission. Satisfy
configured forge checks and approvals without adding a separate review gate.

Record that confirmation with `merge-stack/scripts/journal_event.sh`:

```json
{
  "event": "merge-authorized",
  "authorized_by": "user",
  "merge_method": "squash",
  "integration_start_sha": "<full initial integration SHA>",
  "allow_verified_restacks": true,
  "evidence": "<direct user instruction or confirmation>",
  "changes": [
    {
      "change_id": "<PR ID>",
      "source_branch": "<branch>",
      "head_sha": "<full source SHA>",
      "parent_sha": "<full original parent SHA>",
      "target_branch": "<integration branch>",
      "message_sha256": "<canonical squash message hash>"
    }
  ]
}
```

List all changes in merge order. Use `merge_method: "merge-commit"` and
`allow_verified_restacks: false` for merge commits; omit their message hashes
unless supplying custom messages. The destination is integration even while a
stacked PR temporarily targets its predecessor. Record message files and hashes
in preparation extensions; reuse their exact text on resume.

Authorization survives resumption and verified squash restacks in the same
release. A restack must start at the authorized source/parent, target the last
confirmed release result, preserve its own patch sequence and reproduced tree,
and retain the same message. Journal the proof and lease push; refresh checks
for the new head. `release_authorization.py` checks that mapping before merging.
No per-successor user confirmation is needed. Conflicts, changed feature scope,
unexpected ref movement, changed messages or failed proof require a new decision;
the permission excludes another release and the final integration-to-base merge.
Legacy authorization covers only its exact heads; omitted merge methods mean
`merge-commit`, and missing restack permission grants none.

## Completion

After the complete selected scope is assembled, pin its candidate commit/tree
and verify every included source tip or squash mapping. Move qualifying slices
from `review/` to `in_release/`, record `release_candidate` on each existing
build branch (or link preparation change entries when no build exists),
and reconcile parents from their complete approved maps. Repair maintained
plan/artefact paths and any path-dependent freeze digest under the shared move
rules. For an active build, return these results to its coordinator instead of
writing shared plans or manifests. Starting preparation or partial assembly
preserves stages; do not move already merged or fulfilled slices backwards.

Merging into integration means assembled, not released. Do not move plans to
slice or spec `merged/` or `fulfilled/` folders, delete sources, or
mark the build manifest released. Freeze the assembled candidate's commit and
tree, verify its combination and deploy that exact commit through
`rebuild-staging-with-branches`. Delegate acceptance of the deployed candidate
to persistent ` - Acceptance` chats running `verify-staging-acceptance` under
`prepare-release-integration`. Aggregate every requirement separately from
deployment success; an individual owner's pass does not accept the release.

The final PR contains the scope, individual PR links and merge order,
integration resolutions, candidate identity, test and staging evidence,
limitations, and rollback. Create it only after acceptance and current-base
checks pass. Leave it open for the final reviewer; preparation never merges
the final PR or deploys production.

After an independently authorized final integration-to-base merge, confirm
landed commits. Move slices to `merged/` while required acceptance remains
outstanding, or directly to `fulfilled/` when satisfied; advance `merged/` slices
once acceptance passes or its limitations are explicitly accepted. Reconcile
parents under the shared layout. Assembly advances only `in_release`, never
`merged` or `fulfilled`. Staging and final PR publication retain `in_release`.
On cancellation, replacement, or candidate invalidation, reconcile membership
and return uncovered unmerged plans to `review` (or `in_progress` for fixes).
