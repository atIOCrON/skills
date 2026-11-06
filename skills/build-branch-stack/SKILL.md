---
name: build-branch-stack
description: Build approved slices as a linear branch stack, verify individual implementations, and hand integration testing to release/staging workflows. Support explicit scope or the to_do spec queue with parallel implementation and one canonical build manifest.
disable-model-invocation: true
metadata:
  layer: runner
---

# Build Branch Stack

Build and push approved executable slices from explicit scope or the approved
`plans/specs/to_do/` queue. Finish with individually verified branches in `review/`
and a canonical build manifest.

## Contracts and ownership

Read these references before selection, moves, edits, branch creation/adoption or
dispatch; each owns the named rules:

| Reference under `references/` | Authoritative rules |
| --- | --- |
| `operational-records.md` | Schema-v2 JSON, receipts, counts, operator handoffs and validation |
| `orchestration-plans-layout.md` | Approval, stages, parent reconciliation, moves and legacy paths |
| `orchestration-runtime.md` | Persistent owners, providers/transports, execution leases, IDs and sessions |
| `queue-build.md` | Selection/resumption, spec blocks, authoring/accepted pins and release ownership |
| `implementation-readiness.md` | Pre-move inspection, slice cohesion and dispatch readiness |
| `scheduling.md` | Eligibility, parallel capacity, isolation and waiting reasons |
| `review-convergence.md` | Failure families, architecture reassessment, fix limits and review cap |
| `build-handoff.md` | Build progress, final reporting and concurrent release handoffs |

Invocation adds no credentials/external authority.

## Autonomous decision authority

An authorized build permits repository-local implementation, verification,
architecture, narrow dependency correction, plan amendments and slice decisions
needed for selected approved release scope without further approval when they:

- serve existing acceptance or a demonstrated prerequisite;
- preserve outcomes, exclusions, binding contracts and release membership;
- retain coherent implementation and rollback boundaries;
- add no independently releasable product capability;
- use the narrowest viable native owner or supported extension; and
- waive no evidence gate and require no production, destructive, credential,
  financial, legal or external-communication authority.

New product outcomes require a scope decision. Require a human only to change
product/release/frozen scope, acceptance/exclusions, binding contract/policy,
required evidence, broad upstream ownership, or authority outside the above.

## Workflow

1. Select/resume and initialize pinned v2 scope under `queue-build.md`.
2. Dispatch all eligible work under `implementation-dispatch.md`/`scheduling.md`.
3. Coordinate acceptance/restacks under `queue-build.md`, `git-branch-commit.md`
   and `git-sync-branch.md`.
4. Read `trim-review.md` then `code-review-loop.md`.
5. Run `artefact-audit.md` at handoff and report under `build-handoff.md`.
6. Route authorized draft publication to `open-stack-requests` before release
   assembly; hand selected releases to `prepare-release-integration`.
   This skill opens no CR.

Read `references/release-manifest.md` for build metadata and
conditional historical maintenance.
