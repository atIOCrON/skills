# Orchestrator Runtime

The host is `codex`, `claude`, or `cursor`.

- Use the host's native sub-agents for implementation and its matching reviewer.
- Use CLI sessions for the other two reviewers.
- Start each reviewer in a fresh context and run all three in parallel.
- Reuse the implementation sub-agent for fixes and each reviewer context for
  closure.

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
