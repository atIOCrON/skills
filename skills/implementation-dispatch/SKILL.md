---
name: implementation-dispatch
description: Implementation-worker dispatch skill. Use to send approved plans, verification failures, and accepted review fixes to a Codex implementation worker while preserving owned-file boundaries and existing plan-implement behavior.
metadata:
  layer: capability
---

# Implementation Dispatch

Send implementation and accepted-fix requests to a worker that follows
`.agents/skills/plan-implement/SKILL.md`.

## Inputs

Require:

- repository root;
- plan path;
- dispatch type: `initial-implementation`, `verification-fix`, or
  `code-review-fix`;
- owned files or modules;
- fix requests or verification failures for non-initial dispatches;
- relevant artifact paths.

## Initial Implementation

For initial implementation:

1. Read `.agents/skills/plan-implement/SKILL.md`.
2. Render
   `.agents/skills/implementation-dispatch/references/plan_implement_skill_invocation.md`.
3. Assign owned files or modules as a newline bullet list.
4. Send the prompt to a fresh Codex worker.
5. Record the worker id or thread reference when available.

## Fix Dispatch

For verification or code-review fixes:

1. Prefer reusing the original implementation worker when available.
2. Otherwise start a fresh worker.
3. Render
   `.agents/skills/implementation-dispatch/references/plan_implement_fix_request.md`.
4. Include only accepted fixes or concrete verification failures.
5. Include relevant artifact paths, not long copied transcripts unless needed.
6. Preserve owned-file boundaries.

## Guardrails

- Do not send rejected findings as work.
- Do not request speculative refactors, compatibility shims, fallback defaults,
  or unrelated cleanup.
- If a fix request would require changing files outside ownership, stop and ask
  the runner to expand ownership or split the fix.

## Output

Report:

- dispatch type;
- worker/session reference when available;
- owned files or modules;
- requested changes;
- artifact paths supplied;
- expected verification command or focused check.
