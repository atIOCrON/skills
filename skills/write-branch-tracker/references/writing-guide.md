# Branch Tracker Writing Guide

## Required format

Use these columns in this exact order for CSV and Google Sheets:

1. `Sort`
2. `Stack`
3. `Target Branch`
4. `Source Branch`
5. `Status`
6. `To Do`
7. `Plan`
8. `Operator problem`
9. `Solution`
10. `Suggested operator test path`
11. `Pass condition`
12. `Note`
13. `Type(s)`
14. `Change surface(s)`
15. `Package(s)`

The JSON passed to `scripts/write_branch_tracker.py` must be an array of objects
with these exact keys. `Sort` and `Stack` are positive JSON integers; all other
values are strings without NUL or embedded newlines. Draft `To Do` and `Note`
must be empty. `Plan` and `Package(s)` may be empty when absent; other text is
required. Separate multiple types, surfaces, or packages with `; ` and remove
duplicates. Keep the primary type first.

The CSV writer emits UTF-8 BOM, quoted fields, CRLF records, and a final record
terminator. Use the user's timezone (default `Australia/Sydney`) for the name:

```text
YYYY-MM-DDTHH-MM-SS+ZZZZ-branch-tracker.csv
```

## Research each row

Use multiple forms of evidence where available:

- the exact branch ref, branch-only commits, and diff against its intended parent;
- the plan that explicitly declares the branch and its parent or stack position;
- implementation and review artefacts, especially accepted corrections or deferred checks;
- tests, fixtures, configuration, profile/template manifests, and operator-facing routes changed by the branch;
- related requested branches that provide foundations, supersede expected behavior, or must be deployed together.

Use Git inspection commands that do not alter the working tree, such as `git rev-parse`, `git log`, `git diff`, `git show`, and `git merge-base`. Do not infer a row from its branch name alone. A diff against `master` is not branch-specific when the branch contains a parent stack.

When plan and implementation differ, describe the implementation that exists on the named branch. Retain a plan requirement only if the implementation, accepted review outcome, or external operating contract still supports it. Do not turn an aspiration or unavailable receiver check into a pass claim.

## Column guidance

### Sort and Stack

`Sort` is unique and consecutive across the generated tracker, starting at 1.
Group rows by stack, with dependencies before descendants. `Stack` is an integer
starting at 1, shared by branches in the same dependency group. One stack uses
1 throughout. Number independent stacks by first appearance in the request.
Do not infer dependencies merely from input order or a common base.

### Target Branch and Source Branch

`Target Branch` is the evidenced parent/comparison branch, not its SHA or the
final integration destination. Use it for the branch-only diff. For an
independent branch, use its evidenced base. Reconcile manifest, plan, review,
and Git evidence; ask if the parent remains ambiguous.

Copy the supplied branch name exactly into `Source Branch`.

### Status and Plan

Use the current executable slice plan's stage under `plans/slices/`, not the
parent specification's approval state, build progress labels, CI success, or
the Sheet's old value:

| Current stage | Status |
| --- | --- |
| `draft` | Draft |
| `backlog` | Backlog |
| `to_do` | To Do |
| `in_progress` | In Progress |
| `review` | Review |
| `fulfilled` | Fulfilled |
| `superseded` | Superseded |

`Deprecated` requires explicit branch retirement evidence; it is not a plan
stage. Use `Superseded` for a plan replaced by identified plans. Branch age,
absence, or inactivity does not establish retirement or supersession.
Ask when status evidence is missing or contradictory; do not invent another value.

Follow the repository's plans-layout contract used by `build-branch-stack`.
`Review` allows pending human/external acceptance, release-candidate checks,
review-cap disposition, restacks, or current-tip evidence. `Fulfilled` requires
confirmed merge and every required final acceptance check passed or its
limitation explicitly accepted. Report a stale `fulfilled` stage when these gates
are demonstrably unmet; do not edit plans or claim completion from code alone.

`Plan` is the current path relative to the plans repository, for example
`plans/slices/review/rival_configdebug_setup/rival_configdebug_setup.md`.
Resolve moved plans by slice slug and explicit branch declaration, including
legacy locations without moving files. Reconcile legacy `done` to `Fulfilled`
only with confirmed merge and acceptance evidence; report discrepancies.
Leave blank and report the limitation if no matching plan exists but other
evidence supports status.

### To Do and Note

Leave both empty for new rows. Preserve existing operator values when updating
a Sheet, including any formulas, links, or formatting in those cells.

### Type(s)

Classify the purpose using only these values:

