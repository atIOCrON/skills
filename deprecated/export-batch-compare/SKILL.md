---
name: export-batch-compare
description: Compare two export CSV batches in data/exports by line counts, sha256 sums, and per-stem byte identity, deriving the stem list from the baseline batch. Use when asked how the latest export batch differs from the previous one or to compare two specific export batches. Read-only; does not run the pipeline or modify the database.
metadata:
  layer: capability
---

# Export Batch Compare

Compare two export CSV batches. Read-only: do not run the pipeline, modify
the database, edit files, or stage anything.

## Inputs

- Baseline and new batch timestamps in `YYYYMMDD_HHMMSS` format.
- When not supplied, default to the two most recent batch timestamps found in
  `data/exports`:

```bash
find data/exports -type f -name '*.csv' -print \
  | sed -E 's/.*_([0-9]{8}_[0-9]{6})(_[0-9]+)?\.csv/\1/' \
  | sort -u | tail -2
```

The first (older) timestamp is the baseline batch; the second (newer) is the
new batch. Fail with a clear message when `data/exports` contains fewer than
two batch timestamps and none were supplied; the script also refuses
identical baseline/new timestamps.

## Workflow

From the repo root:

```bash
.agents/project-skills/export-batch-compare/scripts/compare_export_batches.sh <baseline-batch> <new-batch> data/exports
```

The script derives the CSV stem list dynamically from the files present in
the baseline batch and compares both batches.

## Report

- Line counts per CSV for both batches.
- `IDENTICAL` or `DIFFERS` per stem.
- `ONLY-IN-BASELINE` / `ONLY-IN-NEW` for stems present in one batch only.
- The sha256 listing.
