---
name: rebuild-staging-with-branches
description: Build an integration branch from pinned master and selected feature branches, validate it, then replace staging and verify deployment.
---

Make staging match a tested integration of origin/master and the
user’s selected branches.

Do not change master, deploy production, or disturb existing local
work. Perform integration work in a separate disposable checkout.

1. Fetch origin. Pin master and each selected branch to full commit
   SHAs. Check staging directly on origin; record its SHA or absence.
   Distinguish local branches from remote branches. If their tips
   differ and the intended source is unclear, resolve that before
   merging. Exclude uncommitted changes.

2. Create feature/staging-integration/<UTC-timestamp> from pinned
   master. Inspect feature ancestry for dependencies and unrelated
   commits. Merge pinned feature SHAs in dependency order, preserving
   shared ancestry. Do not merge old staging or add unrequested
   branches. Resolve conflicts in the integration checkout; stop
   when resolution requires an unresolved product decision.

3. Validate the complete candidate. Confirm pinned master and every
   selected feature tip are ancestors. Review the diff against master,
   including conflict resolutions. Check dependency locks and patch
   order. Run the required build, tests, and relevant regressions.
   Commit integration fixes and pin the final candidate SHA.

4. Inspect pipeline and deployment scripts from the candidate.
   Preserve deployment guards. Resolve deployment prerequisites before
   updating staging; report anything outside the authorized scope.
   Check for active staging deployments. Record the running release
   and preserve its rollback artifact.

5. Recheck remote staging. If it exists, create and verify a remote
   backup pointing to its full SHA:

   backup/staging-before-rebuild/<UTC-timestamp>-<12-character-sha>

   Use YYYYMMDDTHHMMSSZ. Create backups with an explicit absence lease;
   never overwrite one. If staging is absent, record that fact.
   A source backup does not preserve the deployed release or database.

6. Push and verify the candidate under its unique integration branch.
   Then update staging once, directly to the candidate SHA.

   If staging exists:

   git push --force-with-lease=refs/heads/staging:<old-staging-sha> origin <candidate-sha>:refs/heads/staging

   If staging is absent:

   git push --force-with-lease=refs/heads/staging: origin <candidate-sha>:refs/heads/staging

   Never use plain --force or bypass branch protection. If the lease
   fails, recheck deployments and back up the new tip before retrying.
   Stop if concurrent updates continue. Do not deploy intermediate
   integration commits.

7. Follow the staging pipeline for the candidate SHA. Verify remote
   staging, the deployed release, pipeline result, application health,
   and relevant regressions. If deployment fails, establish rollback
   compatibility before using the repository’s recovery procedure.
   If staging already matches the candidate, rerun deployment only
   when the running release needs it.

Report the source SHAs, integration branch and candidate SHA, backup
or prior branch absence, previous and deployed releases, pipeline
result, checks, and unresolved failures.
