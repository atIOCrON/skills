# Implementation Dispatch

Send implementation and accepted-fix requests to a worker using the bundled
instructions in `references/plan-implement.md`.

## Inputs

Require:

- repository root;
- host provider: `codex`, `claude`, or `cursor`;
- plan path;
- dispatch type: `initial-implementation`, `verification-fix`, or
  `code-review-fix`;
- owned files or modules;
- fix requests or verification failures for non-initial dispatches;
- relevant artifact paths.
- reviewed or failed commit SHA for fix dispatches.

For every dispatch, include the contents of
`references/orchestration-plans-layout.md` in the worker prompt and assign
execution and evidence subdirectories within its ownership scope.

## Initial Implementation

For initial implementation:

1. Read `references/plan-implement.md` and include its operational instructions
   in the worker prompt; do not send the worker a path to load.
2. Render
   `references/implementation-dispatch-plan-invocation.md`.
3. Assign owned files or modules as a newline bullet list.
4. For a complex or cross-cutting change, require the worker to create the
   implementation analysis defined in `references/plan-implement.md` before
   editing. Pass its artifact path to later fix requests.
5. Send the prompt to a fresh native implementation sub-agent of the host.
6. Record its session reference.

## Fix Dispatch

For verification or code-review fixes:

1. Resume the original implementation sub-agent.
2. If it cannot be resumed, record the lost session and dispatch a fresh worker
   with the plan, design checkpoint, current SHA, accepted findings, ownership,
   and evidence. Do not rely on missing conversation state.
3. Read `references/plan-implement.md`, include its operational instructions in
   the worker prompt, then render
   `references/implementation-dispatch-fix-request.md`.
4. Include only accepted fixes or concrete verification failures. For each code
   review fix, include its family ID, `reproduced` or `binding-proof` class,
   pinned SHA, supported path, and evidence. Batch accepted findings for the
   same worker into one request.
5. Include relevant artifact paths, not long copied transcripts unless needed.
6. Preserve owned-file boundaries.
7. Require edits on the current plan branch; the orchestrator creates a new
   commit after the worker returns.

## Guardrails

- Do not send rejected findings as work.
- Before editing for a code-review finding, independently confirm its pinned
  SHA and either reproduce it through the cited supported path with existing
  facilities or confirm its binding proof. Return an unconfirmed finding to
  triage without changing production code or tests.
- Do not request speculative refactors, compatibility shims, fallback defaults,
  or unrelated cleanup.
- If a fix needs files outside ownership, return the exact paths and reason. The
  runner may expand ownership or split the fix within the approved outcome.

## Output

Report:

- dispatch type;
- host provider and native transport;
- worker/session reference;
- owned files or modules;
- requested changes;
- artifact paths supplied;
- expected verification command or focused check.
