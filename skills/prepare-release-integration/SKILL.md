---
name: prepare-release-integration
description: Prepare a Bitbucket release through individual PRs, pause for merge confirmation, assemble it, test the exact candidate on staging, and open the final PR to the base branch.
disable-model-invocation: true
metadata:
  layer: runner
---

# Prepare Release Integration

Coordinate `open-stack-requests`, `merge-stack`, and
`rebuild-staging-with-branches`. Read those skills from their installed sibling
directories; stop if a required skill or its release mode is unavailable.
Keep operational steps in those skills. This workflow
launches no code review loops, implements no features, and leaves production
unchanged.

## Inputs

Use the selected release's ordered, already-pushed branches, dependency pins,
verification evidence, and release ID. Prefer an existing build manifest for
scope and evidence; an explicit user branch list is also supported. Do not
require draft PRs. Resolve the remote default branch unless the user names a
base. Accept explicit upfront authorization for merging and staging deployment;
otherwise obtain missing authorization at the relevant boundary.

Read `references/release-preparation.md`. Create the preparation record without
rewriting the build manifest's parent pins, targets, reviews, or freeze digest.
Link it from that manifest's integration state when present.
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

Resume unchanged scope and pinned inputs under the same ID and ref, regardless
of elapsed time. A replacement after separately authorized fixes or scope changes
gets a new ID. Preserve and link both records; mark the old candidate superseded
once its replacement is established. Changed inputs require fresh merge
authorization and applicable acceptance. No nested attempts directory is needed.

## Prepare And Publish

1. Pin the remote base, source and parent SHAs, and merge order. Validate ancestry
   and release membership, including inherited commits. Preserve the primary
   checkout; use an isolated checkout for Git operations.
2. Create a fresh `feature/release-integration/<release-id>` at the pinned base,
   or use the exact name the user supplied. Push with an explicit absence lease
   and verify it. On resume, require the recorded ref; do not overwrite a
   pre-existing branch from another run. Never assemble from old staging.
3. Call `open-stack-requests` in `release` mode with the record. It creates fresh
   non-draft PRs, one per change, using predecessor targets for clean stacked
   diffs and integration for independent roots.
4. Present all PR links, descriptions, pinned source SHAs, and merge order.
   **Pause before merging unless explicitly authorized upfront.** Record direct
   user authorization in the merge journal as defined by the shared record.
   Resuming an unchanged authorized release does not need another confirmation.

## Assemble, Test, And Publish The Release

1. Call `merge-stack` in `release` mode with `strategy: merge-commit`. It merges
   each PR into integration, retargets successors, preserves source heads by
   default, and stops for conflicts or drift. Do not repair code or launch
   reviews automatically. Record the assembled candidate commit and tree.
2. Within staging authorization, call `rebuild-staging-with-branches` with the
   integration branch as its **sole input**, the original base branch, and
   `expected_candidate_sha` equal to the assembled commit. The exact-candidate
   guard must pass before any remote mutation. Reuse that skill's backups,
   deployment, checks, and receipt; do not create an MR into staging.
3. Record acceptance for this deployed candidate from the release's applicable
   tests and human/external evidence. Deployment success alone is not acceptance.
   Pause only for required acceptance evidence the skill cannot obtain. Reuse
   valid unchanged evidence; no blanket review or test reruns.
4. Require the remote integration still equals the tested candidate and the
   remote base still equals its pin. If either moved, stop for updating and
   retesting. Call `open-stack-requests` in `release-final` mode to create the
   integration-to-base PR with individual PR links and acceptance evidence.
5. Leave that PR open for the final reviewer. Authorization for individual
   assembly merges does not authorize merging it. Keep feature plans out of
   slice and spec `merged/` and `fulfilled/` folders until the final merge is
   confirmed. Then use `merged` while required acceptance remains outstanding,
   or `fulfilled` once satisfied, under the shared layout.

## Report

Return the preparation record, merge journal, individual PRs, candidate commit
and tree, staging receipt and acceptance, final PR, and outstanding blockers.
Distinguish published, awaiting merge confirmation, assembled, deployed,
accepted, and awaiting final review. Attach created PRs to the current chat
when the app supports PR attachments.
