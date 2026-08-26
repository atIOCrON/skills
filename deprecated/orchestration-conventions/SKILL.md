---
name: orchestration-conventions
description: 'Reference skill defining the shared orchestration vocabulary: plans layout and slug format, the cross-pass triage ledger protocol, material-finding and root-cause definitions, finding-ID formats, stacked pull request terminology, and the preflight smoke token. Use when another skill points here or when an orchestration term, artefact path, or ledger rule needs its canonical definition. Load only the reference file that covers the needed convention.'
metadata:
  layer: reference
---

# Orchestration Conventions

Reference skill for shared orchestration vocabulary and artefact contracts.
Load only the reference file needed for the current task.

## References

- `references/plans_layout.md`: plans directory layout and plan slug format.
- `references/triage_ledger_protocol.md`: cross-pass triage ledger schema,
  status vocabulary, identity matching, recurrence, and consolidation.
- `references/definitions.md`: material finding and root cause definitions.
- `references/finding_ids.md`: plan-review and code-review finding ID formats,
  reviewer slugs, and canonical finding line format.
- `references/stacked_prs.md`: stacked pull request terminology (base target
  branch, stack parent branch, PR target branch, true stacked PR chain,
  base-targeted stack).

## Inline Conventions

`AGENTS.md` is the repo-root docs index of the consuming project.

The literal token `ORCHESTRATE_SESSION_SMOKE` proves session resume in
`reviewer-preflight`.

## Precedence

Skills inline operational values such as artefact paths and ID shapes at their
point of use. This skill's reference files are the canonical definitions and
win on any conflict unless a skill explicitly defines an operational exception.
