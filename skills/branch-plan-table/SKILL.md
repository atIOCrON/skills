---
name: branch-plan-table
description: List current local and remote Git branches with their spec and slice plans in a chat table.
metadata:
  layer: capability
---

# Branch Plan Table

Use the requested repository, otherwise the active project. Work read-only; create no files.

1. Read local `refs/heads` and each remote live with `git ls-remote --heads <remote>`.
   Strip `refs/heads/`, combine exact branch names, deduplicate and sort alphabetically.
   Disclose failed remote checks; do not claim a complete inventory after failure.
2. Match current project plans: prefer slice sources, then intended branches and
   build records; use Markdown for legacy plans. Derive specs from slice ownership,
   not ancestry, dependencies or historical mentions. Leave missing or ambiguous plans blank.
3. Return one Markdown table in chat with exactly these headers:

   Branch name | Local | Remote | Spec plan | Slice plan

   Use `yes` for presence, blank for absence, and plan identifiers joined with
   semicolons for shared plans. Remote means present on any configured remote.
   Add prose only for lookup failures or mapping conflicts.
