---
name: reviewer-preflight
description: Verify a reviewer CLI before a workflow uses it. Use to check that the claude or cursor-agent CLI is installed, can create or resume a session in the target workspace, can answer a smoke prompt, and can resume the same conversation. Takes the reviewer to verify (claude or cursor) as input.
compatibility: Requires the claude or cursor-agent CLI on PATH with valid authentication for the reviewer being verified
metadata:
  layer: capability
---

# Reviewer Preflight

Verify one reviewer CLI's availability and same-conversation resume behavior.

## Inputs

Require:

- reviewer: `claude` or `cursor`;
- repo root (required when the reviewer is `cursor`).

Fail with a clear message when the reviewer input is neither `claude` nor
`cursor`, and require the repo root when the reviewer is `cursor`.

## Claude Checks

Run:

```bash
.agents/skills/reviewer-preflight/scripts/run_reviewer_preflight.sh claude
```

## Cursor Checks

Run from the repository root, replacing `{repo_root}` with the absolute
repository root:

```bash
.agents/skills/reviewer-preflight/scripts/run_reviewer_preflight.sh cursor "{repo_root}"
```

## Pass Criteria

Pass only when:

- the reviewer CLI command resolves (`claude` or `cursor-agent`; for cursor,
  `cursor-agent create-chat` must also return a chat id);
- the first smoke prompt's normalized token line returns exactly
  `REVIEWER_SMOKE_OK`;
- the resumed session's normalized token line returns exactly
  `ORCHESTRATE_SESSION_SMOKE`.

Normalize smoke output by reading the last non-empty output line before
comparing it to the expected token. Some reviewer CLIs prepend model or agent
headers even when `--output-format text` is used; those headers should not fail
the smoke test when the final token line is correct.

## Failure Rules

Stop without retrying for: auth/login required, permission denied, missing
command, or a non-resumable session.

The smoke token convention is defined in .agents/skills/orchestration-conventions/SKILL.md.

## Output

Report:

- reviewer verified;
- command availability;
- smoke session/chat id;
- first prompt status;
- resume status;
- pass/fail;
- blocker reason when failed.
