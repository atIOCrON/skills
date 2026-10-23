# Plan Implement

Implement one approved slice in `plans/slices/in_progress` within assigned
files/modules. If plan or ownership is missing, ask. Approved intent, exclusions,
binding policy/contracts and relevant repository standards govern scope; general
best practice adds none. Persistent owner continues commit/check/review route.

## Before editing

Read entire slice, parent/map and applicable AGENTS/repo/config/test/contracts.
Require all approved, map matching slug/acceptance/blockers/exclusions and parent
backlog/to_do/in_progress/review. Open every cited file:line, resolving stale lines
by symbol/current context; return unverifiable/contradictory claims for evidenced
amendment, stopping only at caller authority boundary. Require one verifiable
outcome/rollback boundary and sibling exclusions; return separable acceptance
outcomes for in-scope split.

Map each acceptance group/changed surface/component to candidate-owned mechanism,
lifecycle modified versus routing/config/reachability only, runtime owner, local/
inherited/external proof and binding requirement. Exclude unmapped work; changed
outcomes do not imply ownership of unchanged dependency lifecycles. Identify what
requires each new layer/dependency/config/persistence/interface/compatibility/scenario;
choose smaller sufficient designs and return broader ones to architecture checkpoint.

Before edits save `<feature_dir>/<plan_slug>.execution/design-checkpoint.md`:
architecture epoch/design/prior failure, native owner/extension, smallest design/
production surfaces, new state owners/async coordinators (or none), relevant
extension/adapter/upgrade/upstream/dependency alternatives and why smaller options
fail, verification ownership/harness/inherited/external proof, reassessment triggers.
Read on fixes; update when design changes. Complex/cross-cutting work also needs
`implementation-analysis.md`: scope map, entry points/readers, transitions/failures,
invariants/hazards and adversarial checks. Use it for implementation; exclude it
from fresh reviewer context to retain independence.

Compare test machinery with owned production mechanism before edits. Provider/server/
persistence simulators, retry models or disproportionate lifecycle fixtures require
simplification or verification-boundary amendment, even if a plan proposed them.
Preserve acceptance and binding commands without reconstructing unchanged upstream behavior.

## Implementation and verification

Use the least-complex native owner/documented extension meeting the outcome; no
hypothetical capability, compatibility shim, deprecation/fallback or unrelated cleanup.
Small detail deviations preserving approved outcome/authority and improving correctness
or repo fit are allowed; report them. Update every in-repo reader of changed schemas,
flags/views/errors/config/exports and retain touched invariants/transitions/failures.
Preserve others' edits. Return scope expansions before editing outside ownership;
caller can amend in-scope policy conflicts, otherwise obtain authorized decision.

Reassess before page-global mutable coordinators, cross-provider lifecycle managers,
retry/recovery frameworks, broad dependency replacement, patches spanning independent
defects or material excess over checkpoint. Lines are signals, not limits. Permanent
dependency correction needs reproduced locked-version defect and no supported extension:
record defect/rejected alternatives, smallest correction/removal condition, source/
effective identities, behavioral proof, replay order and maintenance effect; one coherent
defect per patch and applicable capability skill. A patch grants no general lifecycle ownership.

Run practical plan/preliminary and adversarial checks; add proportionate behavioral
regressions for candidate-owned changes even if omitted from plan. Lifecycle changes
(browser activation/rendering/concurrency/current values/cancellation/retry/token/provider
callbacks) need executable highest-practical-seam proof, not structural assertions alone.
Routing/selection/config/reachability of unchanged dependency lifecycles needs source
contract/effective runtime binding or code identity, exact applicable inherited proof
and separate real-provider acceptance. Lightweight routing doubles are valid; fake
provider/server/persistence/account/order transitions do not prove production. Plan
verification specifies evidence outcomes, not permission for excessive harnesses;
user/binding-policy commands remain required. Report impossible verification and why.

This edit phase does not stage/branch/commit/push/open CRs. Owner then follows assigned
selective-stage/new-commit/exact-check/independent-review route; coordinator or explicit
lease publishes. New findings authorize no new responsibility merely through broad acceptance.

## Operator handoff

Return `operator_handoff` under `operational-records.md`; reconcile four descriptions,
registered touched packages/modules and surfaces against branch-only diff after fixes.
Suggested tests claim no executed acceptance. Workers return draft/ready pinned data;
coordinator writes canonical JSON. Write for an operator with no code access:

- Use verified project/storefront/Admin terminology, not another domain's labels.
- Name real screens/actions/prerequisites/result location, checked in templates/layouts;
  internal terms get brackets on first use; fields appear only if visible there.
- Give no commands, paths or test names; explain automated/third-party coverage instead.
  Use short positive sentences without a sentence cap.
- State when fresh staging cannot reproduce old issue or only automation proves a case.
  Describe internal refactors as “an internal tidy-up with no visible effect”.

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

- `Ready for owner commit, verification and reviews`
- `Partial - blocker encountered`
