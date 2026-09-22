# Reviewer Preflight

Verify one external reviewer CLI, same-session resume, and read-only repository
commands.

## Inputs

Require:

- reviewer: `codex`, `claude`, or `cursor`;
- repository root.

Run this only for CLI reviewers; the host reviewer uses the native runtime
contract.

Reuse a successful preflight for the same repository, provider executable and
version, selected model, authentication context and host session. Record that
identity and the evidence path. Rerun only when an identity changes, a reviewer
fails to launch or resume, or the cached evidence is missing or invalid.

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
- the resumed session can run `git status`, commit-to-commit `git diff`, `git show`, and a
  synthetic `git apply --check` without changing the worktree;
- the resumed session's normalized token line returns
  `ORCHESTRATE_SESSION_SMOKE <HEAD_SHA>` with the actual repository HEAD.

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
- resume and read-only command status;
- identity key and whether the result was executed or reused;
- pass/fail;
- blocker reason when failed.
