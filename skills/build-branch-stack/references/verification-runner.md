# Verification Runner

Verify one committed revision in a clean detached worktree and hand bounded
failures back to its implementation worker.

## Inputs

Require:

- repository root;
- plan path and commands classified as `authoring`, `candidate`, or
  `integration`;
- exact candidate commit SHA;
- touched files or modules;
- implementation worker reference when available;
- verification point, such as `initial-candidate`, `post-review-fix`,
  `behavior-candidate`, or `patch-mechanics-candidate`;
- capability reuse keys and prior evidence, when available.

Stop if the plan lacks deterministic verification commands or the commit cannot
be resolved.

Use the readiness inventory from `SKILL.md` to prepare exact locked
dependencies, required services and fixtures, and any isolated setup needed to
exercise components disabled in the default test configuration. Record the
setup and commands so the clean-worktree result is reproducible.

## Workflow

1. Resolve the candidate commit to a full SHA.
2. Create a temporary detached Git worktree at that SHA. Do not verify the
   mutable implementation checkout.
3. Confirm the temporary worktree is clean and its `HEAD` is the candidate SHA.
4. Run every required `candidate` command from the temporary worktree root.
   Do not rerun `authoring` or `integration` commands. Reuse prior capability
   evidence only when its complete content, configuration and toolchain key
   matches; record the cache decision. Add focused checks when touched-surface
   risk justifies them. Use the smallest representative behavioral checks that
   exercise each materially distinct transition. Prefer an existing test seam;
   do not create a custom harness without the user's explicit approval recorded
   in the plan. Source-text, snapshot, mutation, and generated-artifact-shape
   checks are supplementary; they cannot be the primary proof of runtime behaviour.
   Record unavailable real-provider checks as external acceptance rather than
   replacing local behavioural coverage with structural assertions.
   For a Composer behavior candidate, include package-scoped strict replay and
   effective-tree equality but defer mechanics review. For a patch-mechanics
   candidate, verify delivery mechanics and equality; any effective-tree change
   returns the branch to behavior verification.
5. Keep bulk output outside plan artefact folders. Save commands, start and
   finish times, elapsed time, exit status, cache status, concise results,
   candidate SHA, and evidence links under
   `<feature_dir>/<plan_slug>.evidence/` in the primary checkout.
6. Remove only the explicit temporary worktree after capturing evidence.
7. Return `verification-passed` only for that SHA.

Pass required non-versioned inputs by explicit path. Never copy dirty working
tree content into the verification worktree.

## Failure Repair

On failure, send the original worker the command, concise failure, expected
behavior, owned scope, and rerun command. The worker must create a new candidate
commit through `staged-diff-scope` and `git-branch-commit`; verify that new
SHA from a new clean worktree. Stop after two failed fix attempts at one
verification point.

## Output

Report the commit SHA, commands and status, timing, cache decisions, focused
checks, evidence paths, fix attempts, cleanup status, and final
`verification-passed` or `verification-blocked`.
