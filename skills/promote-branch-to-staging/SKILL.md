---
name: promote-branch-to-staging
description: Point the disposable staging branch at one already-built feature tip, deploy the Bitbucket staging pipeline, and revert by restoring the backup SHA. Use when the user asks to push, promote, or test a finished feature on staging, or how that differs from a Bitbucket MR into staging. Not for resetting staging to the remote default branch or rebuilding several user-selected branches.
disable-model-invocation: true
metadata:
  layer: runner
---

# Promote Branch To Staging

Make `origin/staging` equal one already-pushed candidate SHA, then let the
Bitbucket `staging` pipeline do a code-only deploy. Do not change the resolved
base, rewrite pinned parent/integration/feature branches, deploy production,
restore databases, replace media, or disturb local work.

Use this skill only when **all** of these are true:

- The candidate branch is finished and already on `origin`.
- Current `origin/staging` is an **ancestor** of the candidate (fast-forward
  of what staging already runs). Typical case: staging still points at a
  pinned `feature/staging-integration/<UTC>`, and the new feature was branched
  from that exact SHA.
- The user authorized moving the staging pointer. Do not promote unsolicited.

Otherwise stop and use a different skill:

- Staging should match the remote default branch →
  `rebuild-staging-from-default-branch`
- Need to merge several user-selected branches on the resolved base →
  `rebuild-staging-with-branches`

## Why not a Bitbucket merge request into staging

Staging is a **leased disposable pointer**, not a merge target. An MR into
`staging` creates a merge commit, treats staging as long-lived history, and
makes revert a second merge instead of moving the pointer back.

Practice: push the candidate SHA to `refs/heads/staging` with
`--force-with-lease`. The feature branch, its pinned parent, and every source
feature stay at their existing SHAs. Only `staging` moves. Revert moves it
back.

Do **not** create an extra `feature/staging-integration/<UTC>` that merely
duplicates the candidate SHA. That name is for a rebuild that produces a new
integration commit. A named feature already *is* the candidate.

## Untouched vs changed

Untouched (no new commits, no force-push):

- resolved base branch
- pinned parent / previous integration branch
- every feature that went into that parent
- the candidate feature branch itself

Changed:

- `staging` → candidate SHA
- new backup ref `backup/staging-before-rebuild/<UTC>-<12-char-old-staging-sha>`
  → previous staging SHA

## Prepare

Do not switch, reset, clean, stash, or edit local files. Fetch, then pin
**full** SHAs from `origin`. Local Git metadata from fetch is the only local
change.

If the user names a base branch, use that branch from `origin`. Otherwise
resolve the base with `git ls-remote --symref origin HEAD`; require one usable
`refs/heads/<branch>` target. Do not assume `main`, `master`, or `develop`, and
do not infer the base from the checked-out branch, `init.defaultBranch`, or a
possibly stale local `origin/HEAD`. Stop if remote HEAD is missing, ambiguous,
or points to `staging`.

```bash
git fetch origin staging "$BASE" "$FEATURE" "$PARENT"
CANDIDATE=$(git rev-parse "origin/$FEATURE")
OLD_STAGING=$(git rev-parse origin/staging)
PARENT_SHA=$(git rev-parse "origin/$PARENT")
BASE_SHA=$(git rev-parse "origin/$BASE")
```

For the base, feature, and parent, compare any corresponding local branch with
the pinned origin SHA. Stop and report both SHAs if a local branch exists and
differs. A missing local branch is fine. Never substitute a local tip. Do not
compare or use a local `staging` branch.

Stop unless:

- `git merge-base --is-ancestor "$OLD_STAGING" "$CANDIDATE"`
- parent is still an ancestor of the candidate and still equals the SHA the
  user pinned
- `CANDIDATE` ≠ `OLD_STAGING` (if equal, do not redeploy unless the running
  release is unhealthy)
