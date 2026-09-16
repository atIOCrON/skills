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
deterministic-checks.md
hash-manifest.sha256
```

`index.md` records the plan, dependency-parent branch and pinned base SHA,
plan branch, review commit and tree SHAs, creation time, and evidence paths.
It also records which standards sources were found. If `AGENTS.md` is absent,
say so and identify the applicable plan, repository docs and configuration,
affected contracts, tests, and nearby patterns used for review. General
engineering practice may inform a finding but is not a binding repository rule.
`ownership-map.md` maps each changed path to plan scope or owner. Capture each
deterministic command, exit status, and literal output.

After a restack, link its old/new ranges, `range-diff`, delta classifications,
and deterministic evidence from `index.md`.

For vendor-derived changes, also record the exact package version or archive
hash, lockfile evidence, pristine and patched trees, complete hash manifests,
strict apply results without fuzz or offsets, and required byte comparisons.
Keep large trees outside review artefacts and link them from `index.md`.

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
diff, hashes, deterministic results, and verification evidence. Do not rebuild
an unchanged vendor baseline.
For evidence-only closure, keep the pinned diff and SHAs, refresh the evidence
links and affected deterministic results, and record what changed in the pack.

Fresh reviewers receive only the pinned diff, approved plan, repository
standards, reproducible inputs, verification results, and this pack. Exclude
prior findings, triage, fix narratives, conclusions, and review hints.

## Output

Report the pack path, base and review SHAs, refreshed files, deterministic-check
status, and any blocker.
