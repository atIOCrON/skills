---
name: full-pipeline-export-test
description: 'Run the full Docker pipeline export test: reset from the latest Cameron Sino full-scrape seed database, run the pipeline with ingest and skip-checkpoint, and compare the new export CSV batch to the previous batch via export-batch-compare. Use when the user asks to test staged or current changes by running the full pipeline. To compare existing export batches without running the pipeline, use export-batch-compare instead.'
compatibility: Requires Docker, docker compose, and a Cameron Sino full-scrape seed database under data/
metadata:
  layer: runner
---

# Full Pipeline Export Test

Do not edit code, stage files, commit, or clean unrelated workspace changes.

## Workflow

From repo root:

```bash
git status --short

baseline_batch=$(find data/exports -type f -name '*.csv' -print \
  | sed -E 's/.*_([0-9]{8}_[0-9]{6})(_[0-9]+)?\.csv/\1/' \
  | sort | tail -1)

.agents/project-skills/full-pipeline-export-test/scripts/reset_seed_db.sh

docker compose down
docker compose up -d
docker compose logs --tail=80 app

docker compose exec app python -m src.cli.main run-pipeline --skip-checkpoint --include-ingest
```

The pipeline must exit 0 and report a `PIPELINE COMPLETE` line.

Capture the new export batch timestamp:

```bash
new_batch=$(find data/exports -type f -name '*.csv' -print \
  | sed -E 's/.*_([0-9]{8}_[0-9]{6})(_[0-9]+)?\.csv/\1/' \
  | sort | tail -1)
```

Then delegate the comparison to
`.agents/project-skills/export-batch-compare/SKILL.md` with `$baseline_batch` as the
baseline batch timestamp and `$new_batch` as the new batch timestamp.

## Report

Include:

- Seed DB copied.
- Pipeline exit status and duration if available.
- New export batch timestamp.
- Line counts by CSV.
- Whether each CSV is byte-identical or differs from baseline.
- Docker container status.

When any CSV differs, list the differing stems and instruct the operator to
inspect them before treating the run as a pass.
