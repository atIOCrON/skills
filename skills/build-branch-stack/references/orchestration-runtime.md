# Orchestrator Runtime

The host is `codex`, `claude`, or `cursor`.

- Use the host's native sub-agents for implementation and its matching reviewer.
- Use CLI sessions for the other two reviewers.
- Run `claude`, `codex`, and `cursor` in fresh parallel contexts for every
  review pass. All three must complete successfully.
- Reuse the implementation sub-agent for fixes and each reviewer context for
  closure.

These automated reviews are pre-review evidence, not repository approval. A
qualified independent reviewer or required Code Owner must approve the final
SHA under repository policy.

Native execution must support start, wait, resume, and final-output capture.
Persist native output and session metadata in the same artifact shape as CLI
reviewers. Stop if the host cannot provide those operations.

Resolve `orchestration_skill_root` to the directory containing the active
`SKILL.md`. Invoke bundled scripts with absolute paths under that directory.

For each run, record:

- host provider;
- provider-to-transport mapping;
- implementation session reference;
- reviewer session references.
