---
name: write-high-level-plans
description: Write concise, outcome-focused implementation plans with foundational database schemas, while leaving detailed technical design to the implementing agent.
---

# Write High-Level Plans

Create or update the requested plan in the project’s `plans/` folder.

- Inspect relevant code, documentation, and existing conventions first.
- State the goal, intended outcome, key decisions, dependencies, and boundaries.
- Specify every required new or modified table and view.
- For each new database object, define its name, grain, columns, data types, nullability, keys, relationships, and important field semantics.
- Distinguish schema requirements from implementation suggestions.
- Capture every user requirement in clear, contextualized plan language, preserving its intended meaning, scope, constraints, and acceptance conditions.
- Leave processing design, exact file changes, line numbers, and implementation mechanics to the implementing agent.
- Keep the plan direct, succinct, high level, and internally consistent.
