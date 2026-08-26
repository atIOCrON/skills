---
name: rank-concurrent-plans
description: Rank repo plans into dependency-safe concurrent agent lanes. Use when the user provides plans, plan ranks, or a plans/ folder and wants to know which plans can be implemented concurrently, which must be sequenced in the same lane, and which must wait because they depend on another lane.
metadata:
  layer: capability
---

# Rank Concurrent Plans

## Workflow

1. Read `AGENTS.md`, relevant docs, and each listed `plans/*.md`.
2. Extract dependency notes, files touched, explicit sequencing, and shared-module collisions.
3. Build lanes so each agent can implement its own list in order without waiting on another agent.
4. If a plan depends on another lane, either move it into that lane or put it in `Hold`.
5. Prefer fewer, larger lanes over cross-agent dependencies.
6. Treat same-file code edits as lane conflicts unless they are clearly independent and trivial. Treat docs-only conflicts as acceptable unless the user asks for zero conflicts.
7. Keep the answer short.

## Output

Use this shape:

```text
Agent 1:
- <rank> <plan>
- <rank> <plan>

Agent 2:
- <rank> <plan>

Hold:
- <rank> <plan> — <reason>
```

Add a one-line confirmation: all listed plans are covered, or name exactly which are held.

## Reusable Prompt

Rank these plans into dependency-safe concurrent agent lanes. Each agent may implement its own list in order. Do not assign any plan that needs another agent's work; put those in `Hold`. Output a plain list: `Agent N:` followed by `- <rank> <plan>`, then `Hold:` with reasons. Keep it short.
