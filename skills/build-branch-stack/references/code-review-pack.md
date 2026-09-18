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

Include the smallest pinned chain that determines changed behavior: the
component, its caller or theme consumer, relevant layout or DI binding, and
locked vendor method when applicable. Put targeted excerpts or Git object IDs
and SHA-256 hashes in `index.md` or a linked context file. Identify each source
path and revision; explain omitted links. Do not copy whole vendor trees into
the pack. For package provenance, identify the exact lock entry and package or
archive used to establish what the vendor ships.

In `evidence-manifest.json`, record the review SHA and one entry per required
check: `id`, `kind` (`agent` or `external`), `required`, `last_run_sha` (full
commit SHA or `null`), `command`, `runtime`, `result` (`passed`, `failed`,
`pending`, or `blocked_by_environment`), `log_path`, and `log_sha256`. Use
`null` paths and hashes when no log exists. A result from an older SHA must
remain visible with its old `last_run_sha`; it cannot count as a passed required
agent check on the current SHA. Link each log from `verification-summary.md`.
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

For vendor-derived changes, also record the exact package version or archive
hash, lockfile evidence, pristine and patched trees, complete hash manifests,
strict apply results without fuzz or offsets, and required byte comparisons.
Keep large trees outside review artefacts and link them from `index.md`.
Run `scripts/strict_patch_replay.sh <tree> <patch> <log> <strip-level>` for each
patch in registered order on an isolated tree. The
script requires GNU patch, uses `--fuzz=0`, rejects reported fuzz or offsets,
and saves the raw apply output even on failure. Link each log and its hash from
the pack. Do not infer strict application from a successful `patch --fuzz=0`
exit alone.

## Deterministic Checks

Use explicit object IDs:

- scope and patch: `git diff <base-sha>...<review-sha>` and `--binary`;
- identity: `git rev-parse <review-sha>^{commit}` and `^{tree}`;
- ancestry: `git merge-base --is-ancestor <base-sha> <review-sha>`;
- pinned base and dependency-parent head equality;
- local branch tip, upstream, fetched remote tip, reviewed, and verified SHA
  equality;
- clean-worktree verification evidence for `<review-sha>`;
- file identity, strict patch application, and byte comparison where required.

A failed check, unexplained delta, or SHA mismatch blocks review.

## Refresh Policy

Build the pack before pass 1. After a fix commit or restack, refresh the commit,
diff, hashes, deterministic results, and verification evidence. Preserve and
link all three prior clean reviews for a proven equal-range-diff restack;
otherwise run a fresh three-reviewer discovery pass. Do not rebuild an
unchanged vendor baseline.
For evidence-only closure, keep the pinned diff and SHAs, refresh the evidence
links, manifest, hashes, and affected deterministic results, and record what
changed in the pack. Rerun the validator after each refresh.

Fresh reviewers receive only the pinned diff, approved plan, parent
specification, slice map, design checkpoint, repository standards, reproducible
inputs, verification results, and this pack. Distinguish behavioural evidence
from source-text, snapshot, mutation, and patch-shape assertions; structural
checks cannot stand in for runtime lifecycle proof. Exclude prior findings,
triage, fix narratives, conclusions, and review hints.

## Output

Report the pack path, base and review SHAs, refreshed files, deterministic-check
status, and any blocker.
