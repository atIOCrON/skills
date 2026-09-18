# Orchestrator Runtime

The host is `codex`, `claude`, or `cursor`.

- Use the host's native sub-agents for implementation and its matching reviewer.
  Use CLI sessions for the other two reviewers.
- Run `claude`, `codex`, and `cursor` in fresh parallel contexts for every
  discovery pass. All three must complete successfully.
- Use a fresh context for each discovery pass. Reuse the implementation
  sub-agent for fixes and the originating reviewer context for closure.

These automated reviews are pre-review evidence, not repository approval. A
qualified independent reviewer or required Code Owner must approve the final
SHA under repository policy.

Use native execution's start, wait, resume, and final-output capture operations.
Persist native output and session metadata in the same artifact shape as CLI
reviewers.

Resolve `orchestration_skill_root` to the directory containing the active
`SKILL.md`. Invoke bundled scripts with absolute paths under that directory.

For each run, record:

- host provider;
- provider-to-transport mapping;
- implementation session reference;
- all three reviewer session references.
