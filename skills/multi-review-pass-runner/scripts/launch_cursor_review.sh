#!/usr/bin/env bash
# Launch one Cursor review in a fresh chat scoped to the repo workspace,
# persisting output, stderr, attempt metadata, session metadata, and numeric
# exit status as artifacts.
# Exit codes: 2 = usage/missing/unreadable/empty prompt file, 3 = cursor-agent
# CLI unavailable, 4 = chat creation failed, 5 = launcher-level empty output
# failure; otherwise propagates the reviewer CLI's final exit status.
set -euo pipefail

if [ "$#" -ne 3 ]; then
  echo "usage: launch_cursor_review.sh <prompt-file> <artifact-dir> <repo-root>" >&2
  exit 2
fi

prompt_file="$1"
artifact_dir="$2"
repo_root="$3"
mkdir -p "$artifact_dir"

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=launcher_common.sh
source "$script_dir/launcher_common.sh"
# shellcheck source=lib_review_launch.sh
source "$script_dir/lib_review_launch.sh"

output_file="$artifact_dir/cursor.md"
session_file="$artifact_dir/cursor-session.md"
exit_code_file="$artifact_dir/cursor-exit-code"
stderr_file="$artifact_dir/cursor-stderr.log"
attempts_file="$artifact_dir/cursor-attempts.md"
failure_file="$artifact_dir/cursor-failure.md"
model="composer-2.5"
reviewer="cursor"

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
    "cursor-agent setup" \
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
# Cursor Review Session

- slug: cursor
- chat_id: unavailable
- model: $model
- command: cursor-agent setup
- prompt_path: $prompt_file
- output_path: $output_file
- stderr_path: $stderr_file
- attempt_log_path: $attempts_file
- final_output_bytes: $(artifact_size "$output_file")
- failure_artifact_path: $failure_file
EOF
  echo "cursor review failed during setup: $detail" >&2
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
if ! command -v cursor-agent >/dev/null 2>&1; then
  record_setup_failure 3 "error: cursor-agent CLI not found on PATH"
fi

create_chat() {
  local chat_stderr="$1"
  local candidate

  set +e
  candidate="$(cursor-agent create-chat 2>> "$chat_stderr")"
  chat_exit=$?
  set -e

  if [ "$chat_exit" -ne 0 ]; then
    chat_exit_code="$chat_exit"
    return 1
  fi

  if [ -z "$candidate" ]; then
    printf '%s\n' "error: cursor-agent create-chat returned no chat id" >> "$chat_stderr"
    chat_exit_code=4
    return 1
  fi

  chat_exit_code=0
  chat_id="$(printf '%s' "$candidate" | tr -d '[:space:]')"
  if [ -z "$chat_id" ]; then
    printf '%s\n' "error: cursor-agent create-chat returned no chat id" >> "$chat_stderr"
    chat_exit_code=4
    return 1
  fi
  return 0
}

prompt_flag="$(select_prompt_flag cursor-agent)"
attempt=1
max_attempts=2
final_exit_code=1
final_chat_id=""
failure_class="transient launcher failure"
failure_detail="unknown launcher failure"
chat_exit_code=0
chat_id=""

while [ "$attempt" -le "$max_attempts" ]; do
  attempt_stderr="$(mktemp)"
  : > "$output_file"
  append_stderr_header "$stderr_file" "$attempt"

  if ! create_chat "$attempt_stderr"; then
    cat "$attempt_stderr" >> "$stderr_file"
    final_exit_code=4
    final_chat_id="unavailable"
    failure_detail="cursor-agent create-chat failed or returned no chat id"
    if is_deterministic_setup_error "$attempt_stderr"; then
      failure_class="deterministic setup failure"
      retry_decision="no retry - deterministic setup failure"
    elif is_retryable_launcher_error "$attempt_stderr"; then
      failure_class="transient launcher failure"
      if [ "$attempt" -lt "$max_attempts" ]; then
        retry_decision="retry - retryable create-chat stderr with fresh chat"
      else
        retry_decision="no retry - create-chat retry exhausted"
      fi
    else
      failure_class="non-retryable create-chat failure"
      retry_decision="no retry - non-retryable create-chat failure"
    fi
    append_attempt_log \
      "$attempts_file" \
      "$attempt" \
      "cursor-agent create-chat" \
      "$chat_exit_code" \
      "$(artifact_size "$output_file")" \
      "$(artifact_size "$attempt_stderr")" \
      "$retry_decision"
    rm -f "$attempt_stderr"
    case "$retry_decision" in
      retry*)
        attempt=$((attempt + 1))
        continue
        ;;
    esac
    break
  fi

  final_chat_id="$chat_id"
  command_shape="cursor-agent --model $model --trust --force --workspace $repo_root --resume <chat-id> $prompt_flag --output-format text < <prompt-file-stdin>"

  set +e
  cursor-agent --model "$model" --trust --force --workspace "$repo_root" --resume "$chat_id" \
    "$prompt_flag" --output-format text \
    < "$prompt_file" \
    > "$output_file" 2>> "$attempt_stderr"
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
    "retry - empty stdout with fresh chat" \
    "retry - retryable launcher stderr with fresh chat" \
    "retry - usage drift with alternate prompt flag and fresh chat"
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
# Cursor Review Session

- slug: cursor
- chat_id: $final_chat_id
- model: $model
- command: cursor-agent --model $model --trust --force --workspace $repo_root --resume <chat-id> <prompt-mode> --output-format text < <prompt-file-stdin>
- prompt_path: $prompt_file
- output_path: $output_file
- stderr_path: $stderr_file
- attempt_log_path: $attempts_file
- final_output_bytes: $(artifact_size "$output_file")
- failure_artifact_path: $failure_path
EOF

echo "cursor review finished with exit code $final_exit_code (output: $output_file)"
exit "$final_exit_code"
