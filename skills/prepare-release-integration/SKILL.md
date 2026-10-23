---
name: prepare-release-integration
description: Prepare a Bitbucket release with upfront merge choices, publish individual PRs concurrently through persistent owners, assemble and test the exact candidate on staging, and open the final PR to the base branch.
disable-model-invocation: true
metadata:
  layer: runner
---


Read `references/operational-records.md` before creating or updating plan metadata,
builds, releases or deployments. Its schema-v2 JSON contract is authoritative
for operational records. Write and validate canonical JSON alongside each state
change; do not leave the browser report to reconstruct state from Markdown.
Use `scripts/validate_operational_records.py <record> --project-root <original-project>`
for each owned record before handoff. Whole-project audit findings are separate.
Keep historical extensions and existing authorization, verification and review
gates; they do not authorize schema aliases or inferred reporting values.
# Prepare Release Integration

Own release integration verification after individual branches complete their
implementation checks/reviews. Import deferred checks from selected specs, slice
maps/plans and build records; preserve acceptance IDs, status/evidence, owner,
executor, procedure, prerequisites and blocking milestone. Branch completion is
not assembled-runtime acceptance. Agent-run testing belongs here when it proves
cross-feature, deployed-asset or full storefront/Admin/cache/provider behavior.
Use the phase and evidence-reuse rules in `references/operational-records.md`.

## Upfront Choices

Before release work, resolve both choices from the user's instructions:

- **Strategy:** merge commit (`merge-commit`) or squash (`squash`).
- **Approval:** pause after publishing PRs (`pause`) or proceed to assembly
  automatically (`proceed`). Proceed authorizes this release's selected PRs and
  verified squash restacks; pause requires one confirmation before assembly.

Immediately ask for all missing choices together, then wait. Ask only for missing
answers; do not assume defaults or treat strategy selection as merge permission.
Interpret “merge commit” as one strategy; clarify a bare “commit” if ambiguous.
Resolve these choices before discovery, record creation, Git operations or PR
publication. Explicit choices and authorization persist for the same release;
resume them without asking again. A recorded legacy default is not a user choice.
Record both choices and their direct user evidence in `extensions.merge_options`
under `strategy`, `approval`, and `evidence`. Read the shared preparation contract
for scoped authorization. Staging authorization remains separate.

Coordinate `open-stack-requests`, `merge-stack`,
`rebuild-staging-with-branches`, and `verify-staging-acceptance`.
Read those skills from their installed sibling directories; stop if a required
skill or its release mode is unavailable.
Keep operational steps in those skills. This workflow
launches no code review loops, implements no features, and leaves production
unchanged.

## Inputs

Use the selected release's ordered, already-pushed branches, dependency pins,
verification evidence, and release ID. Link contributing build manifests for
scope and branch evidence; an explicit user branch list is also supported. Do not
require draft PRs. Resolve the remote default branch unless the user names a
base. Use the upfront merge choices; obtain missing staging authorization at its
deployment boundary.
Validate contributing schema-v2 build records with the operational validator
before selecting qualification evidence. Reconcile historical records explicitly
before adoption; legacy validation does not supply dashboard state.
Release preparation records and deployment receipts use their own contracts;
do not apply the build review-record schema to them.

Read `references/release-preparation.md`. Create the preparation record without
rewriting the build manifest's parent pins, targets, or reviews. Apply only the
shared path-migration rules when stage moves affect its freeze digest.
Link it from each contributing manifest's integration state when present.
For active builds, follow the shared Concurrent Build Snapshot rules: pin a
qualified prefix in separate preparation state, return results to its coordinator,
and obtain a handoff before source mutation. Do not freeze unfinished queue work.
Create new records under `plans/releases/active/<release-id>/`; resolve existing
records on resume. Follow the shared record's lifecycle moves and preserve links
to builds and deployment receipts without copying their evidence.

## Release Identity

Use the user's release ID or generate `stack-release-<YYYYMMDDTHHMMSSZ>` once
from UTC time. Require an unused record path and integration ref; append a short
random suffix on generated-ID collisions. Never overwrite an existing release.
Record the creation time and ID source. Before publishing PRs, show the ID,
record path, and integration branch; explain that the ID identifies a candidate,
not a completed release or Bitbucket tag.

