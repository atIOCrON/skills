---
name: code-review-loop
description: Focused staged-diff code-review loop skill. Use after implementation or for already staged changes to run at least two Claude/Codex/Cursor code-review passes, triage material findings, dispatch accepted fixes, verify, close findings, update the ledger, and stop only when ready for git handoff. Not for a single review pass; use code-review for that.
metadata:
  layer: runner
---

# Code Review Loop

Focused loop for staged-diff code review and material finding closure.

Delegate reviewer launch, staged-diff preparation, triage, closure,
implementation fixes, and verification to their focused skills.

## Delegated Skills

Read the plan path now. Read each delegated skill's SKILL.md at the step in
Pass Policy that first invokes it, not up front:

- `.agents/skills/code-review/SKILL.md`;
- `.agents/skills/code-review-triage/SKILL.md`;
- `.agents/skills/code-review-closure/SKILL.md`;
- `.agents/skills/multi-review-pass-runner/SKILL.md`;
- `.agents/skills/staged-diff-scope/SKILL.md`;
- `.agents/skills/implementation-dispatch/SKILL.md`;
- `.agents/skills/verification-runner/SKILL.md`.

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
`.agents/skills/orchestration-conventions/references/triage_ledger_protocol.md`.

## Pass Policy

Run at least two numbered code-review passes. Run more only while material risk
remains.

For each pass:

1. Use `staged-diff-scope` to stage and confirm only intended files.
2. Create `plans/<plan_slug>.reviews/code-review-pass<N>/`.
3. Use `multi-review-pass-runner` with
   `.agents/skills/code-review-loop/references/code_review_skill_invocation.md`
   as the prompt envelope.
4. Run `.agents/skills/code-review-triage/SKILL.md` on all reviewer outputs;
   its accepted fix requests feed the next step.
5. Send accepted fixes through `implementation-dispatch`.
6. Rerun `verification-runner` after accepted fixes.
7. Restage intended files through `staged-diff-scope`.
8. Use `code-review-closure` only for rejected blockers/should-fix findings,
   unresolved contradictions, uncertain triage, or user-requested closure.
   Render
   `.agents/skills/code-review-loop/references/code_review_closure_skill_invocation.md`
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
  `.agents/skills/orchestration-conventions/references/triage_ledger_protocol.md`);
- required closure is complete.

Nits are advisory unless triage finds them material (see
`.agents/skills/orchestration-conventions/references/definitions.md`).

## Sub-Passes

Use a sub-pass only when applying or checking fixes reveals a new in-scope issue.
Sub-pass finding IDs use the format defined in
`.agents/skills/orchestration-conventions/references/finding_ids.md`. Triage,
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
