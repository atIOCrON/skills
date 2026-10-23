# Verification Runner

Verify the individual branch implementation at its exact committed candidate in
a clean detached worktree, using fresh checks
and/or deterministic evidence reuse. Require repository, plan/commands, exact SHA,
touched files/modules, acceptance verification ownership, capability equivalence/
prior evidence when available, owner ref and verification point (initial or post-fix).
Read the phase contract in `operational-records.md`. Only declared branch
implementation obligations gate this runner; return later integration/activation
checks with real status, owner, procedure, prerequisites and blocking milestone.
An agent-run or single-feature runtime check may belong to release/staging.
Reconcile saved mandatory gates under covering authority before changing them.
Missing commands return for in-scope evidence amendment; unresolved commit blocks
chain without substituting mutable state. Prepare readiness-inventoried locked
dependencies/services/fixtures/disabled-component setup reproducibly.

1. Resolve full candidate SHA, create detached worktree and confirm clean HEAD matches.
2. Map changed source and non-versioned dependencies to checks, using every determining
   input, not path overlap alone. Each required branch check runs there or reuses a passed
   origin with identical source/config/dependency/fixture/toolchain/runtime/effective
   identities, valid log/SHA and fresh current-tip proof. Missing/changed identity
   means rerun; new SHA or reviewer pass alone does not require expensive reruns.
3. Add focused behavioral checks for concrete implementation risks even if omitted
   by plan, using the cheapest sufficient seam. Cover changed lifecycle logic and
   applicable failure/atomicity/security cases; a database alone does not defer a
   check. Structural assertions supplement executable behavioral proof. Full
   assembled browser/provider journeys, renderer/asset integration and environment/
   account activation flow to release/staging or activation acceptance. Do not build
   a full environment merely for stronger branch evidence. Justify an exception
   by concrete implementation risk and why cheaper proof cannot suffice, or cite
   explicit user/binding-policy authority for an early gate.
4. Unchanged dependency lifecycle reached via routing/config/selection needs direct
   source-contract/effective binding/code proof and exact applicable inherited branch tests,
   not fake provider/server/persistence/account/order models. Lightweight routing
   doubles are valid; real-provider integration/acceptance stays in its assigned
   later phase even when available to an agent.
5. Save command/reuse mapping, exit/results, current/origin SHAs, input/result identities
   and evidence under primary `<feature_dir>/<plan_slug>.evidence/`; bulk logs stay
   outside. Explicit paths supply non-versioned inputs, never dirty-worktree copies.
6. Capture evidence, remove only the explicit temporary worktree, return
   `verification-passed` only if every required branch check passed or validly maps
   to tip. This claims no release acceptance; later pending checks do not block it.

On failure send existing owner command/error/expected behavior/scope/rerun/evidence.
New fixes use staged-diff-scope/git-branch-commit and a new clean verification worktree;
rerun only affected checks. After two failed fixes at one verification point, stop
repeating, group invariant and amend design/verification boundary, starting epoch
if mechanism changed. Continue in-scope redesign and independent work; block only
when every in-scope design violates hard constraint/approved outcome. Report SHA,
direct/reused checks/origins/identities/paths, attempts, cleanup and passed/blocked.