Resume unchanged scope and pinned inputs, including recorded verified squash
restacks, under the same ID and ref, regardless of elapsed time. A replacement
after separately authorized fixes or scope changes gets a new ID. Preserve and
link both records; mark the old candidate superseded once its replacement is
established. Other changed inputs require fresh merge
authorization and applicable acceptance. No nested attempts directory is needed.

## Prepare And Publish

1. Pin the remote base, source and parent SHAs, and merge order. Validate ancestry
   and release membership, including inherited commits. Preserve the primary
   checkout; use an isolated checkout for Git operations.
2. Create a fresh `release/<release-id>` at the pinned base,
   or use the exact name the user supplied. Push with an explicit absence lease
   and verify it. On resume, require the recorded ref; do not overwrite a
   pre-existing branch from another run. Never assemble from old staging.
3. Delegate `open-stack-requests` in `release` mode under **Publishing Owners**
   below. Each owner creates one fresh non-draft PR, using its predecessor target
   for a clean stacked diff or integration for an independent root.
   For squash, compose each own-change message under
   `merge-stack/references/git-commit-message.md` and fingerprint it with
   `merge-stack/scripts/merge_message.py`; save files and hashes in preparation
   extensions before presenting the PRs.
4. Present all PR links, descriptions, pinned source SHAs, merge order, selected
   strategy, and proposed squash messages. With `approval: pause`, obtain one
   confirmation for assembly and verified squash restacks. With `approval: proceed`,
   continue using the user's upfront authorization. Record its exact scope in the
   merge journal before mutation. Resume an unchanged authorized run without
   another confirmation.

## Assemble, Test, And Publish The Release

1. Call `merge-stack` in `release` mode with the selected strategy and approval
   choice. It merges each PR into integration and retargets successors. Squash
   adds one commit per PR with a composed message and verified successor restacks;
   merge commits retain source history. Stop for conflicts or drift. Do not repair
   code or launch reviews automatically. Record the assembled candidate commit and tree.
   Advance included `review` slices to `in_release`, record pinned membership,
   reconcile parents, and repair manifest paths under the shared layout. For an
   active build, return these results to its coordinator for shared writes.
2. Within staging authorization, call `rebuild-staging-with-branches` with the
   integration branch as its **sole input**, the original base branch, and
   `expected_candidate_sha` equal to the assembled commit. The exact-candidate
   guard must pass before any remote mutation. Reuse that skill's backups,
   deployment, checks, and receipt; do not create an MR into staging.
   Assign pre-deployment integration checks and pipeline/deployment health to that
   runner; pass the deferred checklist so no build obligation disappears in transit.
3. Delegate `verify-staging-acceptance` under **Acceptance Owners** below.
   Import every assigned result and required human/external evidence for this
   deployed candidate. Deployment success alone is not acceptance. Record
   acceptance only when all requirements pass or have an authorized limitation
   decision; leave unavailable evidence pending with its owner and procedure.
   Assign deployed-runtime acceptance and any activation/account/device/operator
   proof separately, regardless of executor. Keep later activation obligations
   linked to their explicit blocking milestone; never infer release acceptance
   from successful branch tests, CI or deployment smoke checks.
   Proceed to final publication only after aggregate acceptance qualifies.
4. Require the remote integration still equals the tested candidate and the
   remote base still equals its pin. If either moved, stop for updating and
   retesting. Call `open-stack-requests` in `release-final` mode to create the
   integration-to-base PR with delivered scope, individual PR links, and a concise
   acceptance summary under the publication skill's description rules.
5. Leave that PR open for the final reviewer. Authorization for individual
   assembly merges does not authorize merging it. Retain `in_release` through
   staging, acceptance, and final PR review. Keep feature plans out of
   slice and spec `merged/` and `fulfilled/` folders until the final merge is
   confirmed. Then use `merged` while required acceptance remains outstanding,
   or `fulfilled` once satisfied, under the shared layout.

## Publishing Owners

