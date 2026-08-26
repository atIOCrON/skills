# Orchestration Final Handoff

Final reporting component for orchestration workflows.

## Inputs

Require:

- route and final state;
- plan path;
- files changed or staged file list;
- verification summary;
- review pass summaries;
- reviewer artifact paths;
- ledger path and status counts when code review ran;
- rejected, deferred, or user-decided findings;
- skill feedback entries.

## Output For Reviewed Plan

Include:

- plan path and whether it was created or loaded;
- plan-review pass count and one-line outcome per pass;
- rejected/deferred findings with evidence or recorded reason;
- reviewer artifact paths, including failures;
- confirmation all required plan-review passes closed, or blocker;
- `## Skill Feedback For User Review` with entries or `- None`;
- final state: blocker or `Ready for implementation`;
- next recommended bundled component:
  `references/from-reviewed-plan-to-git-handoff.md`.

## Output For Git Handoff

Include:

- plan path and files changed;
- verification commands and status;
- code-review pass count and one-line outcome per pass;
- rejected/deferred findings with evidence or recorded reason;
- reviewer artifact paths, including failures;
- triage ledger path and terminal-status counts;
- confirmation no non-terminal ledger entries remain before saying
  `Ready for git handoff`;
- `## Skill Feedback For User Review` with entries or `- None`;
- final state: blocker, `Ready for code review`, or `Ready for git handoff`;
- next recommended bundled component:
  `references/git-branch-commit-push.md` when ready for git handoff.

Keep the handoff concise and cite artifact paths rather than copying large
review outputs.
