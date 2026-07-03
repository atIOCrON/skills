#!/usr/bin/env bash
# Launch one Claude Code review in a fresh session, persisting output,
# stderr, attempt metadata, session metadata, and numeric exit status.
# Exit codes: 2 = usage/missing/unreadable/empty prompt file, 3 = claude CLI
# unavailable, 5 = launcher-level empty output failure; otherwise propagates
# the reviewer CLI's final exit status.
set -euo pipefail

if [ "$#" -ne 2 ]; then
  echo "usage: launch_claude_review.sh <prompt-file> <artifact-dir>" >&2
  exit 2
fi

prompt_file="$1"
artifact_dir="$2"
mkdir -p "$artifact_dir"

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=launcher_common.sh
source "$script_dir/launcher_common.sh"
# shellcheck source=lib_review_launch.sh
source "$script_dir/lib_review_launch.sh"

output_file="$artifact_dir/claude.md"
session_file="$artifact_dir/claude-session.md"
exit_code_file="$artifact_dir/claude-exit-code"
stderr_file="$artifact_dir/claude-stderr.log"
attempts_file="$artifact_dir/claude-attempts.md"
failure_file="$artifact_dir/claude-failure.md"
model="opus"
reviewer="claude"

rm -f "$failure_file"
: > "$output_file"
: > "$stderr_file"
init_attempt_log "$attempts_file" "$reviewer" "$prompt_file"

record_setup_failure() {
  local exit_code="$1"
  local detail="$2"

  printf '%s\n' "$detail" >> "$stderr_file"
  printf '%s\n' "$exit_code" > "$exit_code_file"
  append_attempt_log \
    "$attempts_file" \
    "1" \
    "claude setup" \
    "$exit_code" \
    "$(artifact_size "$output_file")" \
    "$(artifact_size "$stderr_file")" \
    "no retry - deterministic setup failure"
  write_failure_artifact \
    "$failure_file" \
    "$reviewer" \
    "$artifact_dir" \
    "1" \
    "deterministic setup failure" \
    "stopped-blocked" \
    "None" \
    "$stderr_file" \
    "$attempts_file" \
    "$detail"
  cat > "$session_file" <<EOF
# Claude Review Session

- slug: claude
- session_id: unavailable
- model: $model
- command: claude setup
- prompt_path: $prompt_file
- output_path: $output_file
- stderr_path: $stderr_file
- attempt_log_path: $attempts_file
- final_output_bytes: $(artifact_size "$output_file")
- failure_artifact_path: $failure_file
EOF
  echo "claude review failed during setup: $detail" >&2
  exit "$exit_code"
}

if [ ! -f "$prompt_file" ]; then
  record_setup_failure 2 "error: prompt file not found: $prompt_file"
fi
if [ ! -r "$prompt_file" ]; then
  record_setup_failure 2 "error: prompt file not readable: $prompt_file"
fi
if [ ! -s "$prompt_file" ]; then
  record_setup_failure 2 "error: prompt file is empty: $prompt_file"
fi

export PATH="$HOME/.local/bin:$PATH"
if ! command -v claude >/dev/null 2>&1; then
  record_setup_failure 3 "error: claude CLI not found on PATH"
fi

prompt_flag="$(select_prompt_flag claude)"
attempt=1
max_attempts=2
final_exit_code=1
final_session_id=""
failure_class="transient launcher failure"
failure_detail="unknown launcher failure"

while [ "$attempt" -le "$max_attempts" ]; do
  session_id="$(uuidgen | tr '[:upper:]' '[:lower:]')"
  final_session_id="$session_id"
  attempt_stderr="$(mktemp)"
  : > "$output_file"

  command_shape="claude --model $model --dangerously-skip-permissions --session-id <session-id> $prompt_flag --input-format text --output-format text < <prompt-file-stdin>"
  append_stderr_header "$stderr_file" "$attempt"

  set +e
  claude --model "$model" --dangerously-skip-permissions \
    --session-id "$session_id" \
    "$prompt_flag" --input-format text --output-format text \
    < "$prompt_file" \
    > "$output_file" 2> "$attempt_stderr"
  exit_code=$?
  set -e

  cat "$attempt_stderr" >> "$stderr_file"
  output_bytes="$(artifact_size "$output_file")"
  attempt_stderr_bytes="$(artifact_size "$attempt_stderr")"
  final_exit_code="$exit_code"

  classify_reviewer_attempt \
    "$exit_code" \
    "$output_bytes" \
    "$attempt_stderr" \
    "$attempt" \
    "$max_attempts" \
    "retry - empty stdout" \
    "retry - retryable launcher stderr" \
    "retry - usage drift with alternate prompt flag"
  final_exit_code="$review_final_exit_code"
  failure_class="$review_failure_class"
  failure_detail="$review_failure_detail"
  retry_decision="$review_retry_decision"
  if [ "$review_switch_prompt_flag" -eq 1 ]; then
    prompt_flag="$(alternate_prompt_flag "$prompt_flag")"
  fi

  if [ "$exit_code" -eq 0 ] && [ "$output_bytes" -gt 0 ]; then
    append_attempt_log "$attempts_file" "$attempt" "$command_shape" "$exit_code" "$output_bytes" "$attempt_stderr_bytes" "$retry_decision"
    rm -f "$attempt_stderr"
    break
  fi

  append_attempt_log "$attempts_file" "$attempt" "$command_shape" "$exit_code" "$output_bytes" "$attempt_stderr_bytes" "$retry_decision"
  rm -f "$attempt_stderr"

  case "$retry_decision" in
    retry*)
      attempt=$((attempt + 1))
      continue
      ;;
  esac

  break
done

printf '%s\n' "$final_exit_code" > "$exit_code_file"

failure_path="None"
if [ "$final_exit_code" -ne 0 ] || [ "$(artifact_size "$output_file")" -eq 0 ]; then
  failure_path="$failure_file"
  if [ "$final_exit_code" -eq 0 ]; then
    final_exit_code=5
    printf '%s\n' "$final_exit_code" > "$exit_code_file"
  fi
  write_failure_artifact \
    "$failure_file" \
    "$reviewer" \
    "$artifact_dir" \
    "$attempt" \
    "$failure_class" \
    "stopped-blocked" \
    "None" \
    "$stderr_file" \
    "$attempts_file" \
    "$failure_detail"
fi

cat > "$session_file" <<EOF
# Claude Review Session

- slug: claude
- session_id: $final_session_id
- model: $model
- command: claude --model $model --dangerously-skip-permissions --session-id <session-id> <prompt-mode> --input-format text --output-format text < <prompt-file-stdin>
- prompt_path: $prompt_file
- output_path: $output_file
- stderr_path: $stderr_file
- attempt_log_path: $attempts_file
- final_output_bytes: $(artifact_size "$output_file")
- failure_artifact_path: $failure_path
EOF

echo "claude review finished with exit code $final_exit_code (output: $output_file)"
exit "$final_exit_code"
