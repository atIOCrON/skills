# Reviewer Preflight

Verify one external reviewer CLI and same-session resume.

## Inputs

Require:

- reviewer: `codex`, `claude`, or `cursor`;
- repository root.

Run this only for CLI reviewers; the host reviewer uses the native runtime
contract.

## Command

Run:

```bash
"$orchestration_skill_root/scripts/run_reviewer_preflight.sh" <codex|claude|cursor> "{repo_root}"
```

## Pass Criteria

Pass only when:

- the provider CLI resolves and can create a session;
- the first smoke prompt's normalized token line returns exactly
  `REVIEWER_SMOKE_OK`;
- the resumed session's normalized token line returns exactly
  `ORCHESTRATE_SESSION_SMOKE`.

Compare the last non-empty output line to the token.

## Failure Rules

Stop without retrying for: auth/login required, permission denied, missing
command, or a non-resumable session.

The smoke token convention is defined in references/orchestration-conventions.md.

## Output

Report:

- reviewer verified;
- command availability;
- smoke session/chat id;
- first prompt status;
- resume status;
- pass/fail;
- blocker reason when failed.
