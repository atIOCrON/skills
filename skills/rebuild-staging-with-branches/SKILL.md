---
name: rebuild-staging-with-branches
description: Build an integration branch from a pinned origin base and the user's selected feature branches, validate it, then replace staging and verify deployment. The base defaults to origin's advertised default branch.
disable-model-invocation: true
metadata:
  layer: runner
---

# Rebuild Staging With Branches

Make `origin/staging` match one tested integration of a pinned base and the
user's ordered, already-pushed branches. This is a staging pointer rebuild,
not `build-branch-stack` or `promote-branch-to-staging`. Do not require a
frozen release manifest or send the user to create one.

Do not change the base or source branches, deploy production, merge old
staging, or disturb existing local work. Perform integration work in a
separate disposable checkout.

## User input

The user supplies:

- the target repository, defaulting to the current workspace;
- an ordered list of branch names whose `origin` tips are the inputs;
- optionally, a base branch; otherwise use `origin`'s advertised default
  branch; and
- authorization to move `staging`.

For example:

```text
/rebuild-staging-with-branches

On top of the repository default branch:
feature/staging-integration/20260918T104341Z
feature/checkout-card-refresh
feature/some-other-branch
```

The user may instead say `On top of develop:` or name another base. Never
assume that the base is `main`, `master`, or `develop`.

## Pin inputs and write the receipt

1. Resolve the repository root without switching, resetting, cleaning,
   stashing, or editing the user's tracked work. Use `origin` as the remote.
2. If the user omitted the base, query the remote directly with
   `git ls-remote --symref origin HEAD`. Require exactly one usable
   `refs/heads/<branch>` target. Do not infer the base from the current local
   branch, `init.defaultBranch`, or a possibly stale local `origin/HEAD`. If
   remote HEAD is missing, ambiguous, or points to `staging`, stop and ask the
   user to name the base.
3. Validate every supplied name as a branch name. Fetch `origin`, then pin the
   base, each listed `refs/remotes/origin/<branch>`, and current
   `refs/remotes/origin/staging` to full commit SHAs. A missing selected branch
   is an error. `staging` may be absent.
4. For the base and every selected feature, if a corresponding local
   `refs/heads/<branch>` exists, compare its full SHA with the pinned origin
   SHA. Stop and report both SHAs if they differ. A missing local branch is
   fine. Never substitute a local tip for the origin tip. Do not apply this
   comparison to a local `staging` branch; the remote staging pointer is
   authoritative.
5. Get one timestamp with `date -u +%Y%m%dT%H%M%SZ`. After pinning, write a
   small receipt in the original target workspace, not the disposable
   integration checkout:

   ```text
   plans/releases/staging-rebuild-<UTC-timestamp>/manifest.json
   ```

   Before creating it, verify that the exact prospective file is ignored with
   `git check-ignore`. If it is not ignored, stop and ask the user; do not edit
   `.gitignore`. The receipt is a local operational record: never stage,
   commit, or push it, and never use `git add -f`. Creating and updating this
   ignored receipt is the only permitted change in the user's original
   workspace.

Start the receipt with `state: "building"`. Keep it small and record at least:

- `release_id`: `staging-rebuild-<UTC-timestamp>`;
- `state`: `building`, changed to `staged` only after verified deployment;
- `created_from`: `user_branch_list`;
- `base`: the actual remote, branch name, and pinned full SHA;
- `branches`: ordered `source` and pinned `tip_sha` entries;
- `integration`: branch name, candidate commit SHA, tree SHA, and merge order;
- `staging_before`: the old `origin/staging` SHA or `null`;
- `backup`: the backup branch name or `null`; and
- `staging_after`: the new staging SHA, once verified.

Use `null` for candidate, tree, backup, and staging-after values that are not
known yet, then update them as the rebuild advances.

The receipt is evidence produced by this skill, not a prerequisite or release
scope authority. Do not add freeze digests, review blocks, plan paths, or
release-orchestration gates.

## Build and validate

1. Create `feature/staging-integration/<UTC-timestamp>` at the pinned base in
   the disposable checkout. Exclude uncommitted changes. Do not add branches
   the user did not list.
2. Process the pinned feature tips in the user's exact order:
   - if the current candidate is an ancestor of the next tip, fast-forward;
   - if the next tip is already an ancestor of the candidate, record the
     no-op; and
   - otherwise merge the pinned tip.

   Never reorder the list silently. If the supplied order conflicts with a
   demonstrated dependency, stop and report it.
3. Classify conflicts. Generated `composer.lock` or routine `composer.json`
   conflicts may be regenerated with the repository's pinned toolchain and
   locked inputs. Behavioral and patch-preimage conflicts require a product
   decision; stop if unresolved. Resolve authorized integration-only
   conflicts only in the disposable checkout. Do not rewrite or restack a
   source branch to repair them.
4. Confirm that the pinned base and every selected tip are ancestors of the
   candidate. Inspect dependency locks and patch order. Run the repository's
   relevant build, tests, and regressions. Pin the final candidate commit and
   tree SHAs, then update the still-ignored receipt.

## Replace and verify staging

1. Inspect pipeline and deployment scripts from the candidate. Preserve their
   code-only versus database-deploy guards. Check for an active staging deploy
   lock. Record the running release and retained rollback release.
2. Recheck remote staging immediately before mutation. If it differs from
   `staging_before`, stop; do not silently repin or retry.
3. If staging exists, create and verify this remote backup with an explicit
   absence lease, never overwriting an existing ref:

   ```text
   backup/staging-before-rebuild/<UTC-timestamp>-<12-character-old-staging-sha>
   ```

   If staging is absent, record `backup: null`.
4. Push the unique integration branch with an absence lease and verify its
   remote SHA. Then update `refs/heads/staging` directly to the candidate once,
   using `--force-with-lease` with the pinned old SHA or an absence lease when
   staging did not exist. Never use plain `--force`, bypass branch protection,
   open an MR into staging, or deploy intermediate commits. Stop on a failed
   lease.
5. Follow the staging pipeline. Verify the remote staging SHA, live release,
   previous release retention, application health, and relevant regressions.
   Change the receipt to `state: "staged"` and set `staging_after` only after
   the candidate identity and deployment are verified. Otherwise leave it in
   `building` state and record the failure in the report.

## Report

Report the resolved base branch and SHA, ordered source SHAs, integration
branch, candidate commit and tree SHAs, receipt path, backup or prior branch
absence, previous and live releases, pipeline result, checks, and unresolved
failures.

Also report the exact leased revert command without running it. When staging
previously existed, the command must restore `staging_before` while leasing on
the deployed candidate SHA. When staging was previously absent, the command
must delete `staging` while leasing on the deployed candidate SHA.