| Type | Meaning |
| --- | --- |
| Feature | Adds or intentionally changes a capability, including project customisation. |
| Fix | Corrects behaviour that violates an established expectation or contract. |
| Operations | Changes how the system is deployed, maintained, recovered, or operated. |
| Tests | Adds or changes verification. |
| Documentation | Changes explanatory or instructional material. |
| Housekeeping | Refactoring, cleanup, or removal without intended functional change. |

Assign one primary type; add another only for substantial distinct work.
Incidental tests, documentation, or cleanup do not make every branch multi-type.
Configuration is a surface: enabling a capability is Feature, correcting a bad
setting is Fix, and changing environment/deployment settings is Operations.
Package ownership does not determine purpose.

### Change surface(s)

Classify the changed implementation locations using only these values:

| Surface | Includes |
| --- | --- |
| First-party code | Project modules, plugins, observers, services, and application code. |
| Composer patch | Composer-managed dependency patches. |
| Theme | Templates, layouts, styles, and frontend assets. |
| Configuration | Dependency manifests/locks, settings, DI configuration, and environment profiles. |
| Data/schema | Schema declarations, migrations, seed data, and data corrections. |
| Tests | Test code and fixtures. |
| Documentation | Plans, guides, and operating instructions. |
| Tooling | Scripts, CI, deployment automation, and developer utilities. |

Include each applicable surface from the branch-only diff. Surfaces may overlap:
a module schema correction is `First-party code; Data/schema`; a dependency
patch with regression tests is `Composer patch; Tests`. A first-party plugin is
First-party code, not a separate surface.

### Package(s)

Use exact owning package names from `composer.json` or locked dependency
metadata. For a first-party module without a Composer identity, use its exact
registered Magento module name. Include a dependency whose version/constraint
changes or whose code is patched. Exclude unchanged consumers, inherited
ancestor changes, and untouched transitive dependencies. Leave empty when no
package is affected. Do not guess names from directory slugs.

### Operator problem

In one or two compact sentences, explain the concrete failure, risk, inconsistency, or operational gap that motivated the branch. Describe its observable consequence and affected workflow. Avoid code-level causes unless they are necessary to understand the operator impact.

Good characteristics:

- understandable by a release owner, store operator, or tester;
- specific enough to distinguish the branch from neighboring work;
- neutral and factual, without claiming the fix is already proven in production.

### Solution

In one or two compact sentences, explain the behavior the branch provides and the important boundary it preserves. Mention a prerequisite, configuration choice, or fallback only when it materially affects deployment or validation.

Prefer outcomes over file names and class-level mechanics. Technical precision is appropriate for an external contract such as a schema URL, event field, identifier format, stock state, timestamp basis, or export column.

### Suggested operator test path

Give an executable staging path in prose:

- say where to start, such as storefront, Admin, a dedicated analytics destination, or an isolated export target;
- name the representative actions and fixtures supported by evidence;
- cover the smallest meaningful scenario matrix, including warm-cache, retry, store, state-transition, or partial-operation cases only when relevant;
- use safe test accounts, sandbox payments, dedicated receivers, disposable content, and isolated export destinations where applicable;
- assign payload inspection, cache internals, failure injection, patch application, or source/config verification to a developer when an operator cannot observe it directly;
- explicitly say when a foundation has no new operator screen.

Do not suggest destructive fault injection in shared staging. Do not imply that visiting a page proves an internal security, timestamp, patch-order, or delivery property.

### Pass condition

State observable, falsifiable results. Include exact fixture values only when the evidence supplies them. Cover preservation properties such as identities, quantities, totals, event counts, links, cached behavior, fallbacks, or unrelated output when those are central to the regression risk.

Distinguish these levels of proof:

- operator-visible behavior;
- payload, source, configuration, or deployment verification by a developer;
- third-party receiver ingestion or reporting;
- unavailable checks that must remain pending.

If another requested branch supersedes part of the expectation, state that relationship in the affected row. A successful deployment, HTTP request, page load, or order alone is not proof of properties it cannot reveal.

## Cross-row quality check

Before writing the file, confirm that:

- each row describes only its branch's contribution rather than its entire ancestor stack;
- foundation rows and consumer rows have distinct problems, tests, and pass conditions;
- rows agree on shared identity, pricing, availability, ETA, or event semantics;
- prerequisites and configuration activation are not mistaken for code deployment;
- unresolved or invalid context uses the evidenced fallback and never borrows another item, store, session, or branch's data;
- the language is concise enough to scan in a spreadsheet but complete enough to run a staging check.
