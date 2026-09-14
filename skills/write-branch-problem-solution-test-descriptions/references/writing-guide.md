# Branch Description CSV Writing Guide

## Required format

Use these five columns in this exact order:

1. `Branch`
2. `Operator problem`
3. `Solution`
4. `Suggested operator test path`
5. `Pass condition`

The JSON passed to `scripts/write_branch_descriptions.py` must be an array of objects with those exact keys. Every value must be a non-empty string without embedded newlines. The writer emits an Excel-friendly UTF-8 BOM, quotes every field, uses CRLF record endings, and names the file:

```text
YYYY-MM-DDTHH-MM-SS+ZZZZ-branch-problem-solution-test-descriptions.csv
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

### Branch

Copy the supplied branch name exactly.

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
