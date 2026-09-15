# Code Review Pack

Build one neutral evidence pack at
`plans/<plan_slug>.reviews/code-review-pack/`. All fresh reviewers in a pass use
the same pack instead of reconstructing deterministic facts.

## Contents

Create or refresh:

```text
index.md
staged-files.txt
staged-stat.txt
staged.diff
ownership-map.md
verification-summary.md
deterministic-checks.md
hash-manifest.sha256
```

`index.md` records the plan, repository commit, staged-tree hash, creation time,
and paths to the pack files and verification evidence. `ownership-map.md` maps
each staged path to its plan scope or owner. Capture command, exit status, and
literal output for deterministic checks.

For Composer patches or other vendor-derived changes, also record:

- the exact package version, source reference or archive hash, and lockfile
  evidence;
- paths to pristine before and strictly patched after trees;
- complete before and after hash manifests;
- the strict apply command, exit status, and log, with fuzz and offsets
  disabled;
- any verbatim-output comparison required by the plan.

Keep large reconstructed trees outside review artefact folders and link their
absolute paths from `index.md`. A failed strict apply, offset, fuzz, unexpected
hash, or unexplained file delta blocks review.

## Deterministic Checks

Use Git and comparison tools—not reviewer inference—to establish:

- staged scope and patch bytes: `git diff --cached` and
  `git diff --cached --binary`;
- commit and ancestry: `git rev-parse` and `git merge-base --is-ancestor`;
- file and tree identity: SHA-256 manifests;
- verbatim equality: `cmp` or `diff --no-index`;
- patch applicability: the repository's strict dry-run/apply procedure with no
  fuzz or offsets.

Use the repository's documented commands when they are stricter.

## Refresh Policy

Build the pack before the first fresh pass. After a code fix or restack, refresh
only staged-state, hashes, deterministic results, and verification evidence
that changed; do not reconstruct an unchanged vendor baseline.

Fresh review prompts may receive only neutral inputs: the current staged diff,
approved plan, repository standards, exact vendor baseline, reproducible
commands, verification results, and this pack. Exclude prior findings, triage,
fix narratives, reviewer conclusions, and hints about difficult areas.

## Output

Report the pack path, staged-tree hash, refreshed files, deterministic check
status, and any blocker.
