# Orchestration Conventions

Bundled reference for shared orchestration vocabulary and artefact contracts.
Load only the reference file needed for the current task.

## References

- `references/orchestration-plans-layout.md`:
  plans directory layout and plan slug format.
- `references/orchestration-triage-ledger-protocol.md`:
  cross-pass triage ledger schema, status vocabulary, identity matching,
  recurrence, and consolidation.
- `references/orchestration-definitions.md`:
  material finding and root cause definitions.
- `references/orchestration-finding-ids.md`:
  plan-review and code-review finding ID formats, reviewer slugs, and canonical
  finding line format.
- `references/orchestration-stacked-mrs.md`:
  stacked merge request terminology (base target branch, stack parent branch,
  MR target branch, true stacked MR chain, base-targeted stack).

## Inline Conventions

`AGENTS.md` is the repo-root docs index of the consuming project.

The literal token `ORCHESTRATE_SESSION_SMOKE` proves session resume in
`reviewer-preflight`.

## Precedence

Components inline operational values such as artefact paths and ID shapes at
their point of use. These reference files are the canonical definitions and
win on any conflict unless a component explicitly defines an operational
exception.
