---
name: write-specs
description: Write proportionate specifications with stable acceptance IDs, justified verification, trim loops, and approval states. Use write-slices before implementation.
disable-model-invocation: true
metadata:
  layer: capability
---

# Write Specifications

Write the parent specification for a complete product or system outcome. A
specification may cover several related behaviours, providers, or delivery
increments. It is not an executable branch plan.

Resolve `plans/...` against the user's primary local checkout of the target
repository, or another local directory they explicitly designate. Do not use
an agent worktree as the plan root merely because it is the current directory.
Read `references/orchestration-plans-layout.md` for moves and legacy migration.

Create a new specification at:

```text
plans/specs/draft/<spec_slug>/<spec_slug>.md
```

For an update, locate the existing specification by slug across spec status
directories and edit it there. Move its whole folder only for a status change
or legacy migration; refresh links to the specification and its slice map.
Keep slice implementation stages under `plans/slices/` separate from spec
statuses. Classify legacy files before migrating; never treat a slice as a spec.

Use a lowercase `snake_case` slug of at most 40 characters. Inspect relevant
code, contracts, documentation, and established extension points before
writing. Report the absolute specification path.

## Specification Lifecycle

Require a `Specification Status` section with exactly one value, matching the
folder under `plans/specs/`:

- `draft`: still being defined; `write-slices` must not decompose it.
- `approved`: explicitly approved by the user; slices may be created and built.
- `fulfilled`: every mapped slice is in `plans/slices/done/`, its merge is
  confirmed, and required acceptance passed or was explicitly accepted.
- `superseded`: replaced by a named specification and no longer actionable.

Create specifications as `draft`. Never infer approval from a request to write
or update one. Change `draft` to `approved` only on explicit user approval.
Move its folder from `draft/` to `approved/` with that status update.
`merge-stack` changes `approved` to `fulfilled` and moves the folder after
proving completion. Change a specification to `superseded` and move it to
`superseded/` only when the user identifies its replacement.

Changes to acceptance IDs, scope, binding decisions, authorized complexity,
required verification, or external acceptance return an `approved` or
`fulfilled` specification to `draft` and move its folder to `draft/`.
Mark an existing slice map `stale`; affected slices cannot start until the
specification and revised map are approved.
Clarifications that preserve those contracts retain the current status. Report
every status transition and why it occurred.

## Scale The Initial Plan

Start with the smallest sufficient change. Inspect its owned behaviour, failure
impact, and effects on persistence, public contracts, and runtime coordination.
Scale design and verification to those risks. Small fixes may need only a short
specification and one slice.

Use existing platform behaviour, tests, and release procedures. Add machinery
or gates only for demonstrated gaps; inspect uncertainty before adding scope.

## Required Content

- Observed problem and evidence.
- Specification status.
- Complete outcome and affected capability.
- Explicit non-goals and binding constraints.
- Stable acceptance IDs (`AC-01`, `AC-02`, ...), each expressing one observable
  behaviour or verifiable system property.
- Agent-run verification sufficient to prove the changed behaviour and relevant
  preserved contracts.

Include applicable decisions, dependencies, external acceptance, and authorized
complexity. For required new or modified tables and views, specify name, grain,
columns, types, nullability, keys, relationships, and important semantics.
Omit inapplicable topics or write `none`; do not invent work to fill a template.

## Acceptance Cohesion

Group requirements by the outcome they prove. Do not hide independent
implementations behind aggregate wording such as "every enabled method" when
providers, lifecycle owners, failure modes, or acceptance procedures differ.
Assign stable IDs now; `write-slices` will give each ID one owning
slice.

Source-text, snapshot, or patch-shape assertions may protect structure. They do
not prove browser activation, DOM replacement, concurrency, retry, cancellation,
provider callbacks, current totals, or other runtime lifecycle behaviour.
Use the least costly verification sufficient to establish those behaviours.
Add executable coverage only where existing checks or inspection cannot establish
them; record real-provider or real-environment acceptance separately when needed.

## Authorized Complexity

For every added or materially expanded architectural layer, dependency,
configuration option, persistent object, public interface, compatibility
behaviour, or supported scenario, state:

