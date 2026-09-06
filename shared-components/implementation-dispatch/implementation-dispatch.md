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

## Initial Implementation

For initial implementation:

1. Read `references/plan-implement.md` and include its operational instructions
   in the worker prompt; do not send the worker a path to load.
2. Render
   `references/implementation-dispatch-plan-invocation.md`.
3. Assign owned files or modules as a newline bullet list.
4. Send the prompt to a fresh native implementation sub-agent of the host.
5. Record its session reference.

## Fix Dispatch

For verification or code-review fixes:

1. Resume the original implementation sub-agent.
2. Stop if it cannot be resumed; do not silently change implementers.
3. Read `references/plan-implement.md`, include its operational instructions in
   the worker prompt, then render
   `references/implementation-dispatch-fix-request.md`.
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
- host provider and native transport;
- worker/session reference;
- owned files or modules;
- requested changes;
- artifact paths supplied;
- expected verification command or focused check.
