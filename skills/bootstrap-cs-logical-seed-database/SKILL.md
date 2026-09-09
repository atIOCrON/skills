---
name: bootstrap-cs-logical-seed-database
description: Create a brand-new current-branch SQLite database in better-batt-sql-new by extracting only the authorized CS operational logical seed from an immutable backup. Use for local branch-schema database bootstraps; do not use for full restores, protected seed publication, baseline changes, or pipeline execution.
metadata:
  layer: runner
---

# Bootstrap CS Logical-Seed Database

Create a local `data/database.db` with the complete schema from the currently
checked-out branch and only the permitted operational seed data from the source
backup.

## Fixed paths

- Repository: `/Users/liammccarroll/Documents/Projects/better-batt-sql-new`
- Source backup: `data/backups/database full data download_mr828_cim_260825.db`
- Destination: `data/database.db`
- Canonical implementation: `scripts/codex/database_seed.py`

Resolve relative paths from the repository root. Do not reinterpret the backup
as a protected Codex seed release.

## Safety boundary

Before any mutation:

1. Read `AGENTS.md` completely and read the relevant files in `docs/`, including
   the database migration policy. Treat repository policy and the checked-out
   implementation as authoritative if they have evolved since this skill was
   written.
2. Record `git status --short`. Preserve every unrelated worktree change.
3. Require the source to be an existing regular SQLite database. Open it through
   `database_seed._read_only_connection()` or an equivalent `mode=ro` URI with
   `PRAGMA query_only = ON`. Never open it through a writable connection and
   never modify, move, checkpoint, vacuum, or replace it.
4. Require `data/database.db` not to exist. If it exists in any form, stop and
   report that no work was published. Never unlink or overwrite it. Repeat this
   check immediately before publication so a concurrent creator cannot be
   clobbered.

Create all intermediate databases in a temporary directory on the same
filesystem as `data/database.db`, close every SQLite connection before
publication, and remove temporary artifacts on success or failure.

## Allowed logical seed

The only tables whose rows may be preserved are the current
`database_seed.DATABASE_SEED_TABLES` allowlist, which must resolve to exactly:

- `ops_pipeline_runs`
- `ops_pipeline_supplier_source_runs`
- `raw_ext_product_pages_cs`
- `ops_image_source_identities`

Use the checked-out `database_seed` capture logic rather than rebuilding its SQL
by hand:

- `database_seed._validate_cs_source_lineage(..., require_current_view=False)`
  selects the exact authoritative current completed `SUCCESS` CS `product` run
  and its snapshot.
- `database_seed._capture_tables()` applies the selected run/snapshot filters,
  includes the exact pipeline-run and supplier-source-run parents, preserves the
  allowed image-source identities, and applies
  `PIPELINE_RUN_SEED_EXCLUDED_COLUMNS` to `ops_pipeline_runs`.
- The `TableSnapshot` results are the logical seed manifest: preserve their
  projected columns, row counts, stable ordering, and content hashes.

Stop if the runtime allowlist differs from the four tables above. This task does
not authorize silently expanding the preserved data surface.

## Workflow

1. Open the source read-only and hold a read transaction while validating and
   extracting. Require:

   - `PRAGMA quick_check` returns exactly `ok`.
   - `PRAGMA foreign_key_check` returns no rows.
   - `_validate_cs_source_lineage()` passes with `require_current_view=False`.

2. Create an ephemeral logical-seed artifact containing only the four allowlisted
   tables. Use `_capture_tables()` so its current filters, excluded-column
   handling, batching, stable ordering, and content hashes are retained. Do not
   use `build_publication_candidate()`: its settings, imports, image-file, and
   release concerns are outside this task.

3. Validate the logical-seed artifact before loading it. Require its application
   table inventory to equal the four-table allowlist, `quick_check` to return
   `ok`, `foreign_key_check` to return no rows, CS lineage validation to pass,
   and every projected row count and content hash to match its `TableSnapshot`.

4. Create a separate temporary destination database by calling exactly:

   ```python
   scripts.codex.database_seed.initialize_current_schema(temporary_database)
   ```

   The destination file must be new. Capture the initialized schema object and
   application-table inventory before importing rows. Do not create a schema by
   copying the backup and do not hand-maintain DDL.

5. Load the logical seed with the current `_load_seed_rows()` behavior. Prefer
   calling `_load_seed_rows()` directly by supplying an in-memory release-like
   object whose `artifact`, `manifest`, and `manifest_file` describe the
   temporary four-table logical artifact. Its logical manifest can be built from
   `TableSnapshot.logical_payload()` results; do not create or publish a release
   tree. If the helper interface has changed, adapt the local one-off bootstrap
   to preserve all of these invariants:

   - Attach the seed artifact using a read-only SQLite URI.
   - Require every preserved destination table to be empty before import.
   - Import only columns shared by the logical seed and current schema.
   - Allow destination-only columns only when nullable or populated by a usable
     default.
   - Fail when a destination-only column is a primary key or is `NOT NULL`
     without a default.
   - Record destination-only defaulted/nullable columns, ignored source-only
     columns, and imported columns for every preserved table.
   - Compare source and destination projected row counts and content hashes
     using the logical seed's stable ordering.
   - Require all non-seed application tables to remain empty.
   - Require `foreign_key_check` to return no rows, `quick_check` to return `ok`,
     and `_validate_cs_source_lineage(..., require_current_view=True)` to pass
     against the current schema and authoritative view.

6. Reopen the completed temporary destination read-only and independently
   verify:

   - Its schema object and table inventory still match the schema initialized by
     `initialize_current_schema()`.
   - Each preserved table's imported count and projected hash match the logical
     seed over the imported shared columns.
   - Every application table outside the four-table allowlist has zero rows.
   - `PRAGMA quick_check` returns `ok`.
   - `PRAGMA foreign_key_check` returns no rows.
   - Current-schema CS authoritative-source-lineage validation passes with the
     authoritative view required.

7. Publish only after all verification succeeds. Use a no-clobber atomic
   publication on the destination filesystem, such as creating
   `data/database.db` with `os.link(temporary_database, destination)` and then
   unlinking the temporary name. The operation must fail if the destination was
   created concurrently; never use an overwrite-capable replacement without a
   no-existence guarantee.

## Prohibited actions

Do not:

- Copy or restore all source tables, including the full 185-table backup.
- Call protected seed publication or promotion workflows.
- Change a protected baseline lock.
- Copy settings, imports, exports, source images, or materialized images.
- Run the application pipeline.
- Modify tracked repository files for this bootstrap.
- Commit, stage, reset, clean, or otherwise alter Git state.

Use a transient Python invocation or a file outside the repository for any
orchestration code. Do not leave a bootstrap helper in the worktree.

## Report

Report the outcome and exact evidence:

- Selected authoritative CS `pipeline_run_sk` and `snapshot_at`.
- Imported row count for each of the four allowlisted tables.
- Per-table schema evolution: defaulted/nullable destination columns, ignored
  source columns, and imported columns. State `none` explicitly for empty
  categories.
- Logical-seed versus destination projected content-hash match for every table.
- Source, logical-artifact, and final-database `quick_check` results.
- Source, logical-artifact, and final-database `foreign_key_check` results.
- Final current-view authoritative CS lineage result.
- Confirmation that every non-seed application table is empty.
- Final `data/database.db` byte size and human-readable size.
- Final `git status --short`, distinguishing pre-existing unrelated changes.

If any check fails, do not publish the destination. Report the failed invariant
and confirm whether temporary artifacts were removed and the source remained
unchanged.
