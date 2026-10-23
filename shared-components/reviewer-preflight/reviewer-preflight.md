# Reviewer Preflight

Preflight each non-host CLI (codex/claude/cursor) with repository root:

```bash
"$orchestration_skill_root/scripts/run_reviewer_preflight.sh" <codex|claude|cursor> "{repo_root}"
```

Require CLI availability/new resumable session, first normalized last-nonempty line
exactly REVIEWER_SMOKE_OK, and same-session read-only git status/diff/show plus
synthetic git apply --check without worktree mutation; resumed line must be exactly
`ORCHESTRATE_SESSION_SMOKE <HEAD_SHA>` with actual HEAD. Native host uses runtime.
Stop without retry on auth/permission/missing command/unresumable session.
Report reviewer/command, smoke ID, first/resumed token and read-only command results,
pass/fail and blocker.
