# Code Review Pack

Build a neutral, commit-pinned pack at
`plans/<plan_slug>.reviews/code-review-pack/`. Every fresh reviewer in a pass
uses the same immutable review boundary.

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

`index.md` records the plan, stack-parent branch and pinned base SHA, plan branch,
review commit and tree SHAs, creation time, draft MR, and evidence paths.
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
- pinned base and current MR target SHA equality;
- local, upstream, MR source, reviewed, and verified SHA equality;
- clean-worktree verification evidence for `<review-sha>`;
- file identity, strict patch application, and byte comparison where required.

A failed check, unexplained delta, or SHA mismatch blocks review.

## Refresh Policy

Build the pack before pass 1. After a fix commit or restack, refresh the commit,
diff, hashes, deterministic results, and verification evidence. Do not rebuild
an unchanged vendor baseline.

Fresh reviewers receive only the pinned diff, approved plan, repository
standards, reproducible inputs, verification results, and this pack. Exclude
prior findings, triage, fix narratives, conclusions, and review hints.

## Output

Report the pack path, base and review SHAs, refreshed files, deterministic-check
status, and any blocker.
