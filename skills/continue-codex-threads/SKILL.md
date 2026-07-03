---
name: continue-codex-threads
description: Send the fixed follow-up prompt "Continue. Claude usage has reset" to user-provided Codex threads. Use when the user asks Codex to continue, wake, resume, or message a specific list of existing Codex desktop/app threads by title or thread ID after Claude usage has reset.
metadata:
  layer: runner
---

# Continue Codex Threads

Send one fixed follow-up message to existing Codex threads selected by the user.
Do not create new threads, fork threads, rename threads, archive threads, or change
model/reasoning settings. Use the bundled sender script, which drives Codex
app-server with `thread/resume` followed by `turn/start`.

## Message

Always send this exact prompt:

```text
Continue. Claude usage has reset
```

## Workflow

1. Extract the user-provided target threads. Accept thread IDs and exact thread
   titles. Do not infer extra targets beyond what the user named.
2. Run the sender script from the repo root with the exact targets supplied by
   the user:

```bash
.agents/project-skills/continue-codex-threads/scripts/send_continue_message.py "<THREAD_TITLE_OR_ID>" "<ANOTHER_THREAD_TITLE_OR_ID>"
```

3. The script must resolve every target before sending anything. If any target
   is missing or ambiguous, stop and report the unresolved targets.
4. For each resolved thread ID, the script starts a Codex app-server connection,
   resumes the thread, starts a new turn with the fixed prompt, and waits for
   the turn to complete. A message is not considered sent merely because a user
   item was appended; the script must observe `turn/completed`.
5. Report the exact thread titles and IDs messaged, the new turn IDs, and any
   targets skipped or failed.

For a preview that does not send messages, run:

```bash
.agents/project-skills/continue-codex-threads/scripts/send_continue_message.py --dry-run "<THREAD_TITLE_OR_ID>" "<ANOTHER_THREAD_TITLE_OR_ID>"
```

## Guardrails

- Send only to threads explicitly provided by the user in the current request or
  clearly referenced from immediately preceding context.
- Do not use fuzzy title matches for sending. Exact title matches or thread IDs
  are required.
- Include archived threads in resolution output, but do not skip them solely
  because they are archived unless the user asked for active threads only.
- If multiple exact title matches exist, treat the target as ambiguous.
- Do not use Computer Use, Chrome, the in-app browser, or desktop UI automation.
- Do not use `codex exec resume`; it can persist a user message without reliably
  running the resumed assistant turn. Use app-server `thread/resume` plus
  `turn/start` through the sender script.
- Do not use interactive `codex resume`.

## Helper Script

`scripts/resolve_threads.py` reads the local Codex state database and resolves
exact titles or IDs. It is read-only. Use `--json` when structured output is
more convenient for batching tool calls.

`scripts/send_continue_message.py` resolves the same targets and then sends the
fixed prompt by running an app-server turn in each resolved thread. Use this
script for the normal workflow.
