---
name: plan-implement
description: Implement an approved plans/ file within an assigned file/module ownership scope. Use when dispatched with an approved plan and owned files to edit. Updates all in-repo readers of changed contracts. Does not create plans, stage, or commit.
metadata:
  layer: capability
---

# Plan Implement

Implement one approved plan from `plans/` within the assigned file or module
ownership scope. The plan defines approved intent and scope; current repo docs,
code contracts, and gold-standard data-engineering practice govern
implementation details. If no plan path or ownership scope is provided, ask.

## Before Editing

1. Read the plan end to end, including out-of-scope notes.
2. Open every cited `file:line`. If a line number is stale, search the current
   file for the referenced symbol, behavior, or nearby text and use the current
   location. Stop only when the claim cannot be verified in the current codebase,
   contradicts current evidence, or would materially change the approved scope.
3. Read the docs AGENTS.md labels as code standards and logging standards, and
   any other referenced or relevant `docs/*.md`.
4. Identify the files to create, change, or delete within the assigned ownership scope.

Use `AGENTS.md` to choose relevant docs.

## Implementation Rules

- Implement only the approved plan's intent within the assigned ownership
  scope.
- Small implementation-detail deviations are allowed when they preserve the
  approved outcome, stay in scope, improve correctness, or better match current
  repo patterns. Report the divergence in the handoff.
- If plan details conflict with current repo docs, code contracts, or
  gold-standard data-engineering practice, prefer the stronger engineering
  standard and report the divergence.
- If the ownership scope is insufficient, stop and report the needed scope
  expansion instead of editing outside it.
- The workspace may contain edits from the user or other agents. Do not revert,
  overwrite, or clean up work you did not make.
- Update every in-repo reader of a changed schema, CLI flag, view, error shape,
  config key, or exported field within your scope.
- No backward-compatibility shims, deprecation paths, fallback defaults,
  speculative features, or unrelated cleanup.
- Use the repo primitives named by AGENTS.md as documented in the docs/ files
  it indexes.
- Preserve idempotency, raw/Bronze immutability, deterministic keys, lineage, batch boundaries, observability, and explicit empty/duplicate/failure handling.
- Do not stage files, commit, branch, push, or open a pull request.

## Verification

Run the verification named by the plan when practical for the owned surface.
Report failures honestly; if verification is impossible here, say why.

## Output

```markdown
## Implemented
- <file> - <change>

## In-repo Readers Updated
- <file> - <why, or None>

## Verification
- <command/check> - <pass/fail/evidence>

## Changed Files
- <file>

## Blockers
- <blocker, or None>
```

End with exactly one:

- `Ready for orchestrator integration`
- `Partial - blocker encountered`
