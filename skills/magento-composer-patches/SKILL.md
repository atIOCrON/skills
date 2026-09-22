---
name: magento-composer-patches
description: Create or revise Composer-managed Magento 2 vendor patches, including patch ownership, ordering, deterministic regeneration, strict replay, and effective-result verification. Excludes Magento setup data and schema patches.
disable-model-invocation: false
metadata:
  layer: capability
---

# Magento Composer Patches

Use this capability for Composer-managed modifications to locked Magento 2
packages. Repository policy is authoritative. If `docs/composer-patches.md`
exists, read it before editing and use its categories, paths, strip levels,
registration order, and branch landing order.

## Classify Ownership Before Editing

Inspect the locked package, registered patches, their exact application order,
and the effective installed code. Distinguish:

- a defect in the pristine locked package;
- a defect introduced by an existing project patch;
- a project-specific customization; and
- an integration that depends on other project code or data.

Compare the package's supported Magento plugin, observer or event, layout/XML
extension, project module or adapter, package upgrade, and upstream correction
before choosing a Composer patch. Repository policy decides which mechanisms
are supported. A patch is appropriate for a narrow locked-package defect or
authorized customization; clean mechanics do not make broad local ownership
proportionate.

Stop for architecture approval before a permanent dependency modification
that lacks a supported extension point, replaces a substantial dependency-owned
surface, coordinates providers, introduces shared mutable browser state or a
retry/recovery framework, or makes the project own an upstream subsystem.

## Patch Ownership and Order

Keep original-package bug fixes standalone and first. Each must apply to the
pristine locked package without project customizations or another local patch
and remain suitable for upstream reporting. Put independently applicable,
vendor-neutral changes before project integrations unless repository policy
says otherwise.

Revise the existing patch that owns a concern. Do not add a follow-up patch
merely to correct or extend it. Create a new patch only for a distinct defect or
customization, and never combine independently testable defects merely because
they touch one package. If one patch mixes an upstream defect with project
customization, extract the upstream fix on its owning branch, then rebase and
regenerate the customization on top.

Stack overlapping same-package branches in final patch order. A branch changes
only the patches it owns. Earlier patches must be finalized before dependent
later patches are regenerated. Intermediate branches with stale later patches
are review layers and must not be promoted independently.

Use these baselines:

- an original-package bug fix: the pristine locked package;
- a customization: the locked package with every preceding registered patch;
- a revised patch: the correct baseline without that patch's old output.

Temporary edits inside `vendor/` may help author a patch, but they are never the
deliverable. Preserve locked versions and references unless an upgrade is
authorized. Exclude formatting churn, generated files, and local configuration.

## Verification Phases

### Authoring

Work against the correct baseline and run the smallest fast checks that expose
syntax, patch shape, and the targeted behavior. A validated immutable baseline
or patch-prefix cache may be reused. Regenerate only the patch currently owned;
do not repair unrebased later patches in the same branch.

### Candidate

Regenerate the owned patch from the correct pristine or preceding-prefix tree.
Start from the longest validated cached prefix whose locked package, patch
bytes and order, strip level, replay tool, and relevant configuration are
unchanged. Replay from the first changed or added patch through the end of the
candidate's in-scope suffix. If only the final patch was removed, the validated
preceding-prefix result is the candidate result; record its identity without
replaying it. A locked package, strip level, replay tool, or relevant
configuration change invalidates every prefix. Patch byte or order changes
invalidate the changed boundary and its suffix. Replay each required suffix
patch with:

```bash
scripts/strict_patch_replay.sh <tree> <patch-file> <log-file> <strip-level>
```

The script requires GNU patch, sets `--fuzz=0`, rejects reported fuzz or
offsets, and preserves raw output in the named log. A zero exit from another
patch command is not equivalent evidence.

Record the locked package version or archive hash, lock evidence, pristine or
prefix tree identity, ordered patch identities, strip level, GNU patch identity,
strict replay logs, and effective result tree identity. Compare the resulting
code byte-for-byte where repository policy requires it. Review and test both
the patch source and the effective resulting code. Run syntax and focused
behavioral tests. For lifecycle changes, exercise state transitions,
cancellation, retries, current-value changes, and replacement at the highest
practical local seam; source-shape checks remain supplementary.

### Integration

A per-slice candidate, publication tip, or review SHA is not the final
integration tip. Do not run complete-sequence replay during candidate
publication or review.

At the final integration tip, reconstruct the pristine locked package and
strictly replay the complete registered patch sequence in order. Verify the
effective full tree and run combined syntax, build, and behavioral regression
checks before deployment or promotion. Keep unavailable real-provider checks
as explicit external acceptance rather than substituting structural evidence.

## Immutable Prefix Cache

Use `scripts/prepare_patch_prefix_cache.py` when repeated authoring or review
would otherwise reconstruct the same pristine package and ordered patch prefix:

```bash
python scripts/prepare_patch_prefix_cache.py \
  --pristine-tree <tree> \
  --cache-root <cache-directory> \
  --strip-level <n> \
  --patch <first.patch> \
  --patch <second.patch>
```

The cache key covers the pristine tree contents, patch bytes and order, strip
level, strict-replay script, and GNU patch identity. A hit is valid only when
the manifest inputs and cached output tree hash still match. Any changed input
produces a different key. A corrupted entry blocks reuse and is never silently
overwritten. Keep the cache outside versioned review artefacts; link its
manifest and relevant logs from the review evidence.

## Patch-Pressure Report

When deciding whether an accumulating patch set should become a maintained fork
or a different extension, report repository-derived evidence rather than a
fixed threshold. Include package and locked version, patch count and order,
changed lines or bytes, overlap between patches, upstream churn or divergence,
strict replay failures or offsets, available supported extension points, and
the observed regeneration and regression-test burden. Treat the report as an
architecture input, not automatic authorization to fork.

## Upstream Report

For an original-package fix, provide the affected package and locked version, a
concise defect description, reproduction steps or a regression test, expected
and actual behavior, the standalone patch, and verification results. State any
limitations. Preparing this material does not submit it upstream.

## Output

Report the ownership classification, changed patches, why each new patch was
needed, final application and branch landing order, cache identity when used,
authoring checks, candidate replay and effective-result verification,
integration-sequence verification, patch-pressure conclusion when applicable,
and any external acceptance still pending.
