# Plan Implement

Implement one approved vertical-slice plan from `plans/in_progress/` within the
assigned file or module ownership scope. The plan defines intent and scope.
Binding policies, applicable repository standards, and affected contracts
govern correctness. General best practice informs in-scope work but does not
expand it. If no plan path or
ownership scope is provided, ask.

## Before Editing

1. Read the plan end to end, including out-of-scope notes.
2. Read its parent specification and slice map. Require both to be `approved`
   and require this plan's slice slug, acceptance ownership, blocker, and
   exclusions to match the map.
3. Open every cited `file:line`. If a line number is stale, search the current
   file for the referenced symbol, behavior, or nearby text and use the current
   location. Stop only when the claim cannot be verified in the current codebase,
   contradicts current evidence, or would materially change the approved scope.
4. Read applicable `AGENTS.md` files when present and the repository docs,
   configuration, tests, and contracts relevant to the touched surface.
5. Make a concise scope-to-change map. Map each changed surface and new
   component to an acceptance condition, binding policy, or affected contract.
   Omit anything that cannot be mapped.
6. Confirm the plan has one independently verifiable outcome, one rollback
   boundary, explicit sibling exclusions, and no acceptance group that can ship
   or fail independently. Stop for decomposition if it does not.
7. For any new architectural layer, dependency, configuration option,
   persistent object, public interface, compatibility behavior, or supported
   scenario, identify what requires it. Use a simpler design when it can meet
   the same requirements. Stop if necessary complexity is not authorized.
8. Before initial editing, write
   `<feature_dir>/<plan_slug>.execution/design-checkpoint.md`. On a fix dispatch,
   read it and update it only when the design changes. Record:
   - the native owner or extension point;
   - the smallest proposed design and expected production surfaces;
   - every new state owner or asynchronous coordinator, or `none`;
   - supported extensions, adapters, upgrades, upstream corrections, and
     direct dependency modifications that are relevant, and why the smaller
     options do not satisfy the slice;
   - behaviour-level verification and separate external acceptance; and
   - conditions that require stopping for architecture or slice replanning.
9. For a complex or cross-cutting change, write
   `<feature_dir>/<plan_slug>.execution/implementation-analysis.md` before
   editing. Keep it concise and include:
   - the scope-to-change map;
   - entry points and in-repo readers;
   - relevant state transitions and failure states;
   - invariants and hazards the implementation must preserve;
   - adversarial checks that can disprove the proposed behavior.

Use the analysis to shape the implementation and verification harness. Do not
send it to fresh reviewers; they retain an independent perspective.

Use repository instructions or indexes to choose relevant docs when available.

## Implementation Rules

- Choose the least-complex change that meets the acceptance conditions and
  preserves affected binding contracts.
- Prefer the platform's native lifecycle owner and documented extension point.
  A direct dependency modification can correct a narrow locked dependency
  defect; it does not by itself authorize local ownership of the dependency's
  general lifecycle.
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
- Use documented repository primitives and established nearby patterns when
  applicable.
- Preserve the existing invariants identified for the touched surface,
  including state transitions and failure handling.
- Stop before implementing an unapproved page-global mutable coordinator,
  cross-provider lifecycle manager, retry or recovery framework, substantial
  replacement of a dependency-owned surface, or permanent dependency
  modification spanning independently testable defects. Stop as well when the
  production footprint materially exceeds the design checkpoint. Line counts
  are warning evidence, not absolute limits.
- Do not stage files, commit, branch, push, or open a pull request.

## Verification

Run preliminary verification named by the plan when practical for the owned
surface. Add proportionate regression tests for changed behaviour even when
the plan omits them. Browser activation, renderer replacement, concurrency,
current-value changes, cancellation, retries, token invalidation, and provider
callbacks require executable behavioural tests at the highest practical local
seam. Source-text, snapshot, and generated-artifact-shape checks may supplement
but not replace those tests. Keep real-provider acceptance separate when it cannot run
locally. Run planned adversarial checks for complex or cross-cutting work.
Report failures honestly; if verification is impossible here, say why.

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

## Design Checkpoint
- <artifact path and whether the implementation stayed within it>

## Blockers
- <blocker, or None>
```

End with exactly one:

- `Ready for orchestrator integration`
- `Partial - blocker encountered`
