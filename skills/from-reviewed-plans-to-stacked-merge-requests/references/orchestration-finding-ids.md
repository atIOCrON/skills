# Finding IDs And Finding Lines

- Plan-review finding IDs: `plan-p<pass_number>-<reviewer_slug>-NN`.
- Code-review finding IDs: `code-p<pass_number>-<reviewer_slug>-NN`.
- Code-review sub-pass IDs:
  `code-p<pass_number>-orchestrator-sub<subpass_number>-NN`.
- Reviewer slugs: `claude`, `codex`, and `cursor`. Transport does not affect
  finding IDs.
- The canonical cross-skill finding line format is:

```text
[{finding_id}] [{ledger_id}] <text>
```
