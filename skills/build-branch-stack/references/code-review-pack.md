# Code Review Pack

Build a neutral, commit-pinned pack at
`<feature_dir>/<plan_slug>.reviews/code-review-pack/`. Every fresh reviewer in
a pass uses the same immutable review boundary.

Record `review_mode` as `standard`, `behavior`, or `patch_mechanics` in
`index.md`. Use the same required files in every mode so pack validation and
resumption remain uniform.

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
identities that determine it. Keep large input or result trees outside the
pack and link them from `index.md`.

In `evidence-manifest.json`, record the review SHA and one entry per required
check: `id`, `kind` (`agent` or `external`), `required`, `last_run_sha` (full
commit SHA or `null`), `command`, `runtime`, `result` (`passed`, `failed`,
`pending`, or `blocked_by_environment`), `started_at`, `finished_at`,
`elapsed_seconds`, `cache_status` (`hit`, `miss`, or `not_applicable`),
`log_path`, and `log_sha256`. Use
`null` paths and hashes when no log exists. A result from an older SHA must
remain visible with its old `last_run_sha`; it cannot count as a passed required
agent check on the current SHA. Link each log from `verification-summary.md`.
Completed checks require timestamps and elapsed seconds; pending checks use
`null`. A cache hit links the reused evidence and its complete identity key.
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
and deterministic evidence from `index.md`. Retain every required review when equal
range diff or capability-defined semantic identity proves the parent-relative
logical change and effective result are unchanged. Record old-to-new SHA
mappings and the compared source, patch, generated-output and focused-behavior
identities. Require fresh review for unexplained differences or behavior
changes, not for conflict resolution or unequal range diff alone.

For specialized generated or dependency-derived changes, link the applicable
capability's candidate evidence and deterministic reproduction results. Record
the immutable inputs and their identities, the effective result identity, and
the exact capability command used. Link the representations; do not copy
complete generated trees into the pack or duplicate capability procedures.

For a Composer vendor patch, use two modes:

- `behavior`: lead with the baseline-to-effective source diff, relevant project
  runtime code, behavioral evidence, committed patch identity, and strict
  replay equality. Patch mechanics are present only as the identity proof and
  are not review scope.
- `patch_mechanics`: link the clean behavior-review evidence and approved
  effective-tree identity, then expose the final raw patch, correct baseline or
  prefix, registration, classification, order, strip/tool identities, strict
  logs, and equality result. Do not duplicate semantic review material.

Build the mechanics pack only after behavior review is clean. A mechanics-only
refresh retains that approval only while the effective-tree identity remains
equal.

## Deterministic Checks

Use explicit object IDs:

- scope and patch: `git diff <base-sha>...<review-sha>` and `--binary`;
- identity: `git rev-parse <review-sha>^{commit}` and `^{tree}`;
- ancestry: `git merge-base --is-ancestor <base-sha> <review-sha>`;
- pinned base and dependency-parent head equality;
- local branch tip, upstream, fetched remote tip, reviewed, and verified SHA
  equality;
- clean-worktree verification evidence for `<review-sha>`;
- source and effective-result identity plus capability-defined deterministic
  checks where required.

A failed check, unexplained delta, or SHA mismatch blocks review.

## Refresh Policy

Build the pack before pass 1. After a fix commit or restack, refresh the commit,
diff, hashes, deterministic results, and verification evidence. Preserve and
link every required prior clean review for a semantically identical restack;
otherwise run a fresh three-reviewer discovery pass. Reuse immutable inputs
only when the applicable capability proves their content, configuration, and
toolchain identity; never rebuild an unchanged proven input merely to refresh
the pack.
For evidence-only closure, keep the pinned diff and SHAs, refresh the evidence
links, manifest, hashes, and affected deterministic results, and record what
changed in the pack. Rerun the validator after each refresh.

Fresh reviewers receive only the phase-appropriate pinned diff, approved plan, parent
specification, slice map, design checkpoint, repository standards, reproducible
inputs, verification results, and this pack. Distinguish behavioural evidence
from source-text, snapshot, mutation, and generated-artifact assertions;
structural checks cannot stand in for runtime lifecycle proof. Exclude prior findings,
triage, fix narratives, conclusions, and review hints.

## Output

Report the pack path, base and review SHAs, refreshed files, deterministic-check
status, and any blocker.
