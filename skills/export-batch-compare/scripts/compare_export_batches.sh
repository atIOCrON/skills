#!/usr/bin/env bash
# Compare two export CSV batches by line counts, sha256 sums, and per-stem
# byte identity. The CSV stem list is derived dynamically from the files
# present in the baseline batch; stems present in only one batch are
# reported as ONLY-IN-BASELINE or ONLY-IN-NEW. Read-only.
# Usage: compare_export_batches.sh <baseline-batch> <new-batch> [exports-dir]
# Batch format: YYYYMMDD_HHMMSS. exports-dir defaults to the current
# directory.
# Exit codes: 2 = usage, 3 = exports dir missing, 4 = no CSVs for a batch,
# 5 = baseline and new batch timestamps are identical.
set -euo pipefail

if [ "$#" -lt 2 ] || [ "$#" -gt 3 ]; then
  echo "usage: compare_export_batches.sh <baseline-batch> <new-batch> [exports-dir]" >&2
  exit 2
fi

baseline="$1"
new="$2"
exports_dir="${3:-.}"

if [ "$baseline" = "$new" ]; then
  echo "error: baseline and new batch timestamps are identical ($baseline); nothing to compare" >&2
  exit 5
fi

if [ ! -d "$exports_dir" ]; then
  echo "error: exports directory not found: $exports_dir" >&2
  exit 3
fi

list_stems() {
  find "$exports_dir" -type f -name "*_${1}*.csv" -print \
    | sed -E "s|.*/||; s|_${1}(_[0-9]+)?\.csv$||" | sort -u
}

baseline_stems="$(list_stems "$baseline")"
new_stems="$(list_stems "$new")"

if [ -z "$baseline_stems" ]; then
  echo "error: no CSVs found for baseline batch $baseline in $exports_dir" >&2
  exit 4
fi
if [ -z "$new_stems" ]; then
  echo "error: no CSVs found for new batch $new in $exports_dir" >&2
  exit 4
fi

echo "== line counts: baseline batch $baseline =="
find "$exports_dir" -type f -name "*_${baseline}*.csv" -print | sort | xargs wc -l

echo "== line counts: new batch $new =="
find "$exports_dir" -type f -name "*_${new}*.csv" -print | sort | xargs wc -l

# All files for one stem in one batch: the unchunked file and/or the
# `_<N>` chunk files the exporter writes when a view exceeds the CSV row cap.
files_for_stem() {
  find "$exports_dir" -type f \
    \( -name "${1}_${2}.csv" -o -name "${1}_${2}_[0-9]*.csv" \) -print | sort
}

echo "== per-stem comparison =="
all_stems="$(printf '%s\n%s\n' "$baseline_stems" "$new_stems" | sort -u)"
for stem in $all_stems; do
  old_files="$(files_for_stem "$stem" "$baseline")"
  new_files="$(files_for_stem "$stem" "$new")"
  if [ -n "$old_files" ] && [ -n "$new_files" ]; then
    if cmp -s \
      <(printf '%s\n' "$old_files" | tr '\n' '\0' | xargs -0 cat) \
      <(printf '%s\n' "$new_files" | tr '\n' '\0' | xargs -0 cat); then
      printf 'IDENTICAL %s\n' "$stem"
    else
      printf 'DIFFERS %s\n' "$stem"
    fi
  elif [ -n "$old_files" ]; then
    printf 'ONLY-IN-BASELINE %s\n' "$stem"
  else
    printf 'ONLY-IN-NEW %s\n' "$stem"
  fi
done

echo "== sha256 =="
find "$exports_dir" -type f \( -name "*_${baseline}*.csv" -o -name "*_${new}*.csv" \) -print \
  | sort | xargs shasum -a 256
