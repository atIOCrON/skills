# Verification Runner

Verify exact committed candidate in a clean detached worktree, using fresh checks
and/or deterministic evidence reuse. Require repository, plan/commands, exact SHA,
touched files/modules, acceptance verification ownership, capability equivalence/
prior evidence when available, owner ref and verification point (initial or post-fix).
Missing commands return for in-scope evidence amendment; unresolved commit blocks
chain without substituting mutable state. Prepare readiness-inventoried locked
dependencies/services/fixtures/disabled-component setup reproducibly.

1. Resolve full candidate SHA, create detached worktree and confirm clean HEAD matches.
2. Map changed source and non-versioned dependencies to checks, using every determining
   input, not path overlap alone. Each required check runs there or reuses a passed
   origin with identical source/config/dependency/fixture/toolchain/runtime/effective
   identities, valid log/SHA and fresh current-tip proof. Missing/changed identity
   means rerun; new SHA or reviewer pass alone does not require expensive reruns.
3. Add proportionate behavioral checks for owned risks even if omitted by plan.
   New/modified browser/provider lifecycles cover applicable renderer replacement,
   concurrent values, fresh activation, cancellation/failure/retry/token invalidation/
   reauthorization at highest practical seam. Structural/snapshot/mutation/generated
   assertions supplement, never replace executable owned-runtime proof.
4. Unchanged dependency lifecycle reached via routing/config/selection needs direct
   source-contract/effective binding/code proof and exact applicable inherited tests,
   not fake provider/server/persistence/account/order models. Lightweight routing
   doubles are valid; unavailable real-provider checks remain external acceptance.
5. Save command/reuse mapping, exit/results, current/origin SHAs, input/result identities
   and evidence under primary `<feature_dir>/<plan_slug>.evidence/`; bulk logs stay
   outside. Explicit paths supply non-versioned inputs, never dirty-worktree copies.
6. Capture evidence, remove only the explicit temporary worktree, return
   `verification-passed` only if every required check passed or validly maps to tip.

On failure send existing owner command/error/expected behavior/scope/rerun/evidence.
New fixes use staged-diff-scope/git-branch-commit and a new clean verification worktree;
rerun only affected checks. After two failed fixes at one verification point, stop
repeating, group invariant and amend design/verification boundary, starting epoch
if mechanism changed. Continue in-scope redesign and independent work; block only
when every in-scope design violates hard constraint/approved outcome. Report SHA,
direct/reused checks/origins/identities/paths, attempts, cleanup and passed/blocked.
