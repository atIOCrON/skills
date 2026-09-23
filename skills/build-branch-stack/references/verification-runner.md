# Verification Runner

Verify one committed revision in a clean detached worktree with fresh checks,
deterministic evidence reuse, or both. Hand bounded failures to its worker.

## Inputs

Require:

- repository root;
- plan path and verification commands;
- exact candidate commit SHA;
- touched files or modules;
- verification-ownership classification for each acceptance group;
- prior check evidence and capability-defined equivalence rules, when available;
- implementation worker reference when available;
- verification point, such as `initial-candidate` or `post-review-fix`.

If the plan lacks deterministic verification commands, return it to the runner
for an in-scope evidence amendment. If the commit cannot be resolved, block the
affected chain without substituting mutable workspace state.

Use the readiness inventory from `SKILL.md` to prepare exact locked
dependencies, required services and fixtures, and any isolated setup needed to
exercise components disabled in the default test configuration. Record the
setup and commands so the clean-worktree result is reproducible.

## Workflow

1. Resolve the candidate commit to a full SHA.
2. Create a temporary detached Git worktree at that SHA. Do not verify the
   mutable implementation checkout.
3. Confirm the temporary worktree is clean and its `HEAD` is the candidate SHA.
4. Map each changed file and non-versioned dependency to the checks it can
   affect. Use the capability's complete determining-input identities, not path
   overlap alone, to decide reuse.
5. For each required check, either run it from the candidate worktree or map a
   prior passed result to the candidate. Reuse requires identical determining
   inputs and effective result, a valid originating log and SHA, and fresh
   current-tip identity evidence. Rerun when any identity changed, is missing,
   or cannot be proved. Do not rerun an expensive deterministic check merely
   because the commit SHA changed. Starting a reviewer pass does not trigger a
   check; a changed tip or determining input may.
6. Add focused checks when candidate-owned risk justifies them. Require
   proportionate behavioural regression evidence even when the plan omits it.
   When the candidate introduces or modifies browser or provider lifecycle
   logic, cover applicable renderer replacement, concurrent value changes,
   fresh user activation, cancellation, failure and retry, token invalidation,
   and reauthorization at the highest practical local seam. Source-text,
   snapshot, mutation, and generated-artifact checks may supplement but not
   replace proof of runtime behaviour the candidate owns.

   When the candidate only changes routing, selection, configuration, or
   reachability for an unchanged dependency-owned lifecycle, verify that
   mechanism through source-contract evidence and effective runtime binding or
   code identity. Reuse inherited tests only when their exact version,
   configuration, relevant inputs, and effective result apply. Do not add or
   require a fake provider, server, persistence layer, account store, or order
   lifecycle solely to prove unchanged behaviour owned elsewhere; a harness's
   own transitions are not production evidence. Lightweight test doubles may
   prove candidate-owned routing or binding. Record unavailable real-provider
   checks as external acceptance.
7. Keep bulk output outside plan artefact folders. Save each command or reuse
   mapping, status, current and originating SHAs, input and result identities,
   concise results, and evidence links under
   `<feature_dir>/<plan_slug>.evidence/` in the primary checkout.
8. Remove only the explicit temporary worktree after capturing evidence.
9. Return `verification-passed` for the candidate SHA only when every required
   check either passed there or has valid deterministic reuse evidence.

Pass required non-versioned inputs by explicit path. Never copy dirty working
tree content into the verification worktree.

## Failure Repair

On failure, send the original worker the command, concise failure, expected
behavior, owned scope, and rerun command. The worker must create a new candidate
commit through `staged-diff-scope` and `git-branch-commit`; verify the new SHA
from a new clean worktree, rerunning only affected checks. After two failed fix
attempts at one verification point, stop repeating that fix and return to the
design checkpoint. Group the failures by invariant, amend the implementation or
verification boundary, start a new architecture epoch when the mechanism
changes, and continue. This checkpoint blocks only another repetition of the
failed fix; it does not block the plan or build run. Block the affected plan only
when every in-scope design conflicts with a hard constraint or the approved
outcome, and continue eligible independent plans.

## Output

Report the commit SHA, directly run and reused checks, originating SHAs,
identities, evidence paths, fix attempts, cleanup status, and final
`verification-passed` or `verification-blocked`.
