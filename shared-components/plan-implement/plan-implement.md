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
   location. Return unverifiable or contradictory claims to the runner for an
   evidence-based plan amendment; stop only at the calling skill's authority
   boundary.
4. Read applicable `AGENTS.md` files when present and the repository docs,
   configuration, tests, and contracts relevant to the touched surface.
5. Make a concise scope-to-change map. For each owned acceptance group, record
   the candidate-owned mechanism; whether the candidate introduces or modifies
   its lifecycle implementation or only changes routing, selection,
   configuration, or reachability; its runtime owner; and its branch-local,
   inherited, and external evidence. Map each changed surface and new component
   to an acceptance condition, binding policy, or affected contract. Omit
   anything that cannot be mapped. Do not equate a changed observable outcome
   with local ownership of an unchanged dependency lifecycle.
6. Confirm the plan has one independently verifiable outcome, one rollback
   boundary, explicit sibling exclusions, and no acceptance group that can ship
   or fail independently. Return it to the runner for an in-scope implementation
   split if it does not.
7. For any new architectural layer, dependency, configuration option,
   persistent object, public interface, compatibility behavior, or supported
   scenario, identify what requires it. Use a simpler design when it can meet
   the same requirements. Return any broader design to the runner's autonomous
   architecture checkpoint.
8. Before initial editing, write
   `<feature_dir>/<plan_slug>.execution/design-checkpoint.md`. On a fix dispatch,
   read it and update it only when the design changes. Record:
   - the architecture epoch, design identity, and prior failure class, if any;
   - the native owner or extension point;
   - the smallest proposed design and expected production surfaces;
   - every new state owner or asynchronous coordinator, or `none`;
   - supported extensions, adapters, upgrades, upstream corrections, and
     direct dependency modifications that are relevant, and why the smaller
     options do not satisfy the slice;
   - the verification-ownership classification, proposed local test machinery,
     applicable inherited evidence, and separate external acceptance; and
   - conditions that require architecture or slice reassessment.
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

At the design checkpoint, compare proposed verification machinery with the
candidate-owned production mechanism. If verification would introduce a
provider simulator, server model, persistence fixture, retry framework, or more
lifecycle machinery than the production change, simplify it or return the
verification footprint for correction before editing. Approval of a plan does
not authorize disproportionate verification machinery. Preserve the approved
acceptance outcome while amending a requested seam that would simulate
unchanged external or dependency-owned behaviour.

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
- Treat the plan's verification section as required evidence outcomes, not
  authorization to construct a disproportionate harness. A command mandated by
  the user or binding repository policy remains required; otherwise choose the
  smallest meaningful seam that proves the candidate-owned mechanism.
- If the plan conflicts with a binding policy, applicable repository standard,
  or affected contract, return it to the runner. Continue after an in-scope
  correction; require a human decision only when the conflict cannot be resolved
  without changing approved product scope or the binding source.
- If ownership is insufficient, return the exact expansion or split needed.
  The runner may expand repository-local ownership within the approved outcome;
  do not edit outside the assigned scope first.
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
- Return to the runner's architecture checkpoint before implementing a
  page-global mutable coordinator,
  cross-provider lifecycle manager, retry or recovery framework, substantial
  replacement of a dependency-owned surface, or permanent dependency
  modification spanning independently testable defects. Do the same when the
  production footprint materially exceeds the design checkpoint. The runner may
  amend the design within its recorded authority. Line counts are warning
  evidence, not absolute limits.
- Do not stage files, commit, branch, push, or open a pull request.

## Verification

Run preliminary verification named by the plan when practical for the owned
surface. Add proportionate regression tests for changed behaviour even when
the plan omits them. When the candidate introduces or modifies browser
activation, renderer replacement logic, concurrency, current-value changes,
cancellation, retries, token invalidation, or provider callbacks, require
executable behavioural tests at the highest practical local seam. Source-text,
snapshot, and generated-artifact-shape checks may supplement but not replace
proof of runtime behaviour the candidate owns.

When the candidate only changes routing, selection, configuration, or
reachability for an unchanged dependency-owned lifecycle, prove that mechanism
directly through source-contract evidence and effective runtime binding or code
identity. Reuse inherited test evidence only when its exact version,
configuration, relevant inputs, and effective result apply, and keep
real-provider acceptance separate when it cannot run locally. Lightweight test
doubles may establish candidate-owned routing or binding. Do not construct a
fake provider, server, persistence layer, account store, or order lifecycle
solely to prove unchanged behaviour owned elsewhere; the harness's transitions
are not production evidence. Run planned adversarial checks for complex or
cross-cutting work.
Report failures honestly; if verification is impossible here, say why.

## Output

```markdown
## Scope-to-Change Map
- <acceptance group> - <candidate mechanism> - <lifecycle modified or only exposed> - <runtime owner> - <local, inherited, and external evidence>

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
