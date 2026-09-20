---
name: rebuild-staging-from-default-branch
description: Replace staging with the pinned commit advertised as origin's default branch, preserve the previous staging tip, and verify deployment.
disable-model-invocation: true
metadata:
  layer: runner
---

# Rebuild Staging From Default Branch

Make `origin/staging` and the deployed application match the commit currently
advertised as `origin`'s default branch. Do not assume that branch is `main`,
`master`, or `develop`. Do not change the default branch, deploy production,
restore databases, replace media, or disturb local work.

Require the user to authorize moving `staging`. Do not switch, reset, clean,
stash, or edit local files; fetching may update Git metadata.

## Pin the default branch

1. Query `git ls-remote --symref origin HEAD` and require exactly one usable
   `refs/heads/<branch>` target. Do not infer it from the checked-out branch,
   `init.defaultBranch`, or a possibly stale local `origin/HEAD`. Stop if the
   advertised branch is missing, ambiguous, or `staging`.
2. Fetch `origin`, then pin the resolved default branch and `origin/staging`
   to full SHAs. If staging is absent, record that fact.
3. If a local branch with the resolved default-branch name exists, require its
   full SHA to equal the pinned origin SHA. If it differs, stop and report both
   SHAs. Do not compare or use a local `staging` branch.
4. Inspect pipeline and deployment scripts from the pinned default-branch
   commit. Check for active staging deployments before proceeding.

## Backup and replace staging

Record the running staging release and retained rollback release. A branch
backup preserves source history, not the deployed release or database.

Get one timestamp with `date -u +%Y%m%dT%H%M%SZ`. Immediately before mutation,
recheck remote staging. If it changed, stop.

If staging exists, create and verify a remote backup with an explicit absence
lease:

```text
backup/staging-before-rebuild/<UTC-timestamp>-<12-character-old-staging-sha>
```

Never overwrite a backup. If staging is absent, do not create one.

Replace staging with the pinned default-branch SHA using
`--force-with-lease=refs/heads/staging:<old-staging-sha>`, or an explicit
absence lease if staging did not exist. Never use plain `--force`, bypass
branch protection, carry staging-only commits forward, or retry a failed lease
against newly observed state without new user direction.

Pushing staging triggers the Bitbucket build and staging deployment. Follow
the pipeline for the pinned SHA. If staging already matches the default
branch, verify the running release and rerun that commit's pipeline only if a
deployment is needed.

Preserve the guards in `deploy-staging-code-only.php` and its verification
scripts. If dependency, module, or setup checks fail, stop and report that a
database deployment is required. Do not bypass checks or run an unrestricted
`setup:upgrade`.

Verify the remote staging SHA, deployed release, pipeline result, storefront,
login, product, cart, checkout, relevant regressions, and application errors.
If deployment fails, check database compatibility before using the established
release rollback procedure.

Report the resolved default-branch name and pinned SHA, old staging SHA or
absence, backup branch, previous and deployed releases, pipeline result,
checks, unresolved failures, and the exact leased revert command without
running it.
