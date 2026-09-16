# Verification Runner

Verify one committed revision in a clean detached worktree and hand bounded
failures back to its implementation worker.

## Inputs

Require:

- repository root;
- plan path and verification commands;
- exact candidate commit SHA;
- touched files or modules;
- implementation worker reference when available;
- verification point, such as `initial-candidate` or `post-review-fix`.

Stop if the plan lacks deterministic verification commands or the commit cannot
be resolved.

## Workflow

1. Resolve the candidate commit to a full SHA.
2. Create a temporary detached Git worktree at that SHA. Do not verify the
   mutable implementation checkout.
3. Confirm the temporary worktree is clean and its `HEAD` is the candidate SHA.
4. Run every required plan command from the temporary worktree root. Add focused
   checks when touched-surface risk justifies them. Require proportionate
   regression tests for changed behavior even when the plan omits them.
5. Keep bulk output outside plan artefact folders. Save commands, exit status,
   concise results, candidate SHA, and evidence links under
   `plans/<plan_slug>.evidence/` in the primary checkout.
6. Remove only the explicit temporary worktree after capturing evidence.
7. Return `verification-passed` only for that SHA.

Pass required non-versioned inputs by explicit path. Never copy dirty working
tree content into the verification worktree.

## Failure Repair

On failure, send the original worker the command, concise failure, expected
behavior, owned scope, and rerun command. The worker must create a new candidate
commit through `staged-diff-scope` and `git-branch-commit-push`; verify that new
SHA from a new clean worktree. Stop after two failed fix attempts at one
verification point.

## Output

Report the commit SHA, commands and status, focused checks, evidence paths, fix
attempts, cleanup status, and final `verification-passed` or
`verification-blocked`.