- candidate vs current staging is a **code-only** delta: no `app/etc/config.php`
  module enablement, no `db_schema.xml` / Setup scripts / `module.xml` that
  `bin/verify-code-only-deployment.php` will reject. Composer package *objects*
  must match; a lockfile `content-hash` only change is fine. If setup/module
  inputs differ, stop and report that this needs a database deployment, not
  this recipe.

Inspect `bitbucket-pipelines.yml` and `deploy-staging-code-only.php` from the
**candidate** commit. Keep their guards: staging path
`/var/www/html/staging.betterbatt.com.au/site`, `keep_releases=2`, no
unrestricted `setup:upgrade`.

Check there is no active staging deploy before mutating refs:

```bash
ssh -o BatchMode=yes -o ConnectTimeout=15 -p 22222 web@103.21.131.52 \
  'test ! -e /var/www/html/staging.betterbatt.com.au/site/.dep/deploy.lock'
```

Record the running release name (`current` symlink), release list, and
composer.lock `content-hash`. A git backup is branch history, not the
deployed release or database.

Get UTC once when needed: `date -u +%Y%m%dT%H%M%SZ`.

## Backup, then replace staging

Use one timestamp `TS` for the backup name. Never overwrite an existing
backup (absence lease). Verify the remote backup equals `OLD_STAGING`.

```bash
TS=$(date -u +%Y%m%dT%H%M%SZ)
SHORT=$(git rev-parse --short=12 "$OLD_STAGING")
BACKUP="refs/heads/backup/staging-before-rebuild/${TS}-${SHORT}"

git push --force-with-lease="${BACKUP}:" origin "${OLD_STAGING}:${BACKUP}"
git ls-remote origin "$BACKUP"

# Recheck origin/staging is still OLD_STAGING and the deploy lock is still absent.

git push --force-with-lease="refs/heads/staging:${OLD_STAGING}" \
  origin "${CANDIDATE}:refs/heads/staging"
```

Never use plain `--force` or bypass branch protection. If the staging lease
fails, fetch, back up the *new* tip, and retry once only if no concurrent
updates continue. Stop if staging keeps moving.

Pushing `staging` triggers the Bitbucket pipeline (`Build`, then
`Deploy Staging` via `dep -f deploy-staging-code-only.php deploy-artifact`).
Do not also open an MR.

## Follow the pipeline

Bitbucket HTTPS/API is often 401 here. Follow the deploy on the server
instead of polling `api.bitbucket.org`:

- `.dep/deploy.lock` appears, then a new directory under `releases/`
- `current` switches to the new release
- lock and `.dep/staging-deployment.json` clear
- previous release directory remains (`keep_releases=2`)

If `verify-code-only-deployment.php` fails, stop. Do not bypass it or run
`setup:upgrade`.

If staging already runs this candidate SHA and the release is healthy, do
not redeploy.

## Verify

Confirm:

- `git ls-remote origin refs/heads/staging` == `CANDIDATE`
- parent, feature, and resolved base SHAs unchanged
- backup still `OLD_STAGING`
- live `current` is a new release; previous release still on disk
- candidate files exist in `current` (patches/templates from the feature)
- lock/journal gone; storefront and checkout load; `var/log/exception.log`
  has no new deploy-time errors

Do not treat a Magewire “Something went wrong / refresh” overlay as proof
this promotion failed unless the candidate’s files uniquely cause it.

## Revert

Do not revert unless the user asks. Restore the pointer, then the pipeline
redeploys the previous commit. The previous release directory is only a
server-side file rollback aid until the next deploy replaces it.

```bash
git fetch origin staging
LIVE=$(git rev-parse origin/staging)   # must still be CANDIDATE
git push --force-with-lease="refs/heads/staging:${LIVE}" \
  origin "${OLD_STAGING}:refs/heads/staging"
```

Follow that pipeline the same way. Leave the backup ref in place.

## Report

State candidate SHA, old staging SHA, backup ref, whether an extra
integration alias was skipped, pipeline/deploy result, previous and live
release names, what was left untouched, verification, and the exact revert
push. Distinguish “deployed” from “accepted on staging.”
