# Code Review Loop

Focused loop for staged-diff code review and material finding closure.

Delegate reviewer launch, staged-diff preparation, triage, closure,
implementation fixes, and verification to their bundled components.

## Delegated Components

Read the plan path now. Read each bundled component at the Pass Policy step
that first invokes it, not up front:

- `references/code-review.md`;
- `references/code-review-pack.md`;
- `references/code-review-triage.md`;
- `references/code-review-closure.md`;
- `references/multi-review-pass-runner.md`;
- `references/staged-diff-scope.md`;
- `references/implementation-dispatch.md`;
- `references/verification-runner.md`.

## Inputs

Require:

- repository root;
- host provider and provider-to-transport mapping;
- plan path;
- plan slug;
- intended implementation files or modules;
- neutral review-pack path;
- preflight status for both external CLI reviewers;
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

Run numbered fresh code-review passes. A pass is a clean-room three-provider
discovery review; targeted closure rounds do not count as passes. One clean
fresh pass is sufficient. After any accepted material fix, complete targeted
closure, then run another fresh pass. Here, clean means triage accepted no
material finding and left no contradiction unresolved; advisory nits do not
prevent a clean pass.

For each pass:

1. Use `staged-diff-scope` to stage and confirm only intended files.
2. Refresh the staged-state and verification portions of `code-review-pack`.
   Never add review history, triage, or fix narratives.
3. Create `plans/<plan_slug>.reviews/code-review-pass<N>/`.
4. Read `references/code-review.md`, include its operational instructions in
   each reviewer prompt, then use `multi-review-pass-runner` with
   `references/code-review-loop-code-review-invocation.md`
   as the prompt envelope. Start all three reviewers fresh and in parallel.
   Each must complete an exhaustive pass after finding a blocker.
5. Run `references/code-review-triage.md` once on all reviewer outputs. Batch
   all accepted blockers and should-fix findings for the same implementer into
   one fix request. Do not routinely fix or close nits.
6. If fixes were accepted, resume the original implementation worker once with
   the batch, then run `verification-runner`, restage through
   `staged-diff-scope`, and refresh the neutral review pack.
7. Resume every reviewer who originated an accepted material finding. Send one
   closure request per reviewer containing all of that reviewer's accepted
   finding IDs, applied changes, verification evidence, and artifact paths.
   Read `references/code-review-closure.md`, include its operational
   instructions in the closure prompt, then render
   `references/code-review-loop-closure-invocation.md`
   for closure prompts. `{triage_ledger_path}` renders to
   `plans/<plan_slug>.reviews/code-review-triage-ledger.md`.
   Do not send one reviewer another reviewer's findings or conclusions.
8. If targeted closure leaves a material finding open, batch the remaining
   fixes to the same implementer, verify once, and resume only the affected
   reviewers. Repeat targeted closure until those findings close or require a
   user decision. Preserve each closure round as a separate artifact and apply
   its proposed ledger transitions through the orchestrator.
9. Use targeted closure for a rejected material finding only when triage is
   uncertain, evidence conflicts, or the user requests it.
10. Resolve `recurring-escalation` ledger entries with explicit user decisions
    before starting the next fresh pass.

## Completion Condition

Stop as `Ready for git handoff` only when:

- at least one fresh code-review pass ran;
- the newest fresh pass reported no accepted material findings;
- plan verification and focused checks pass;
- no unresolved blocker, should-fix, contradiction, or accepted material fix
  remains;
- no material ledger entry is in a non-terminal status (per
  `references/orchestration-triage-ledger-protocol.md`);
- required closure is complete.

Nits are advisory unless triage finds them material (see
`references/orchestration-definitions.md`). If a fix creates an independent
concern, leave its discovery to the next fresh pass; closure checks only the
original finding and its surrounding invariant.

## Output

Report:

- fresh pass count and one-line outcome per pass;
- targeted closure rounds and originating reviewers;
- accepted fixes and verification status;
- rejected/deferred findings with evidence;
- reviewer artifact paths, including failures;
- ledger path and terminal-status counts;
- unresolved blocker or `Ready for git handoff`;
- skill feedback.
