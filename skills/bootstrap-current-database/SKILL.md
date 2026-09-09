---
name: bootstrap-current-database
description: Build a fresh local SQLite database with the current repository schema and logical seed rows extracted from an operational backup.
metadata:
  layer: runner
---

# Bootstrap

Inputs: source backup and destination path.

1. Refuse if `os.path.lexists(destination)`.
2. Record the source stat identity and SHA-256. Reject SQLite sidecars.
3. Open the source with `database_seed._read_only_connection()`.
4. Require:
   - `PRAGMA quick_check` = `ok`
   - empty `PRAGMA foreign_key_check`
   - `_validate_cs_source_lineage(..., require_current_view=False)` passes
5. Create a temporary sibling directory.
6. Build a logical seed artifact with `_capture_tables()`. This applies the repository’s current table allowlist, row filters, lineage selection, and column exclusions.
7. Build a release-like object containing:
   - the artifact path
   - `database.logical.tables` from each `TableSnapshot.logical_payload()`
   - a placeholder manifest path
8. Create the temporary destination with `initialize_current_schema()`.
9. Confirm every application table is empty and record the schema inventory hash.
10. Import with `_load_seed_rows(temporary_destination, release_like)`.
11. Verify:
    - snapshot counts and full hashes match the seed artifact
    - imported-column counts and projected hashes match between seed and destination
    - schema inventory hash is unchanged
    - `quick_check` is `ok`
    - `foreign_key_check` is empty
    - `_validate_cs_source_lineage(..., require_current_view=True)` passes
    - no non-seed application table contains rows
    - no SQLite sidecars remain
    - source stat identity and SHA-256 are unchanged
12. Close all connections.
13. Publish without replacement using `os.link(temporary_destination, destination)`, then `fsync` the parent directory and remove the temporary directory.
14. Repeat destination integrity and lineage checks.

On failure, remove temporary files and leave the destination absent.

Report seed-table row counts and hashes, schema evolution returned by `_load_seed_rows()`, integrity results, lineage identity, final size and SHA-256, and Git status.
