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
- pinned parent and final verified, local, and remote branch SHAs, plus the
  three clean-review SHAs or valid review mappings;
- clean-worktree verification commands and status;
- code-review pass count and one-line outcome per pass;
- review-cap state and marker path when five completed passes did not satisfy
  review completion;
- rejected/deferred findings with evidence or recorded reason;
- reviewer artifact paths, including failures;
- triage ledger path and terminal-status counts;
- confirmation no non-terminal ledger entries remain;
- canonical release-manifest path, validation result, freeze state, and final
  stack-check status, including passed evidence or the prerequisites for checks
  that remain pending until a complete release candidate exists;
- pending human or external acceptance checks, their procedures and owners,
  and any authorized limitation decisions;
- release-progression status and each pending release-candidate check with its
  prerequisite;
- `## Skill Feedback For User Review` with entries or `- None`;
- final branch state: branch-level blocker, `Review cap reached`, or `In
  review`. After accepted fixes, closure, proportionate trim, and exact-tip
  verification, both completed states enter `review/`. A capped slice awaits
  human disposition for release readiness. Its verified pinned tip may parent
  dependent work while review or disposition remains pending. Report pending
  release-candidate checks separately; they do not change the slice stage.

Keep the handoff concise and cite artifact paths rather than copying large
review outputs.
