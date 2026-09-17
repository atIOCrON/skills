# Orchestration Final Handoff

Final reporting component for orchestration workflows.

## Inputs

Require:

- route and final state;
- plan path;
- changed files and reviewed commit SHA;
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

## Output For Branch Handoff

Include:

- plan path and files changed;
- pinned parent and final verified, reviewed, local, and remote branch SHAs;
- clean-worktree verification commands and status;
- code-review pass count and one-line outcome per pass;
- rejected/deferred findings with evidence or recorded reason;
- reviewer artifact paths, including failures;
- triage ledger path and terminal-status counts;
- confirmation no non-terminal ledger entries remain;
- stack manifest path and final stack-check evidence;
- pending human or external acceptance checks, their procedures and owners,
  and any authorized limitation decisions;
- `## Skill Feedback For User Review` with entries or `- None`;
- final state: blocker or `Verified and pushed, ready for human review`.

Keep the handoff concise and cite artifact paths rather than copying large
review outputs.
