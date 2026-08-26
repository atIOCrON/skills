# Code Review Loop

Focused loop for staged-diff code review and material finding closure.

Delegate reviewer launch, staged-diff preparation, triage, closure,
implementation fixes, and verification to their bundled components.

## Delegated Components

Read the plan path now. Read each bundled component at the Pass Policy step
that first invokes it, not up front:

- `references/code-review.md`;
- `references/code-review-triage.md`;
- `references/code-review-closure.md`;
- `references/multi-review-pass-runner.md`;
- `references/staged-diff-scope.md`;
- `references/implementation-dispatch.md`;
- `references/verification-runner.md`.

## Inputs

Require:

- repository root;
- plan path;
- plan slug;
- intended implementation files or modules;
- reviewer preflight status for Claude Code and Cursor;
- passed initial verification, unless the route is explicitly starting at
  staged changes and verification will run first.

## Ledger

The cross-pass material concern ledger lives at:

```text
plans/<plan_slug>.reviews/code-review-triage-ledger.md
```

Triage creates and maintains it per
`references/orchestration-triage-ledger-protocol.md`.

## Pass Policy

Run at least two numbered code-review passes. Run more only while material risk
remains.

For each pass:

1. Use `staged-diff-scope` to stage and confirm only intended files.
2. Create `plans/<plan_slug>.reviews/code-review-pass<N>/`.
3. Read `references/code-review.md`, include its operational instructions in
   each reviewer prompt, then use `multi-review-pass-runner` with
   `references/code-review-loop-code-review-invocation.md`
   as the prompt envelope.
4. Run `references/code-review-triage.md` on all reviewer outputs;
   its accepted fix requests feed the next step.
5. Send accepted fixes through `implementation-dispatch`.
6. Rerun `verification-runner` after accepted fixes.
7. Restage intended files through `staged-diff-scope`.
8. Use `code-review-closure` only for rejected blockers/should-fix findings,
   unresolved contradictions, uncertain triage, or user-requested closure.
   Read `references/code-review-closure.md`, include its operational
   instructions in the closure prompt, then render
   `references/code-review-loop-closure-invocation.md`
   for closure prompts. `{triage_ledger_path}` renders to
   `plans/<plan_slug>.reviews/code-review-triage-ledger.md`.
9. Resolve `recurring-escalation` ledger entries with explicit user decisions
   before starting the next pass.

## Completion Condition

Stop as `Ready for git handoff` only when:

- at least two code-review passes ran;
- plan verification and focused checks pass;
- no unresolved blocker, should-fix, contradiction, or accepted material fix
  remains;
- no material ledger entry is in a non-terminal status (per
  `references/orchestration-triage-ledger-protocol.md`);
- required closure is complete.

Nits are advisory unless triage finds them material (see
`references/orchestration-definitions.md`).

## Sub-Passes

Use a sub-pass only when applying or checking fixes reveals a new in-scope issue.
Sub-pass finding IDs use the format defined in
`references/orchestration-finding-ids.md`. Triage,
fix, verify, restage, and ledger-update like normal findings. Stop after two
sub-pass iterations in one review pass.

## Output

Report:

- pass count and one-line outcome per pass;
- accepted fixes and verification status;
- rejected/deferred findings with evidence;
- reviewer artifact paths, including failures;
- ledger path and terminal-status counts;
- unresolved blocker or `Ready for git handoff`;
- skill feedback.
