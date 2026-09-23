# Code Review Pack

Build a neutral, commit-pinned pack at
`<feature_dir>/<plan_slug>.reviews/code-review-pack/`. Every fresh reviewer in
a pass uses the same immutable review boundary.

## Contents

Create or refresh:

```text
index.md
changed-files.txt
diff-stat.txt
changes.diff
ownership-map.md
verification-summary.md
evidence-manifest.json
acceptance-gates.md
deterministic-checks.md
hash-manifest.sha256
```

`index.md` records the plan, dependency-parent branch and pinned base SHA,
plan branch, review commit and tree SHAs, creation time, and evidence paths.
Link the slice's parent specification, slice map, and design checkpoint. Record
whether the actual production surfaces stayed within the checkpoint and identify
any new state owner, coordinator, lifecycle interception, whole-template
replacement, or other architectural layer. It also records which standards
sources were found. If `AGENTS.md` is absent,
say so and identify the applicable plan, repository docs and configuration,
affected contracts, tests, and nearby patterns used for review. General
engineering practice may inform a finding but is not a binding repository rule.
`ownership-map.md` maps each changed path to plan scope or owner. Capture each
deterministic command, exit status, and literal output.

Include the smallest pinned chain that determines changed behavior: the source
representation, any generator or transformation configuration, and the
consumer, runtime binding, or effective result. Put targeted excerpts or Git
object IDs and SHA-256 hashes in `index.md` or a linked context file. Identify
each source path and revision; explain omitted links. For generated or derived
deliverables, show reviewers both the source representation and the effective
result, plus the capability-provided content, configuration, and toolchain
identities that determine it.

Every source or effective result needed for review must be readable from the
reviewer's repository workspace. A path, hash, replay log, or reproduction
command does not replace the content. If the authoritative file is outside the
repository workspace, copy the exact file or the smallest sufficient pinned
excerpt into the pack, record its authoritative path, revision or replay input,
and SHA-256, and include the copy in `hash-manifest.sha256`. Keep large trees
outside the pack, but include the review-relevant files or excerpts; record
external bulk paths as code, not local Markdown links. The validator rejects a
pack outside the repository and local links that escape it.

In `evidence-manifest.json`, record the review SHA and one entry per required
check: `id`, `kind` (`agent` or `external`), `required`, `verified_sha`,
`last_run_sha`, `method` (`direct`, `identity_reuse`, or `null`), `command`,
`runtime`, `result` (`passed`, `failed`, `pending`, or
`blocked_by_environment`), `input_identity`, `result_identity`, `log_path`,
`log_sha256`, `reuse_evidence_path`, and `reuse_evidence_sha256`. Use `null`
for inapplicable fields.

For a direct agent result, set `verified_sha` and `last_run_sha` to the tested
SHA and `method` to `direct`. For reuse, set `verified_sha` to the current review
SHA, retain the originating run in `last_run_sha`, set `method` to
`identity_reuse`, and record content-addressed input and result identities plus
the current-tip reuse proof. The originating log and reuse proof must both
remain valid. A required passed agent check counts only when `verified_sha`
matches the review SHA. Link each log and reuse proof from
`verification-summary.md`.
Link supporting files with local Markdown links. Run
`scripts/validate_review_pack.py <pack-dir> <repo-root>` after creating or
refreshing the manifest; it checks local Markdown links, file hashes, check
fields, and log hashes. Fix errors before review. Include every pack file except
`hash-manifest.sha256` in the hash manifest; never hash the hash manifest itself.

In `acceptance-gates.md`, list each human or external gate separately from code
review findings. Record `passed`, `pending`, or `blocked by environment`, the
tested SHA or release, owner, procedure, and evidence location. State what
prevents a pending check and what will unblock it. A pending external gate does
not become a code-review defect merely because it cannot run here; retain its
required status for the later acceptance or production decision.

After a restack, link its old/new ranges, `range-diff`, delta classifications,
and deterministic evidence from `index.md`. When the range diff is equal and
the restack is conflict-free, record the old-to-new SHA mappings and retained
evidence from all three reviews. Require a fresh three-reviewer discovery pass
for manual resolutions, unequal range diffs, changed generated output, or
behavior changes.

After an eligible test-only remediation, link the old and new SHAs, exact-tip
verification, changed-test results, unchanged production and effective-result
identities, ledger state, and same-session closure from each originating
reviewer. Record `test_only_closure` mappings for all three reviews. Any missing
identity, non-test delta, extra accepted finding, or closure concern requires a
fresh three-reviewer pass.

For specialized generated or dependency-derived changes, link the applicable
capability's candidate evidence and deterministic reproduction results. Record
the immutable inputs and their identities, the effective result identity, and
the exact capability command used. Do not duplicate capability-specific replay
or validation procedures in this universal review pack.

## Deterministic Checks

Use explicit object IDs:

- scope and patch: `git diff <base-sha>...<review-sha>` and `--binary`;
- identity: `git rev-parse <review-sha>^{commit}` and `^{tree}`;
- ancestry: `git merge-base --is-ancestor <base-sha> <review-sha>`;
- pinned base and dependency-parent head equality;
- local branch tip, upstream, fetched remote tip, reviewed, and verified SHA
  equality;
- clean-worktree current-tip evidence plus direct or reused check evidence for
  `<review-sha>`;
- source and effective-result identity plus capability-defined deterministic
  checks where required.

A failed check, unexplained delta, or SHA mismatch blocks review.

## Refresh Policy

Build the pack before pass 1. After a fix commit or restack, refresh the commit,
diff, hashes, deterministic results, and verification evidence. Preserve and
link all three prior clean reviews for a proven equal-range-diff restack or an
eligible test-only remediation with recorded closure; otherwise run a fresh
three-reviewer discovery pass. Reuse immutable inputs
only when the applicable capability proves their content, configuration, and
toolchain identity; never rebuild an unchanged proven input merely to refresh
the pack. Starting a fresh reviewer pass does not itself rerun checks.
For evidence-only closure, keep the pinned diff and SHAs, refresh the evidence
links, manifest, hashes, and affected deterministic results, and record what
changed in the pack. Rerun the validator after each refresh.

Fresh reviewers receive only the pinned diff, approved plan, parent
specification, slice map, design checkpoint, repository standards, reproducible
inputs, verification results, and this pack. Distinguish behavioural evidence
from source-text, snapshot, mutation, and generated-artifact assertions;
structural checks cannot stand in for runtime lifecycle proof. Exclude prior findings,
triage, fix narratives, conclusions, and review hints.

## Output

Report the pack path, base and review SHAs, refreshed files, deterministic-check
status, and any blocker.
