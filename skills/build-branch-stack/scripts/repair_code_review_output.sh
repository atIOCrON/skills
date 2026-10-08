#!/usr/bin/env bash
# Preserve a review and repair presentation locally. Never contact a reviewer.
set -euo pipefail

if [ "$#" -ne 4 ] && [ "$#" -ne 6 ]; then
  echo "usage: repair_code_review_output.sh <codex|claude|cursor> <artifact-dir> <repo-root> <pass-number> [--coordinator-assessment <json>]" >&2
  exit 2
fi
provider="$1"
artifact_dir="$2"
repo_root="$3"
pass_number="$4"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
case "$provider" in codex|claude|cursor) ;; *) echo "error: unsupported provider" >&2; exit 2 ;; esac
case "$pass_number" in ''|*[!0-9]*|0) echo "error: pass-number must be positive" >&2; exit 2 ;; esac
assessment=""
if [ "$#" -eq 6 ]; then
  [ "$5" = "--coordinator-assessment" ] || { echo "error: unknown option: $5" >&2; exit 2; }
  assessment="$6"
fi
test -d "$artifact_dir" && test -d "$repo_root" || { echo "error: missing artifact directory or repo root" >&2; exit 2; }

canonical="$artifact_dir/$provider.md"
raw=""
latest_attempt=0
for candidate in "$artifact_dir/$provider-raw-attempt"*.md; do
  [ -e "$candidate" ] || continue
  suffix="${candidate##*raw-attempt}"
  suffix="${suffix%.md}"
  case "$suffix" in ''|*[!0-9]*) continue ;; esac
  if [ "$suffix" -gt "$latest_attempt" ]; then latest_attempt="$suffix"; raw="$candidate"; fi
done
if [ -z "$raw" ]; then
  raw="$artifact_dir/$provider-raw-attempt1.md"
  if [ -f "$canonical" ]; then cp "$canonical" "$raw"; else : > "$raw"; fi
fi
# Existing canonical evidence remains intact until a new candidate is accepted.
review_sha=""
review_prompt="$artifact_dir/$provider-prompt.md"
if [ -f "$review_prompt" ]; then
  review_sha="$(sed -nE 's/^Review commit SHA: ([0-9a-f]{40})$/\1/p' "$review_prompt" | head -n 1)"
fi
if [ -z "$review_sha" ]; then
  echo "coordinator attention required: establish the pinned review commit from saved scope/session evidence"
  exit 11
fi
round=1
while [ -e "${raw%.md}-normalization-round$round.md" ] ||
      [ -e "${raw%.md}-normalization-round$round.json" ] ||
      [ -e "${raw%.md}-normalization-round$round-validation.md" ]; do
  round=$((round + 1))
done
normalized="${raw%.md}-normalization-round$round.md"
mapping="${normalized%.md}.json"
normalization_args=("$raw" "$normalized" "$mapping" "$provider" "$pass_number" "$review_sha")
[ -z "$assessment" ] || normalization_args+=(--assessment "$assessment")
set +e
python3 "$script_dir/normalize_code_review_output.py" "${normalization_args[@]}" > "${normalized%.md}-validation.md"
status=$?
set -e
if [ "$status" -eq 0 ] && [ -s "$normalized" ] && [ -s "$mapping" ]; then
  cp "$normalized" "$canonical"
  exit 0
fi
cat "${normalized%.md}-validation.md"
# 10/11 are coordinator work requests, not retry authorization or a triage gate.
# 12 means no usable review; recover content/transport before declaring completion.
exit "$status"
