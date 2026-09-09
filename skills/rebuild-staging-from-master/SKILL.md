---
name: rebuild-staging-from-master
description: Replace staging with a pinned master commit, preserve its previous history, and deploy to the staging server.
---

Make the staging branch and deployed application match origin/master.
Do not change master, deploy production, restore databases, replace
media, or disturb local work.

1. Fetch origin. Pin the master and staging SHAs. Inspect the pipeline
   and deployment scripts from the pinned master commit. Check for
   active staging deployments before proceeding.

2. Record the running staging release and its rollback artifact.
   A branch backup preserves source history, not the deployed release
   or database.

3. Before changing staging, push its current SHA to a remote backup
   branch using this format:

   backup/staging-before-rebuild/<UTC-timestamp>-<short-staging-sha>

   Use YYYYMMDDTHHMMSSZ and a 12-character commit SHA, for example:
   backup/staging-before-rebuild/20260908T043012Z-2f798cd89fa5

   Verify that the remote backup points to the full staging SHA.
   Never overwrite an existing backup branch.

4. Replace staging with the pinned master SHA. Staging-only commits
   remain in the backup; do not carry them forward or ask which to
   retain. Use an explicit lease:

   git push --force-with-lease=refs/heads/staging:<old-staging-sha> origin <master-sha>:refs/heads/staging

   Never use plain --force or bypass branch protection. If the lease
   fails, fetch and back up the new staging tip before retrying.
   Stop if concurrent updates continue.

5. Pushing staging triggers the Bitbucket build and staging deployment.
   Follow the pipeline for the pinned SHA. If staging already matches
   master, verify the running release and rerun that commit's pipeline
   only if deployment is needed.

6. Preserve the guards in deploy-staging-code-only.php and its
   verification scripts. If dependency, module, or setup checks fail,
   stop and report the required database deployment. Do not bypass
   checks or run an unrestricted setup:upgrade.

7. Verify the remote staging SHA, deployed release, and pipeline result.
   Check storefront, login, product, cart, checkout, relevant regressions,
   and application errors. If deployment fails, check database
   compatibility before using the established release rollback procedure.

Report the pinned master SHA, backup branch, previous and deployed
releases, pipeline result, checks, and unresolved failures.

Do not switch branches, reset, clean, stash, or edit local files.
Use pinned commit SHAs directly for remote pushes. Local changes
are limited to Git metadata updated by fetching.