Read `references/orchestration-runtime.md`. Use its implementation-owner provider,
transport, isolation and same-session rules for one persistent owner per selected
branch, named `<branch name without feature/> - Publishing`. Match the coordinator's
provider; ChatGPT/Codex owners are separate GUI-visible project chats. Keep these
owners separate from implementation and acceptance owners; native sub-agents do
not own publication. Reuse each recorded ID for recovery and follow-up.

Assign the absolute `open-stack-requests/SKILL.md` path, `release` mode, one change,
repository/release record, pinned source/parent/destination branches and SHAs,
branch-only scope and evidence, private metadata/result paths, and coordinator
identity/return route. Owners prepare descriptions and verify pins, then return
the exact creation metadata and authenticated author for the coordinator to record
as intent. Authorize creation of that assigned PR only after its intent is saved.
Owners save provider results immediately in their private paths and return PR
ID/URL, author, source/destination SHAs, metadata, verification and outcome.

Dispatch every eligible owner concurrently within actual agent/provider capacity;
50 PRs may use 50 owners when capacity permits. Fill capacity as results arrive,
without fixed waves or waiting for predecessor PRs: destination branches already
exist. Record actual capacity/rate-limit blockers; retain merge order for assembly.
Unknown creation outcomes require reconciliation before retry or reassignment.

The coordinator alone writes the canonical release record and merge journal,
imports intents/results promptly, validates identities/uniqueness and records each
owner's provider, persistent ID/name, assignment/pins, checkout, status and evidence
under `extensions.sessions`. Owners only publish their assigned PR; source changes,
retargeting and merging remain with the coordinating workflow. Require every PR's
verified result before presenting the complete set or starting assembly. The final
integration-to-base PR remains one coordinator publication in `release-final` mode.

## Acceptance Owners

Read `references/orchestration-runtime.md` for provider selection, persistent
chat creation, messaging, progress, execution ownership, and recovery. Apply
its implementation-owner transport rules to acceptance owners. Match the
coordinator's provider by default; ChatGPT/Codex owners are separate GUI-visible
project chats. Native sub-agents do not own acceptance.

Create or resume one acceptance chat per selected feature branch, or one for
an approved dependency chain, named `<branch name without feature/> - Acceptance`.
For a chain, use its first branch and record all assignments. Reuse that ID for
clarifications, missing evidence, and retests; keep implementation owners separate.

Assign the absolute `verify-staging-acceptance/SKILL.md` path, repository and
release record, source branch/parent pins, assembled candidate commit/tree,
staging URL and deployment receipt, acceptance IDs and scenarios, permitted
test data/settings, evidence directory, coordinator identity and return route.
Include deferred integration/activation check IDs, procedures, prerequisites,
blocking milestones, owners and fresh/reusable evidence. Assign every selected
obligation once or record why it belongs to a later milestone; do not drop a check
because its original executor was an implementation agent.
Every owner tests the same deployed candidate. Assign shared cross-branch
scenarios explicitly to one owner and cover every release acceptance requirement.
Run independent tests concurrently; serialize tests sharing mutable fixtures,
accounts, or settings.

Record owner provider, persistent ID, exact name, assigned requirements,
candidate/environment, status and evidence links in release `extensions.sessions`.
Owners write their assigned evidence and return results; the coordinator alone
updates canonical acceptance and shared lifecycle records. Retrieve handoffs
promptly through the runtime's progress tools. Reconfirm the live candidate and
relevant configuration before aggregating results. Record `acceptance.status`
as `passed` when every requirement passes, `accepted` when explicit authorized
decisions cover remaining limitations, `failed` for unresolved failures, or
`pending` for missing evidence. Link the aggregate evidence and cleanup state.
Route defects to the existing implementation owners through the build coordinator;
acceptance owners do not fix code. A replacement deployment requires rechecking
candidate identity and evidence applicability before retests in the same chats.

## Report

Return the preparation record, merge journal, individual PRs, publication owner
IDs/names and outcomes, candidate commit and tree, staging receipt, acceptance
owner IDs/names and evidence, final PR, and outstanding blockers.
Keep these audit fields in records and the coordinator handoff; PR bodies follow
`open-stack-requests/references/change-request-description.md`.
Distinguish published, awaiting merge confirmation, assembled, deployed,
accepted, and awaiting final review. Attach created PRs to the current chat
when the app supports PR attachments.
