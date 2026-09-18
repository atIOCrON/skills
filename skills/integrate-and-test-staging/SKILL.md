---
name: integrate-and-test-staging
description: Test and accept one frozen manifest candidate on staging with exact, reusable build inputs.
disable-model-invocation: true
metadata:
  layer: runner
---

# Integrate And Test Staging

## Prepare

- Read repository and deployment instructions plus
  `references/release-manifest.md`.
- Require and validate the canonical manifest. Use it for scope, dependencies,
  exclusions, surfaces, checks, accepted gaps, candidate identity, and rollback;
  do not reconstruct them from a Sheet or conversation history.
- Require one frozen candidate commit and tree. If integration is not built,
  use `rebuild-staging-with-branches` first.
- Freeze acceptance scope before deployment. A critical late addition requires
  an authorized thaw and invalidates affected build, pipeline, and acceptance
  evidence. Do not impose a numerical release-size limit.

## Integrate

- Use the manifest's isolated integration branch and pinned candidate, not
  current staging as a source branch.
- Preserve source branches. When review is required for manual conflict
  resolutions, integration-specific behavior, or unexplained deltas, run
  Claude, Codex, and Cursor. Retain all three reviews for unchanged branches
  and proven equal-range-diff restacks.
- Use the repository's pinned CI container or exact PHP, Composer, architecture,
  and lock versions. Record any unavoidable mismatch.
- Reuse persistent Composer and pristine-vendor caches only when keyed by exact
  package version and checksum. Replay patches in declared order.
- Run one clean locked install per candidate SHA and tree. Reuse its evidence
  only while candidate, toolchain, lock, and cache provenance remain unchanged.
- Select focused tests from each branch's declared surfaces and checks, then run
  combined smoke tests based on cross-branch risk.
- Create or refresh the integration CR from the manifest when authorized,
  documenting scope, conflicts, validation, settings, rollback, and accepted
  gaps.

## Deploy

- Deploy only within the user's authorization. Run one staging pipeline for the
  frozen candidate; do not redeploy an identical healthy candidate.
- Record the previous release and verified rollback path.
- Apply only required code, configuration and database changes.
- If deployment fails, inspect its state before retrying or rolling back.
- Verify the active release and site availability.

## Validate

- Run the full risk-based staging acceptance checklist once for the deployed
  candidate. Test each declared surface, relevant failure case, and external
  result.
- Remove test fixtures and restore temporary settings.
- Record each unresolved gap with evidence, impact, owner, and an authorized
  accept-or-fix decision. Do not force unrelated repairs; return only a defect's
  owning branch and demonstrated descendants to implementation.
- Set the manifest to `accepted` only when required acceptance passes or every
  remaining limitation has an authorized decision.

## Report

State the manifest and candidate SHAs, toolchain, clean install, pipeline,
deployed and rollback releases, what passed, accepted gaps, unresolved defects,
cleanup, and evidence paths. Distinguish deployment status from acceptance.

Leave production unchanged.
