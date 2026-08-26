---
name: plan-review-loop
description: Focused plan-review loop skill. Use to run the reviewed-plan phase with three Claude/Codex/Cursor passes, plan-review triage, plan edits, closure, and reviewed-plan handoff while delegating reviewer launch mechanics to multi-review-pass-runner. Not for a single review pass; use plan-review for that.
metadata:
  layer: runner
---

# Plan Review Loop

Focused loop for turning a plan into a reviewed plan.

## Delegated Skills

Read the plan path now. Read each delegated skill's SKILL.md at the step in
Pass Policy that first invokes it, not up front:

- `.agents/skills/plan-review/SKILL.md`;
- `.agents/skills/plan-review-triage/SKILL.md`;
- `.agents/skills/plan-review-closure/SKILL.md`;
- `.agents/skills/multi-review-pass-runner/SKILL.md`.

## Inputs

Require:

- repository root;
- plan path under `plans/`;
- plan slug;
- reviewer preflight status for Claude Code and Cursor.

Stop if the plan lacks deterministic verification.

## Pass Policy

Run exactly three plan-review passes unless blocked or the user explicitly
changes the pass count before the phase starts.

For each pass:

1. Create `plans/<plan_slug>.reviews/plan-review-pass<N>/`.
2. Use `multi-review-pass-runner` with
   `.agents/skills/plan-review-loop/references/plan_review_skill_invocation.md`
   as the prompt envelope.
3. Run `.agents/skills/plan-review-triage/SKILL.md` on all reviewer outputs.
4. Apply accepted plan edits through the triage skill's allowed plan-only
   workflow.
5. Send closure to each reviewer that raised findings using
   `.agents/skills/plan-review-loop/references/plan_review_closure_skill_invocation.md`.
6. Start the next pass only after all current-pass findings are closed,
   rejected with evidence, or escalated to and resolved by the user.

Open questions from reviewers count as unresolved findings until answered,
rejected with evidence, or converted into a concrete plan edit.

## Closure Rule

Closure is non-skippable for any reviewer that raised findings in the current
pass.

## Output

Report:

- plan path;
- pass count;
- one-line outcome per pass;
- accepted plan edits;
- rejected/deferred findings with evidence;
- reviewer artifact paths, including failures;
- unresolved blocker or `Ready for implementation`;
- skill feedback.
