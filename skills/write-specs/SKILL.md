---
name: write-specs
description: Write feature specifications with stable acceptance IDs, explicit architecture boundaries, verification requirements, and a lightweight approval lifecycle. Use write-slices before implementation.
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

Create a new specification at:

```text
plans/specs/<spec_slug>/<spec_slug>.md
```

For an update, edit the existing specification in place. Never move a
specification through `backlog`, `to_do`, `in_progress`, `review`, or `done`;
those stages are for vertical-slice implementation plans. If an older broad
specification exists elsewhere under `plans/`, migrate it to `plans/specs/`
when safe, update its references, and do not leave a duplicate. Do not migrate
a genuine vertical-slice plan.

Use a lowercase `snake_case` slug of at most 40 characters. Inspect relevant
code, contracts, documentation, and established extension points before
writing. Report the absolute specification path.

## Specification Lifecycle

Keep the specification at its stable path. Require a `Specification Status`
section with exactly one value:

- `draft`: still being defined; `write-slices` must not decompose it.
- `approved`: explicitly approved by the user; slices may be created and built.
- `fulfilled`: every slice is in `done/` and required acceptance passed or was
  explicitly accepted.
- `superseded`: replaced by a named specification and no longer actionable.

Create specifications as `draft`. Never infer approval from a request to write
or update one. Change `draft` to `approved` only on explicit user approval.
`merge-stack` may change `approved` to `fulfilled` after proving completion.
Change a specification to `superseded` only when the user identifies its
replacement.

An edit to acceptance IDs, scope, binding decisions, authorized complexity, or
external acceptance returns an `approved` or `fulfilled` specification to
`draft`. If a slice map exists, mark its status `stale`; affected slice plans
cannot start until the specification and a revised decomposition are approved.
Clarifications that preserve those contracts retain the current status. Report
every status transition and why it occurred.

## Required Content

- Observed problem and evidence.
- Specification status.
- Complete outcome and affected capability.
- Explicit non-goals and binding constraints.
- Stable acceptance IDs (`AC-01`, `AC-02`, ...), each expressing one observable
  behaviour or verifiable system property.
- Genuine product, policy, compatibility, schema, and architecture decisions.
- Dependencies and external acceptance environments.
- Authorized complexity and its removal boundary.
- Agent-run behavioural verification and separate human or external acceptance.
- Every required new or modified table and view, including name, grain,
  columns, types, nullability, keys, relationships, and important semantics.

## Acceptance Cohesion

Group requirements by the outcome they prove. Do not hide independent
implementations behind aggregate wording such as "every enabled method" when
providers, lifecycle owners, failure modes, or acceptance procedures differ.
Assign stable IDs now; `write-slices` will give each ID one owning
slice.

Source-text, snapshot, or patch-shape assertions may protect structure. They do
not prove browser activation, DOM replacement, concurrency, retry, cancellation,
provider callbacks, current totals, or other runtime lifecycle behaviour.
State the lowest-cost reliable local seam that executes those requirements and
record real-provider or real-environment acceptance separately. Prefer one
representative scenario that proves several coupled conditions over a
cross-product matrix.

## Test Infrastructure Policy

Do not authorize a new custom test harness unless the user explicitly approves
that harness. A custom harness is new bespoke infrastructure that simulates or
drives a browser, runtime, provider, package, or application outside the
repository's existing test facilities. Approval of the specification, slices,
or implementation does not imply harness approval. Prefer existing tests,
small fixtures within them, focused commands, or explicit external acceptance.

## Authorized Complexity

For every proposed architectural layer, dependency, configuration option,
persistent object, public interface, compatibility behaviour, or supported
scenario, state:

- the demonstrated problem and acceptance ID that require it;
- why the platform's native owner or extension point cannot satisfy it;
- why an upgrade, upstream correction, or smaller compatibility change is
  insufficient; and
- how it can be removed or rolled back.

If none is required, say so. General lifecycle coordination, shared mutable
browser state, cross-provider state machines, retry or recovery frameworks,
whole-template vendor replacements, and local ownership of upstream package
behaviour are architectural layers. Broad acceptance criteria do not authorize
them implicitly.

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

After writing, state that the specification must be approved and decomposed by
`write-slices` before `build-branch-stack` can implement it.
