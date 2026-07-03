---
name: sync-settings-sheets
description: Download the configured Google Drive folder of 21 native Google Sheets as CSV and overwrite the matching existing files in data/settings. Use when asked to refresh, sync, or replace repo settings CSVs from the Drive settings Sheets folder.
metadata:
  layer: runner
---

# Sync Settings Sheets

Use the Google Drive plugin for all Drive access. Do not use browser download
flows or ad hoc public URLs. Connector `download_url` values are short-lived:
consume them immediately or do not use them at all.

## Constants

- Folder URL: `https://drive.google.com/drive/u/0/folders/1sMJg_WUddX5XC0h8WpaxjcTV73Ha0g9c`
- Target directory: `data/settings`
- Expected item count: `21`
- Expected Drive MIME type: `application/vnd.google-apps.spreadsheet`
- CSV export MIME type: `text/csv`

Each Sheet title must map to an existing target file named
`data/settings/<title>.csv`.

## Workflow

1. Check local state before touching files:

```bash
git status --short
find data/settings -maxdepth 1 -type f -name '*.csv' -print | sort
```

Note unrelated dirty files and leave them alone. `data/` is Git-ignored, so do
not rely on Git status or Git diff to detect settings CSV changes.

2. List the Drive folder with
`mcp__codex_apps__google_drive._list_folder`:

```json
{
  "url": "https://drive.google.com/drive/u/0/folders/1sMJg_WUddX5XC0h8WpaxjcTV73Ha0g9c",
  "top_k": 50
}
```

Stop before overwriting anything unless the folder contains exactly 21 files,
every file is a native Google Sheet, every title is unique, and every
`data/settings/<title>.csv` already exists.

3. Export each file as CSV. Prefer
`mcp__codex_apps__google_drive._fetch` because it returns `b64_string` and
`file_name` fields that preserve bytes cleanly:

```json
{
  "url": "<sheet url from list_folder>",
  "download_raw_file": true,
  "raw_export_mime_type": "text/csv"
}
```

`mcp__codex_apps__google_drive._export_file` with `mime_type: "text/csv"` is an
acceptable fallback; the writer also accepts its `content` result.

Do not cache or batch connector `download_url` values. If a connector result
includes `b64_string`, write that payload to the JSONL record. If it only
includes `download_url`, immediately download that one file into `/tmp` with
`curl -fL`, verify the command exits 0, and only then create a JSONL record that
points at the downloaded local file with `payload_path`.

4. Build a two-phase sync workspace outside the repo. Download or export all 21
CSVs into `/tmp`, then validate them before overwriting `data/settings`.

Use strict shell settings for any local download step:

```bash
set -euo pipefail
tmp_dir="$(mktemp -d /tmp/settings-sheet-exports.XXXXXX)"
jsonl="${tmp_dir}/settings_sheet_exports.jsonl"
```

For connector results with only a volatile `download_url`, download
immediately:

```bash
set -euo pipefail
curl -fL "$download_url" -o "${tmp_dir}/${title}.csv"
test -s "${tmp_dir}/${title}.csv"
```

Avoid shell loops or command pipelines that continue after `curl` errors.

5. Put the 21 durable export records into a temporary JSONL or JSON array file,
one complete connector response per record. Keep this file outside the repo,
for example `${tmp_dir}/settings_sheet_exports.jsonl`. Each record must contain
one of:

- `b64_string`
- `content`
- `payload_path` pointing at an already-downloaded local CSV file

Do not write records that contain only `download_url`.

6. Validate without overwriting:

```bash
python .agents/skills/sync-settings-sheets/scripts/write_csv_exports.py \
  --input "${jsonl}" \
  --target-dir data/settings \
  --expected-count 21 \
  --dry-run
```

Validation must pass before any overwrite:

- exactly 21 exports
- every filename matches an existing `data/settings/<title>.csv`
- no zero-byte payloads
- every file parses as CSV
- every file has a non-empty header row
- every exported header exactly matches the current target header

7. Overwrite the CSVs with the bundled writer:

```bash
python .agents/skills/sync-settings-sheets/scripts/write_csv_exports.py \
  --input "${jsonl}" \
  --target-dir data/settings \
  --expected-count 21
```

The writer decodes connector results, validates payloads and filenames, writes
files atomically, and refuses new/unmatched target files by default.

8. Verify and report:

```bash
find data/settings -maxdepth 1 -type f -name '*.csv' -print | sort | wc -l
find data/settings -maxdepth 1 -type f -name '*.csv' -exec wc -l {} +
```

Use the writer output to report which ignored CSV files changed versus remained
byte-identical. Report the number of CSVs overwritten, the target directory,
and any files that changed. If the connector folder or local file set does not
match the expected 21-file contract, report the mismatch and do not overwrite
files.
