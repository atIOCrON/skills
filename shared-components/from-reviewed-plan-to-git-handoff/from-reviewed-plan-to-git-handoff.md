# From Reviewed Plan To Git Handoff

Implement a reviewed plan and run staged-diff code review until the work is
ready for git handoff.

## Inputs

Require:

- reviewed or approved `plans/<slug>.md`;
- implementation ownership scope, or enough plan context to derive one.

Ask only if the plan path or implementation ownership scope is missing.

## Route

Ledger, material, and artefact terms are defined in
references/orchestration-conventions.md.

1. Load `AGENTS.md`, the plan, and relevant docs named by `AGENTS.md`.
2. Read `references/orchestration-runtime.md` and select the host mapping.
3. Read and follow `references/implementation-dispatch.md` for initial
   implementation.
4. Read and follow `references/verification-runner.md`.
5. Read and follow `references/staged-diff-scope.md`.
6. Read and follow `references/reviewer-preflight.md` for both non-host
   providers.
7. Read and follow `references/code-review-loop.md`.
8. Read and follow `references/orchestration-final-handoff.md` for git handoff.

## Stop Conditions

- Ownership scope is insufficient.
- Intended staged-diff scope is unclear or includes unrelated files.
- Verification remains blocked after allowed repair attempts.
- A required native operation or external reviewer preflight fails.
- Code review has unresolved material ledger entries, contradictions, accepted
  fixes, or recurring escalations.

## Output

Report:

- plan path;
- changed files;
- verification status;
- code-review pass outcomes;
- triage ledger path and terminal-status counts;
- blocker or `Ready for git handoff`;
- next bundled component: `references/git-branch-commit-push.md`.
