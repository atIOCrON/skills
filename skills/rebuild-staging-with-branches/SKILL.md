---
name: rebuild-staging-with-branches
description: Reproducibly build a frozen release manifest, replace staging once, and verify the deployed candidate.
disable-model-invocation: true
metadata:
  layer: runner
---

# Rebuild Staging With Branches

Make staging match one tested candidate from a frozen release manifest. Do not
change master, deploy production, or disturb existing local work. Use a
separate disposable checkout.

## Input

Read `references/release-manifest.md`. Require and validate the canonical JSON
manifest; do not reconstruct release scope from a Sheet, prose list, local
branches, or staging history. Require `state: frozen` and verify every recorded
Git ref, SHA, exclusion, dependency, all three review mappings, and evidence
path.

A frozen candidate has no branch-count limit. If its graph or acceptance cost
is risky, report a supported split recommendation, but do not shrink or reject
the user's release scope because of size.

## Build

1. Fetch origin. Re-resolve the manifest's base and branch tips to their full
   SHAs. Check staging directly on origin and record its SHA or absence.
   Exclude uncommitted changes. Stop on manifest or remote drift.
2. Create `feature/staging-integration/<UTC-timestamp>` from the pinned base.
   Merge the pinned feature SHAs in manifest order, preserving demonstrated
   ancestry. Do not merge old staging, infer extra branches, or include a
   manifest exclusion.
3. Classify every conflict:
   - a behavioral or patch-preimage conflict is dependency evidence or a
     product decision;
   - a generated `composer.lock` or routine `composer.json` conflict is not a
     dependency by itself. Regenerate it with the pinned toolchain and locked
     inputs, then prove the result deterministically.
4. Resolve authorized integration conflicts only in the integration checkout.
   Never rewrite or restack source branches to repair an integration-only
   resolution. If source behavior is defective, return only the affected
   branch and demonstrated descendants to `build-branch-stack`.
5. Write a conflict-resolution report recording files, classification,
   resolution, commands, and resulting tree. With unchanged pinned inputs,
   revise only the integration resolution and impacted checks; do not rebuild
   or rereview the source stack.

Record the exact merge order, input SHAs, toolchain, commands, candidate commit
and tree SHAs, and conflict report under `integration` in the manifest. A
repeat build from the same inputs may have a different commit timestamp, but it
must produce the same tree unless the report explains the difference.

## Validate

- Confirm the pinned base and every included feature tip are ancestors of the
  candidate, and no exclusion is an ancestor solely through an accidental
  merge.
- Run Claude, Codex, and Cursor when manual conflict resolutions or
  integration-specific behavior require review. Do not rereview already clean
  logical changes or proven equal-range-diff restacks.
- Use the exact CI PHP, Composer, architecture, and lock inputs where the
  repository provides them. Reuse only checksum-keyed Composer and pristine
  vendor caches; a cache hit is not verification.
- Run one clean locked dependency install for the candidate. Replay patches in
  declared order. Select focused tests from every branch's declared surfaces
  and checks, then run combined risk-based smoke tests.
- Record checks against the candidate SHA and tree SHA. Do not reuse results
  after either changes unless their applicability is proven.

Stop on an unresolved product decision, failed required check, undeclared
dependency, manifest drift, or unexplained tree difference.

## Replace Staging

Inspect deployment scripts from the candidate and preserve their guards. Check
for active staging deployments. Record the running release and rollback
artifact. Recheck remote staging immediately before mutation.

If staging exists, create and verify this remote backup with an explicit
absence lease; never overwrite it:

```text
backup/staging-before-rebuild/<UTC-timestamp>-<12-character-sha>
```

Push and verify the unique integration branch, then update staging once to the
candidate SHA with an explicit lease. Never use plain `--force`, bypass branch
protection, or deploy intermediate commits. If the lease fails, recheck active
deployments and back up the new tip before one retry; stop if updates continue.

Follow one staging pipeline for the candidate SHA. If staging already runs that
candidate, do not redeploy unless the running release is unhealthy or differs.
Verify remote staging, deployed release, pipeline result, application health,
and manifest-selected regressions. Establish rollback compatibility before any
recovery action.

Update the manifest to `staged` only after candidate identity and deployment
are verified. Record previous and deployed releases, rollback release,
pipeline, checks, acceptance state, and evidence.

## Report

Report the manifest path, source SHAs, integration branch, candidate commit and
tree SHAs, conflict report, backup or prior branch absence, previous and
deployed releases, pipeline result, checks, accepted gaps, and unresolved
failures. Distinguish deployment success from acceptance results.
