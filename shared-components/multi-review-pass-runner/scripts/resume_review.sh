#!/usr/bin/env bash
# Resume a provider's original review session for closure.
set -euo pipefail

if [ "$#" -ne 4 ]; then
  echo "usage: resume_review.sh <codex|claude|cursor> <prompt-file> <artifact-dir> <repo-root>" >&2
  exit 2
fi

provider="$1"
prompt_file="$2"
artifact_dir="$3"
repo_root="$4"
session_file="$artifact_dir/$provider-session.md"
output_file="$artifact_dir/$provider-closure.md"
stderr_file="$artifact_dir/$provider-closure-stderr.log"
exit_code_file="$artifact_dir/$provider-closure-exit-code"
events_file="$artifact_dir/$provider-closure-events.jsonl"

test -s "$prompt_file" || { echo "error: closure prompt missing or empty: $prompt_file" >&2; exit 2; }
test -f "$session_file" || { echo "error: session artifact not found: $session_file" >&2; exit 2; }
test -d "$repo_root" || { echo "error: repo-root is not a directory: $repo_root" >&2; exit 2; }

session_id="$(sed -nE 's/^- (session_id|chat_id): (.*)$/\2/p' "$session_file" | head -n 1)"
test -n "$session_id" && test "$session_id" != "unavailable" || { echo "error: resumable session id not found" >&2; exit 2; }

: > "$output_file"
: > "$stderr_file"
: > "$events_file"
attempt=1
max_attempts=2
final_exit_code=1

while [ "$attempt" -le "$max_attempts" ]; do
  : > "$output_file"
  case "$provider" in
    codex)
      command -v codex >/dev/null 2>&1 || { echo "error: codex CLI not found on PATH" >&2; exit 3; }
      set +e
      if [ -n "${CODEX_REVIEW_MODEL:-}" ]; then
        codex -C "$repo_root" -s read-only -a never -m "$CODEX_REVIEW_MODEL" exec resume "$session_id" \
          --json -o "$output_file" - < "$prompt_file" >> "$events_file" 2>> "$stderr_file"
      else
        codex -C "$repo_root" -s read-only -a never exec resume "$session_id" \
          --json -o "$output_file" - < "$prompt_file" >> "$events_file" 2>> "$stderr_file"
      fi
      final_exit_code=$?
      set -e
      ;;
    claude)
      command -v claude >/dev/null 2>&1 || { echo "error: claude CLI not found on PATH" >&2; exit 3; }
      set +e
      claude --model "${CLAUDE_REVIEW_MODEL:-opus}" --permission-mode plan --resume "$session_id" \
        -p --input-format text --output-format text < "$prompt_file" > "$output_file" 2>> "$stderr_file"
      final_exit_code=$?
      set -e
      ;;
    cursor)
      command -v cursor-agent >/dev/null 2>&1 || { echo "error: cursor-agent CLI not found on PATH" >&2; exit 3; }
      set +e
      cursor-agent --model "${CURSOR_REVIEW_MODEL:-cursor-grok-4.6-high}" --trust --mode ask \
        --workspace "$repo_root" --resume "$session_id" -p --output-format text \
        < "$prompt_file" > "$output_file" 2>> "$stderr_file"
      final_exit_code=$?
      set -e
      ;;
    *)
      echo "error: provider must be codex, claude, or cursor: $provider" >&2
      exit 2
      ;;
  esac

  if [ "$final_exit_code" -eq 0 ] && [ -s "$output_file" ]; then break; fi
  if grep -Eiq 'authentication|required.*login|permission denied|not found|not authenticated' "$stderr_file"; then break; fi
  attempt=$((attempt + 1))
done

if [ "$final_exit_code" -eq 0 ] && [ ! -s "$output_file" ]; then final_exit_code=5; fi
printf '%s\n' "$final_exit_code" > "$exit_code_file"
echo "$provider closure finished with exit code $final_exit_code (output: $output_file)"
exit "$final_exit_code"
