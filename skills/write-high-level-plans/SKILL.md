---
name: write-high-level-plans
description: Write concise, outcome-focused implementation plans with foundational database schemas, while leaving detailed technical design to the implementing agent.
disable-model-invocation: true
metadata:
  layer: capability
---

# Write High-Level Plans

Resolve all `plans/...` paths against the user's primary local checkout of the
target repository, or another local directory they explicitly designate. Do
not use a separate agent worktree as the plan root merely because it is the
current working directory. Create and update the plan in the selected local
directory, and report its absolute path.

Create new plans at `plans/backlog/<plan_name>/<plan_name>.md`. The feature
directory and plan file share the same name. For an update, find the existing
plan under `backlog`, `to_do`, `in_progress`, `review`, or `done` and edit it in
place. Check the legacy `plans/<plan_name>.md` path before creating a new plan;
if found, update it in place and report its legacy layout. Never make a
duplicate or change an existing plan's stage. If an update changes an approved
plan, report that its approval and review need refreshing.

- Use a lowercase `snake_case` plan name: words separated by single underscores, using only `a-z`, `0-9`, and `_`, with no leading or trailing underscore. Do not use hyphens or spaces.
- Keep the plan name to a maximum of 40 characters, including underscores but excluding the `.md` extension and directory path. Choose a concise, descriptive name and check its length before saving; for example, `supplier_stock_sync`.
- Inspect relevant code, documentation, and existing conventions first.

## Required Content

- State the observed problem and its evidence.
- State the minimum outcome that solves it.
- Define the affected capability and explicit non-goals. Do not authorize unspecified generalization, configuration, extensibility, scale preparation, new compatibility support, or adjacent cleanup.
- List genuine key decisions and dependencies.
- State any authorized complexity: a new architectural layer, dependency, configuration option, persistent object, public interface, compatibility behavior, or supported scenario. Name what requires it. If none is required, say so.
- Express acceptance conditions as observable behaviour or verifiable system properties: what users or integrations experience, what must be true of the resulting data or state, and what must never happen.
- Specify every required new or modified table and view. For each new database object, define its name, grain, columns, data types, nullability, keys, relationships, and important field semantics.

## Planning Rules

- Authorize only the least-complex change that can meet the acceptance conditions and preserve affected binding contracts. Do not authorize work for hypothetical future needs.
- Do not disguise an implementation mechanism as an outcome. Waits, polling, interception or replay, timeout values, API choice or call sequence, parsing technique, storage technique, and exact control flow belong to the implementing agent unless the user explicitly selected them or they follow from a non-negotiable invariant such as policy, a schema or data contract, or platform correctness. Existing code and conventions are context, not binding constraints by themselves; a rework plan may exist specifically to change them.
- Use a substitution test: if materially different designs could satisfy the same requirement, state the result they must share rather than choosing one design. When a mechanism really is mandatory, identify the source of that constraint so it is not mistaken for an author preference.
- Treat linked APIs, documentation, and existing implementations as references unless the user explicitly requires their use or a non-negotiable invariant leaves no alternative. A citation or current implementation alone does not make a procedure mandatory.
- Put only resolved, consequential forks under key decisions, such as product behaviour, policy, scope, compatibility boundaries, or foundational data contracts. Do not promote incidental mechanics or an uncertain design preference into a decision; leave unresolved implementation choices to the implementing agent.
- Define scope boundaries as walls around the deliverable, not locks on its design. Any design may be used if it meets the acceptance conditions without adding unplanned deliverables or unauthorized complexity.
- Write acceptance criteria in user-visible or externally verifiable terms rather than as algorithms or prescribed procedures. For example, require that a user action is not delayed by optional integration work, without prescribing a particular timer or replay sequence.
- Distinguish schema requirements and other binding constraints from implementation suggestions.
- Capture every actual user requirement in clear, contextualized plan language, preserving its intended meaning, scope, constraints, and acceptance conditions. Treat audits, reviews, and defect reports as evidence of problems and required properties; translate their procedural recommendations into outcomes unless the user explicitly adopts a procedure as a constraint.
- Leave processing design, exact file changes, line numbers, and implementation mechanics to the implementing agent.
- Keep the plan direct, succinct, high level, and internally consistent.
