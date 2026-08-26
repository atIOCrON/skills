---
name: name-chat
description: Suggest a human-visible AI chat title using a shared /plans filename. Use when the user wants a clear title for the active GUI chat/sidebar entry.
metadata:
  layer: capability
---

# Name Chat

Suggest a human-visible GUI chat title as a retrieval label. Do not use this
skill for internal orchestration artifact labels, and do not require sub-agents
or external CLI reviewers to emit chat-name suggestions.

Once a `/plans` file exists, use its exact filename stem:

```text
<plan_slug> - <mode>
```

For example: `catalog_relationship_ownership - Implement` or
`valid_gtin_quality_gate - Code Review`.

When the platform supports direct chat renaming, rename the chat. Always also
include the title in-chat exactly:

````text
# Suggested chat title:

```
<plan_slug> - <mode>
```
````

## Modes

Use the smallest accurate label:

- `Idea` - early exploration before a plan file exists.
- `Plan` - creating or refining the `/plans` artifact.
- `Implement` - making code or documentation changes from the plan.
- `Debug` - investigating a failure, regression, trace, or unexpected result tied to the plan.
- `Plan Review` - reviewing a `/plans` file for correctness, scope, sequencing, standards alignment, and risks.
- `Code Review` - reviewing staged changes, implementation quality, regressions, missing tests, or code standards.
- `Test` - focused verification, test repair, or reproducibility work.
- `Docs` - documentation-only follow-up tied to the plan.
- `PR` - branch, commit, pull request, or git handoff work.
- `Orchestrate` - running the multi-agent planning, review, implementation, verification, and handoff workflow.
- `Follow-up` - related work deliberately split from the original plan.

If several chats share a slug and mode, append a short focus:

```text
<plan_slug> - Debug - export gate
```

## Before A Plan Exists

Use:

```text
<area> - Idea - <topic>
```

When a plan is created, switch to the plan-slug format.

## Rules

- The plan slug format is defined in
  `.agents/skills/orchestration-conventions/references/plans_layout.md`.
- Ledger, material, and artefact terms are defined in
  .agents/skills/orchestration-conventions/SKILL.md.
- Avoid dates, agent names, and vague words such as `misc`, `stuff`, `fixes`, or `changes`.
- If an existing plan slug is imperfect, still use it exactly unless the user asks to rename the plan.
- Suggest a title only when it helps the workflow. Do not repeat the same suggestion.
