---
name: write-high-level-plans
description: Write concise, outcome-focused implementation plans with foundational database schemas, while leaving detailed technical design to the implementing agent.
---

# Write High-Level Plans

Create or update the requested plan in the project’s `plans/` folder.

- Use `plans/<plan_name>.md`, with a lowercase `snake_case` plan name: words separated by single underscores, using only `a-z`, `0-9`, and `_`, with no leading or trailing underscore. Do not use hyphens or spaces.
- Keep the plan name to a maximum of 40 characters, including underscores but excluding the `.md` extension and directory path. Choose a concise, descriptive name and check its length before saving; for example, `supplier_stock_sync`.
- Inspect relevant code, documentation, and existing conventions first.
- State the goal, intended outcome, key decisions, dependencies, and boundaries.
- Specify every required new or modified table and view.
- For each new database object, define its name, grain, columns, data types, nullability, keys, relationships, and important field semantics.
- Distinguish schema requirements from implementation suggestions.
- Capture every user requirement in clear, contextualized plan language, preserving its intended meaning, scope, constraints, and acceptance conditions.
- Leave processing design, exact file changes, line numbers, and implementation mechanics to the implementing agent.
- Keep the plan direct, succinct, high level, and internally consistent.