- the demonstrated problem and acceptance ID that require it;
- why the platform's native owner or extension point cannot satisfy it;
- why an upgrade, upstream correction, or smaller compatibility change is
  insufficient; and
- how it can be removed or rolled back.

Justify only changed responsibilities; write `none` if no complexity is added.
General lifecycle coordination, shared mutable browser state, cross-provider
state machines, retry or recovery frameworks,
whole-template vendor replacements, and local ownership of upstream package
behaviour are architectural layers. Broad acceptance criteria do not authorize
them implicitly.

## Proportionate Verification

Use the smallest sufficient checks for each acceptance condition and plausibly
affected contract. Reuse existing checks; broader checks require broader impact
or binding repository policy.

Distinguish one-time verification from ongoing regression coverage. Existing
checks, diff review, or direct inspection may satisfy acceptance; each acceptance
ID does not require a new test. Add tests only for credible failures in behaviour
or integration the project continues to own. Do not duplicate upstream coverage
solely because native behaviour is being restored.

Do not add tests asserting that removed project-owned customizations remain
absent. Confirm removal through one-time inspection. Absence assertions are
appropriate when retained project-owned behaviour must continue suppressing
upstream behaviour.

For any added fixture, harness, service dependency, full API or end-to-end run,
manual acceptance step, or observation window, state the failure it detects and
why cheaper checks cannot. Prove changed runtime behaviour at a sufficient
executable seam; source assertions may supplement it. Do not reconstruct
unchanged upstream lifecycles with fakes.

Require human or external acceptance only when behaviour needs that environment
or authority; otherwise use `none`. Routine deployment monitoring becomes a
gate only for a demonstrated delayed failure or binding policy. Preserve user
requirements and mandatory repository gates; do not invent staging sign-off
or waiting periods.

Example: declaring existing properties ordinarily needs checks that warnings
disappear and delegation and returned data remain correct. Database fixtures,
full API flows, or a 24-hour gate require evidence of additional affected risks.

## Trim Loop Before Handoff

Trim before presenting the draft for approval and after revisions add scope,
machinery, or verification.

1. Tie responsibilities, added checks, and gates to user requirements, binding
   contracts, or demonstrated risks. Remove speculative and template-driven work.
2. Compare with the smallest viable design using native ownership and existing
   checks. Remove unnecessary layers, mechanisms, duplicate criteria, fixtures,
   and gates.
3. Review verification separately. For each proposed new test, fixture, harness,
   or gate, identify the credible failure it catches that remaining checks would
   miss. Remove checks that only confirm deletion, duplicate coverage, or guard
   against hypothetical future changes. Agent-proposed gates remain eligible
   for removal.
4. Confirm requirements and behavioural proof remain sufficient. Preserve
   acceptance IDs; never silently renumber them or waive user requirements or
   gates required by the user or binding repository policy.
5. Repeat only after a material reduction. Stop when no justified reduction
   remains; do not manufacture findings or require repeated clean passes.

Briefly report reductions or why the draft is proportionate. Apply existing
lifecycle rules to approved contract changes; add no approval stage, ledger,
or mandatory reviewer fleet.

## Planning Rules

- Authorize only the least-complex outcome that meets the acceptance conditions
  and preserves binding contracts. Do not plan for hypothetical future needs.
- Keep outcomes separate from implementation mechanisms. Exact control flow,
  polling, replay, timeouts, API calls, parsing, storage, files, and line numbers
  belong to implementation unless a user decision or binding invariant makes
  them mandatory.
- Use a substitution test: when materially different designs can satisfy the
  requirement, specify their shared result rather than choosing one.
- Treat linked APIs and current implementations as evidence, not mandatory
  procedure, unless the user or a binding contract requires them.
- Scope boundaries limit the deliverable; they must not trap the design. A ban
  on a module, extension point, dependency, service, or interface is a design
  constraint. Include it only when required by the user, policy, contract, or
  deployment environment.
- Translate audit and defect recommendations into required outcomes unless the
  user explicitly adopts the proposed mechanism.
- Preserve every actual user requirement. Keep the specification concise,
  high-level, and internally consistent.

After writing and trimming, state that the specification must be approved and
decomposed by `write-slices` before `build-branch-stack` can implement it.
