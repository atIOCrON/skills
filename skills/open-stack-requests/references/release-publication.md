# Release Publication

Use this path for `release` and `release-final` modes. It bypasses the draft
build lifecycle, not repository requirements. Read `release-preparation.md`,
`change-request-description.md`, and the Bitbucket provider reference's release
section. These modes launch no code review loops and never send work to
`build-branch-stack` automatically.

Require the release preparation record and verified remote input SHAs. Check
existing build evidence when supplied; do not create review requirements or
mark missing reviews passed. Preserve unrelated dirty work and inspect the
pinned commit diff in an isolated checkout.

For `release`, publish every recorded change with its initial destination.
Require its parent pin to remain an ancestor and verify the source still equals
the recorded head. Independent roots target integration; stacked changes target
their selected predecessor. Reject inherited work outside the release. Explain
dependencies and testing in each description; do not include predecessor
changes as if they belong to this feature.

Apply the description guide's audience rules before publication. Individual PRs
describe their own change, checks, and risks; keep release bookkeeping in the
preparation record and handoff.

Under `prepare-release-integration`, each persistent ` - Publishing` owner handles
only its assigned change. Prepare metadata and verify pins, then return the exact
intent to the coordinator. Create the PR after the coordinator confirms that intent
is saved; persist the result in the assigned private path and return it for import.
The coordinator alone updates canonical records. Owners run concurrently against
existing pinned destination branches; predecessor PR creation is not a prerequisite.
Resume an unknown outcome by reconciling that intent before any retry. An assigned
owner ends after its own handoff; it does not dispatch owners or publish other PRs.

For `release-final`, publish only the assembled integration branch against the
original base. Require recorded acceptance on this exact candidate and tree,
and require the remote base still equals its pinned SHA. If the base moved,
stop for updating and retesting the candidate; do not silently rebuild it.

The final description summarizes delivered behavior, included PR links, acceptance
results, outstanding limitations, and material deployment/rollback requirements.
Explain any authorized reuse of acceptance and relevant candidate differences.
Keep exact candidate/base/tree pins and local evidence paths in the release
record; include only reviewer-accessible links needed to assess the release.

Create one JSON metadata file per PR with `title`, `description`, and optional
`reviewers` UUID objects. Do not add reviewers or send separate notifications
unless the user requested them or repository policy requires them. Use:

```bash
python3 scripts/bitbucket_cloud.py origin create \
  <source> <destination> <full-source-sha> <full-destination-sha> <metadata.json>
```

The shared adapter creates a non-draft PR with source retention. Record intent
before calling it and save the result immediately. Recover only this run's
matching PRs on resume; fresh runs do not assume drafts exist. Verify metadata,
author, identities, and uniqueness after publication. Respect configured checks
when merging; pending checks need not prevent opening a PR for review.

Report every PR URL, destination, source SHA, and dependency order. End without
merging. Publication does not grant merge authorization.
