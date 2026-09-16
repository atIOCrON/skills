---
name: artefact-audit
description: Audit implementation and review artefacts for follow-up items, then verify whether each follow-up is still needed in the current codebase. Use when asked to inspect completed implementation artefacts, review folders, worker feedback, or review artefact follow-ups. Read-only unless explicitly asked to create plans or edit code.
disable-model-invocation: true
metadata:
  layer: capability
---

# Artefact Audit

Audit completed implementation and review artefacts without changing code.

Ledger, material, and artefact terms are defined in
.agents/skills/orchestration-conventions/SKILL.md.

## Scope

- Audit completed features under `plans/done/<slug>/` by default. Audit a
  named feature or stage when the user asks, including ongoing reviews.
- Each feature contains `<slug>.md` and any `<slug>.reviews/`,
  `<slug>.execution/`, and `<slug>.evidence/` folders. A review folder alone
  does not establish completion.
- Do not edit files unless the user explicitly asks for plans or fixes after the audit.

## Method

1. Read `AGENTS.md`, then only the docs relevant to the artefacts found.
2. List candidate artefact folders in the selected stage:

```bash
find plans/done -mindepth 2 -maxdepth 2 -type d -name "*.reviews" | sort
find plans/done -mindepth 2 -maxdepth 2 -type f -name "*.md" | sort
```

Use the requested stage instead for other audits. Check that it exists before
running `find`.

3. For each in-scope artefact folder, inspect:
   - `code-review-triage-ledger.md`
   - latest `triage.md`
   - reviewer files containing `Related Existing Issues`, `follow-up`, `out of scope`, `deferred`, `rejected`, or `open`
4. Separate formal ledger status from advisory related-existing notes.
5. Verify each candidate follow-up against current code/docs/tests with `rg`, targeted file reads, and small read-only commands when useful.
6. Check `git status --short` and mention dirty files only if they affect the audit.

## Output

Report:

- In-scope implementation artefact sets reviewed.
- Follow-ups still needed, with file references and why current code confirms them.
- Follow-ups already resolved or not needed, with brief evidence.
- Any relevant dirty-worktree caveats.

Keep the answer concise. Do not paste long artefact text. Do not recommend code changes beyond naming the needed follow-up.
