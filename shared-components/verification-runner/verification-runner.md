# Verification Runner

Verification execution and bounded repair handoff for orchestration workflows.

## Inputs

Require:

- repository root;
- plan path;
- verification commands from the plan;
- touched files or modules;
- implementation worker reference when available;
- verification point label, such as `post-implementation` or
  `post-code-review-fix`.

Stop if the plan lacks deterministic verification commands.

## Workflow

1. Read the plan verification section.
2. Run every required plan verification command from the repository root.
3. Add focused checks for touched surfaces when risk justifies them.
4. Save commands, exit status, and concise results under
   `plans/<plan_slug>.evidence/` and update its index; follow
   `references/orchestration-plans-layout.md` for retention.
5. If verification passes, return `verification-passed`.
6. If verification fails, classify the failure and send a concrete fix request
   through `implementation-dispatch`.
7. Rerun verification after the worker applies a fix.
8. Stop after two failed fix attempts for the same verification point.

## Failure Fix Requests

Each verification fix request must include:

- failing command;
- failure summary;
- relevant output excerpt;
- expected behavior;
- owned file or module boundary;
- command to rerun.

## Output

Report:

- verification point label;
- commands run;
- pass/fail status per command;
- focused checks run;
- fix attempts used;
- blocker reason if stopped;
- final status: `verification-passed` or `verification-blocked`.
