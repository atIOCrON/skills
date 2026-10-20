# Finding IDs And Finding Lines

- Historical plan-review IDs: `plan-p<pass_number>-<reviewer_slug>-NN`.
  Preserve these on existing artefacts; no plan-review phase is run by this workflow.
- Code-review finding IDs: `code-p<pass_number>-<reviewer_slug>-NN`.
- Reviewer slugs: `claude`, `codex`, and `cursor`. Transport does not affect
  finding IDs.
- The canonical cross-skill finding line format is:

```text
[{finding_id}] [{ledger_id}] <text>
```
