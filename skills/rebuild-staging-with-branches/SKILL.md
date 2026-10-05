---
name: rebuild-staging-with-branches
description: Assemble selected pushed branches on a pinned origin base, reuse valid test evidence, verify new combinations, then deploy through the staging pipeline. The base defaults to origin's advertised default branch.
disable-model-invocation: true
metadata:
  layer: runner
---


Read `references/operational-records.md` before creating or updating plan metadata,
builds, releases or deployments. Its schema-v2 JSON contract is authoritative
for operational records. Write and validate canonical JSON alongside each state
change; do not leave the browser report to reconstruct state from Markdown.
Use `scripts/validate_operational_records.py <record> --project-root <original-project>`
for each owned record before handoff. Whole-project audit findings are separate.
Keep historical extensions and existing authorization, verification and review
gates; they do not authorize schema aliases or inferred reporting values.
# Rebuild Staging With Branches

Make `origin/staging` match one tested integration of a pinned base and the
user's ordered, already-pushed branches. This is a staging pointer rebuild,
not `build-branch-stack` or `promote-branch-to-staging`. Do not require a
frozen release manifest or send the user to create one.

Do not change the base or source branches, deploy production, merge old
staging, or disturb existing local work. Perform integration work in a
separate disposable checkout.

An unchanged candidate with passed final stack checks needs deployment
verification, not another development cycle. A new mix of branches needs
combined checks; passing each source build does not verify the mix. Reuse
applicable evidence and let the pipeline build the deployment artifact once.

## User input

The user supplies:

- the target repository, defaulting to the current workspace;
- an ordered list of branch names whose `origin` tips are the inputs;
- optionally, a base branch; otherwise use `origin`'s advertised default
  branch; and
- authorization to move `staging`.

Release preparation may also supply `expected_candidate_sha`: one full commit
SHA that staging must deploy unchanged. In this mode require exactly one input
branch at that SHA and the pinned base to be its ancestor. Reject a divergent
base rather than merging it into an accepted release. Ordinary rebuilds keep
their existing behavior.

For example:

