#!/usr/bin/env bash
# Validate a code review and repair its format in the original session.
set -euo pipefail

if [ "$#" -lt 4 ] || [ "$#" -gt 5 ]; then
  echo "usage: repair_code_review_output.sh <codex|claude|cursor> <artifact-dir> <repo-root> <pass-number> [repair-envelope]" >&2
  exit 2
fi

provider="$1"
artifact_dir="$2"
repo_root="$3"
pass_number="$4"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
validator="$script_dir/validate_code_review_output.py"
review_prompt="$artifact_dir/$provider-prompt.md"
review_sha=""

case "$provider" in codex|claude|cursor) ;; *) echo "error: unsupported provider: $provider" >&2; exit 2 ;; esac
case "$pass_number" in ''|*[!0-9]*) echo "error: pass-number must be numeric" >&2; exit 2 ;; esac

if [ "$#" -eq 5 ]; then
  repair_envelope="$5"
elif [ -f "$script_dir/../code-review-format-repair-invocation.md" ]; then
  repair_envelope="$script_dir/../code-review-format-repair-invocation.md"
else
  repair_envelope="$script_dir/../references/code-review-format-repair-invocation.md"
fi

test -s "$repair_envelope" || { echo "error: repair envelope missing or empty: $repair_envelope" >&2; exit 2; }
test -d "$artifact_dir" || { echo "error: artifact directory not found: $artifact_dir" >&2; exit 2; }
test -d "$repo_root" || { echo "error: repo-root is not a directory: $repo_root" >&2; exit 2; }
if [ -f "$review_prompt" ]; then
  review_sha="$(sed -nE 's/^Review commit SHA: ([0-9a-f]{40})$/\1/p' "$review_prompt" | head -n 1)"
fi

canonical="$artifact_dir/$provider.md"
session_file="$artifact_dir/$provider-session.md"

latest_attempt=0
raw=""
for candidate in "$artifact_dir/$provider-raw-attempt"*.md; do
  [ -e "$candidate" ] || continue
  suffix="${candidate##*raw-attempt}"
  suffix="${suffix%.md}"
  case "$suffix" in ''|*[!0-9]*) continue ;; esac
  if [ "$suffix" -gt "$latest_attempt" ]; then
    latest_attempt="$suffix"
    raw="$candidate"
  fi
done

if [ -e "$canonical" ]; then
  if [ -z "$raw" ]; then
    raw="$artifact_dir/$provider-raw-attempt1.md"
    cp "$canonical" "$raw"
  fi
elif [ -z "$raw" ]; then
  raw="$artifact_dir/$provider-raw-attempt1.md"
  : > "$raw"
fi
rm -f "$canonical"

validate_candidate() {
  local candidate="$1"
  local validation_file="$2"
  local -a validator_args
  set +e
  validator_args=("$candidate" "$provider" "$pass_number")
  [ -z "$review_sha" ] || validator_args+=("$review_sha")
  python3 "$validator" "${validator_args[@]}" > "$validation_file"
  validation_status=$?
  set -e
}

validate_candidate "$raw" "${raw%.md}-validation.md"
if [ "$validation_status" -eq 0 ]; then
  cp "$raw" "$canonical"
  exit 0
fi

if [ "$validation_status" -eq 12 ] && [ -s "$raw" ]; then
  exit 12
fi

session_id=""
if [ -f "$session_file" ]; then
  session_id="$(sed -nE 's/^- (session_id|chat_id): (.*)$/\2/p' "$session_file" | head -n 1)"
fi
if [ -z "$session_id" ] || [ "$session_id" = "unavailable" ]; then
  exit 12
fi

for round in 1 2 3; do
  label="format-repair-round$round"
  prompt="$artifact_dir/$provider-$label-prompt.md"
  cp "$repair_envelope" "$prompt"

  set +e
  "$script_dir/resume_review.sh" "$provider" "$prompt" "$artifact_dir" "$repo_root" "$label"
  resume_status=$?
  set -e
  candidate="$artifact_dir/$provider-$label.md"
  validation_file="$artifact_dir/$provider-$label-validation.md"

  if [ "$resume_status" -ne 0 ]; then
    continue
  fi
  validate_candidate "$candidate" "$validation_file"
  if [ "$validation_status" -eq 0 ]; then
    cp "$candidate" "$canonical"
    exit 0
  fi
  if [ "$validation_status" -eq 12 ] && [ -s "$candidate" ]; then
    break
  fi
done

exit 12
