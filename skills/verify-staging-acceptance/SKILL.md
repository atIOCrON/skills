---
name: verify-staging-acceptance
description: Test the candidate already deployed on staging against assigned acceptance requirements and record passed, failed, and pending results.
disable-model-invocation: true
metadata:
  layer: runner
---

# Verify Staging Acceptance

Test existing staging behavior against acceptance requirements. Assembly,
installation, code changes, deployment, and PR publication belong to other skills.

Return test evidence in both delegated and standalone runs. The release
coordinator records aggregate acceptance in canonical release records.

## Pin Scope And Environment

- Read repository testing instructions, approved acceptance requirements, and
  the supplied release/build records and deployment receipt. A release record
  is optional for standalone testing; explicit requirements and a verified
  deployed identity suffice. Preserve release membership and source pins.
- Confirm the live staging candidate commit/tree and environment. Compare them
  with the assigned candidate and receipt; a branch pointer or successful
  pipeline alone does not prove what is running. Stop on identity mismatch.
- Pin the candidate, environment, relevant configuration, assigned acceptance
  IDs, scenarios, test accounts/data, evidence directory, and known limitations.
  Under delegation, test only the assigned scope.
- Identify agent-run, human, and external checks. Record unavailable credentials,
  services, procedures, and owners as pending; never infer a pass.

## Test And Record

- Run applicable behavior tests against the deployed application: assigned
  journeys, shared-feature interactions, relevant failure cases, and observable
  external results. Derive checks from acceptance requirements and risk.
- Reuse passed evidence only when the candidate and all determining environment,
  configuration, data, and external inputs remain equivalent. Record its source
  and applicability; rerun when equivalence cannot be proved. Build checks and
  deployment smoke tests alone do not establish acceptance.
- Use permitted fixtures and reversible test settings. Coordinate shared mutable
  resources with other owners; do not deploy or change application code, schema,
  or dependencies to make tests pass. Preserve unrelated data and settings.
- Record each requirement as passed, failed, or pending with its procedure,
  expected/observed behavior, candidate identity, evidence, and owner. For defects,
  identify the owning feature and demonstrated affected scope; return findings
  for implementation repair without launching implementation or review loops.
- Remove created fixtures and restore temporary settings. Report incomplete
  cleanup with its exact remaining state and owner.
- Recheck live identity and relevant configuration after testing. A deployment
  or determining-input change requires reconciliation; do not combine results
  from different candidates into one acceptance claim.

## Handoff

Return owner/coordinator IDs, candidate commit/tree, staging environment,
assigned requirements, fresh/reused results, evidence paths, defects, cleanup,
required human/external decisions, and pending procedures/owners. Preserve
original results and pins across retests.

Return the report without changing release or build records. The release
coordinator aggregates results and records acceptance only when every requirement
passes or has an explicit authorized limitation decision for this candidate.
Pending evidence remains pending. Acceptance neither merges the release nor
authorizes production deployment.