```text
/rebuild-staging-with-branches

On top of the repository default branch:
integration/20260918T104341Z
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
   When `expected_candidate_sha` is supplied, call
   `scripts/verify_candidate.sh <pinned-base-sha> <expected-sha> <sole-input-sha>`
   now, before receipt creation or any remote mutation. Stop on failure.
5. Get one timestamp with `date -u +%Y%m%dT%H%M%SZ`. After pinning, write a
   small receipt in the original target workspace, not the disposable
   integration checkout:

   ```text
   plans/deployments/staging-rebuild-<UTC-timestamp>/manifest.json
   ```

   Before creating it, verify that the exact prospective file is ignored with
   `git check-ignore`. If it is not ignored, stop and ask the user; do not edit
   `.gitignore`. The receipt is a local operational record: never stage,
   commit, or push it, and never use `git add -f`. Creating and updating this
   ignored receipt is the only permitted change in the user's original
   workspace.

Start the schema-v2 deployment receipt with `outcome: "pending"`, explicit
`deployment_id`, environment, optional release ID, null candidate pins and an
empty `included_slices` array. Record ordered inputs, base, backup, old staging
pointer and pipeline/recovery evidence under `extensions`. Update candidate
pins during assembly and record exact slice/source/tip membership from validated
release/build JSON or verified Git ancestry. No Markdown inference is allowed.
An integration branch supplied by release preparation must carry the release's
individual slice membership, not just the integration source itself.

Use `outcome: "verified"` only after the candidate and deployment checks pass;
record its evidence path. Preserve failed attempts with `outcome: "failed"`
and failure details. Validate the receipt before publishing each transition.
The receipt is deployment evidence, not release selection or acceptance authority.

## Assemble

1. Create `integration/<UTC-timestamp>` at the pinned base in
   the disposable checkout. Exclude uncommitted changes. Do not add branches
   the user did not list.
2. Process the pinned feature tips in the user's exact order:
   - if the current candidate is an ancestor of the next tip, fast-forward;
   - if the next tip is already an ancestor of the candidate, record the
     no-op; and
   - otherwise merge the pinned tip.

   Branch tips include their ancestors. Check that inherited features are in
   scope and all functional prerequisites are present; a selected tip may
   include earlier features the user did not name separately. Report unclear
   scope or missing prerequisites before proceeding. Never silently reorder
   inputs, add prerequisites, or cherry-pick around unwanted ancestors.
   If the supplied order conflicts with a demonstrated dependency, stop.
3. Classify conflicts. Resolve only mechanical integration conflicts whose
   result is determined by the selected inputs, such as regenerating
   `composer.lock` with the repository's pinned toolchain and locked inputs.
   Stop if a resolution would require editing tests, runtime source, patches,
   or behavior-affecting dependency configuration. Do not make corrective
   changes on the integration branch, and do not rewrite or restack a source
   branch to repair them.
4. Confirm that the pinned base and every selected tip are ancestors of the
   candidate. Pin its commit and tree SHAs, then update the ignored receipt.
   With `expected_candidate_sha`, repeat `scripts/verify_candidate.sh` against
   the final candidate. Do not regenerate locks, resolve conflicts, or add
   commits in this mode: such work changes the release candidate.

## Verify without duplicating work

Inspect the candidate's pipeline and available source-build evidence. Use
existing build manifests and logs when present; do not require a release
manifest. Record a compact check list with each check's owner (local or CI),
fresh or reused result, and evidence path.

- **Previously tested candidate:** reuse passed final combined checks for the
  exact candidate while their determining inputs remain unchanged. Finished
  branches or pending final stack checks are insufficient.
- **New combination:** run applicable combined checks on the assembled
  candidate. This includes subsets, changed bases, merges and conflict
  resolutions. Reuse qualifying branch checks; verify interactions across
  selected features and their shared surfaces. A clean merge or successful
  compilation does not establish behavioural compatibility.
- **Evidence reuse:** require a passed originating result and SHA, plus proof
  that the check's source, configuration, locks, patch order and hashes,
  fixtures, toolchain, runtime bindings and effective results remain
  equivalent. Use documented equivalence rules. A new SHA alone does not
  invalidate evidence; unchanged file paths alone do not establish it. Rerun
  when determining inputs changed or their equivalence cannot be proved.

Choose checks from the selected features' verification requirements and
cross-feature risk. Cover dependency/patch compatibility and shared runtime
behaviour, especially Magento DI, configuration and checkout when affected.
Broaden to the relevant regression suite when interaction scope is uncertain.
Do not repeat branch implementation, trim or blanket code reviews.

Prefer one locked install, patch application, compilation, asset generation
and artifact package in CI, followed by deployment of that same artifact.
Run required tests locally when CI does not cover them. Defer checks to CI
only when they run against this candidate and block activation on failure;
a build-and-deploy pipeline is not evidence that regression tests ran.
Use the pinned toolchain and install only what local checks need. If those
checks require a full local build and CI cannot reuse its artifact, record
why both builds are necessary; otherwise do not create an unused local
deployment artifact. This skill does not change CI configuration.

Before moving staging, every required check must have passed or be assigned
to a confirmed CI gate before activation. Any local failure stops the rebuild;
leave the receipt in `building` and report the source branch to correct.
Do not alter the integration candidate to make checks pass. After pushing,
any CI failure stops deployment verification; inspect deployment state before
retrying or rolling back.

## Replace and verify staging

1. Inspect pipeline and deployment scripts from the candidate. Preserve their
   code-only versus database-deploy guards. Check for an active staging deploy
   lock. Record the running release and retained rollback release.
   If remote staging and the healthy live release already match the candidate
   and all required checks have valid passed evidence, skip backup and ref
   publication and continue with deployment verification below.
2. Recheck remote staging immediately before mutation. If it differs from
   `staging_before`, stop; do not silently repin or retry.
   With `expected_candidate_sha`, also recheck the sole input and remote base
   against their pins, then repeat the exact-candidate guard before any backup
   or staging mutation. Stop on drift.
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
5. Pushing `staging` triggers its pipeline. Follow that run for the pinned SHA;
   do not start a second deployment manually or trigger a duplicate pipeline.
   Confirm assigned CI checks passed, the remote and live candidate SHAs match, the
   previous release remains available, and deployment lock and maintenance
   state are clear. Run staging smoke checks for application health, essential
   journeys and affected surfaces. Rerun deeper checks only where the staging
   environment invalidates earlier evidence or a smoke failure warrants them.
   Set `outcome: "verified"`, candidate pins and evidence only after the
   candidate identity and deployment are verified. Otherwise record `failed`
   with its evidence, or keep `pending` while the outcome remains unknown.

Preserve database deployment guards and established recovery procedures.
Known database drift does not waive them; keep database recovery separate
from branch verification and follow existing user authorization.

## Report

Report the resolved base branch and SHA, ordered source SHAs, integration
branch, candidate commit and tree SHAs, receipt path, backup or prior branch
absence, previous and live releases, pipeline result, checks, and unresolved
failures. Distinguish fresh and reused checks, deferred CI gates and any
necessary duplicate build. Record assembly, local verification and pipeline
timings when available. Report "deployed and ready for user testing" after
verification; full staging acceptance belongs to `integrate-and-test-staging`
when requested, and is not implied by deployment.

Also report the exact leased revert command without running it. When staging
previously existed, the command must restore `staging_before` while leasing on
the deployed candidate SHA. When staging was previously absent, the command
must delete `staging` while leasing on the deployed candidate SHA.
