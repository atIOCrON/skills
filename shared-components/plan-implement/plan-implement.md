# Plan Implement

Implement one approved feature plan from `plans/in_progress/` within the
assigned file or module ownership scope. The plan defines intent and scope.
Binding policies, applicable
repository standards, and affected contracts govern correctness. General best
practice informs in-scope work but does not expand it. If no plan path or
ownership scope is provided, ask.

## Before Editing

1. Read the plan end to end, including out-of-scope notes.
2. Open every cited `file:line`. If a line number is stale, search the current
   file for the referenced symbol, behavior, or nearby text and use the current
   location. Stop only when the claim cannot be verified in the current codebase,
   contradicts current evidence, or would materially change the approved scope.
3. Read the docs AGENTS.md labels as code standards and logging standards, and
   any other referenced or relevant `docs/*.md`.
4. Make a concise scope-to-change map. Map each changed surface and new
   component to an acceptance condition, binding policy, or affected contract.
   Omit anything that cannot be mapped.
5. For any new architectural layer, dependency, configuration option,
   persistent object, public interface, compatibility behavior, or supported
   scenario, identify what requires it. Use a simpler design when it can meet
   the same requirements. Stop if necessary complexity is not authorized.
6. For a complex or cross-cutting change, write
   `<feature_dir>/<plan_slug>.execution/implementation-analysis.md` before
   editing. Keep it concise and include:
   - the scope-to-change map;
   - entry points and in-repo readers;
   - relevant state transitions and failure states;
   - invariants and hazards the implementation must preserve;
   - adversarial checks that can disprove the proposed behavior.

Use the analysis to shape the implementation and verification harness. Do not
send it to fresh reviewers; they retain an independent perspective.

Use `AGENTS.md` to choose relevant docs.

## Implementation Rules

- Choose the least-complex change that meets the acceptance conditions and
  preserves affected binding contracts.
- Do not add capability for hypothetical future needs.
- Small implementation-detail deviations are allowed when they preserve the
  approved outcome, stay within the plan's authorization envelope, improve
  correctness, or better match current repo patterns. Report the divergence.
- If the plan conflicts with a binding policy, applicable repository standard,
  or affected contract, stop and report the conflict. Do not broaden scope to
  resolve it without user approval.
- If the ownership scope is insufficient, stop and report the needed scope
  expansion instead of editing outside it.
- The workspace may contain edits from the user or other agents. Do not revert,
  overwrite, or clean up work you did not make.
- Update every in-repo reader of a changed schema, CLI flag, view, error shape,
  config key, or exported field within your scope.
- No backward-compatibility shims, deprecation paths, fallback defaults,
  speculative features, or unrelated cleanup.
- Use the repo primitives named by AGENTS.md as documented in the docs/ files
  it indexes.
- When relevant to the touched surface, preserve idempotency, raw/Bronze
  immutability, deterministic keys, lineage, batch boundaries, observability,
  and explicit empty, duplicate, and failure handling.
- Do not stage files, commit, branch, push, or open a pull request.

## Verification

Run preliminary verification named by the plan when practical for the owned surface.
Add proportionate regression tests for changed behavior even when the plan omits
them. Run planned adversarial checks for complex or cross-cutting work. Report
failures honestly; if verification is impossible here, say why.

## Output

```markdown
## Scope-to-Change Map
- <acceptance condition, policy, or affected contract> - <necessary change>

## Implemented
- <file> - <change>

## In-repo Readers Updated
- <file> - <why, or None>

## Verification
- <command/check> - <pass/fail/evidence>

## Changed Files
- <file>

## Implementation Analysis
- <artifact path, or Not required>

## Blockers
- <blocker, or None>
```

End with exactly one:

- `Ready for orchestrator integration`
- `Partial - blocker encountered`
