#!/usr/bin/env bash
# Launch a read-only Codex review in a fresh resumable session.
set -euo pipefail

if [ "$#" -ne 3 ]; then
  echo "usage: launch_codex_review.sh <prompt-file> <artifact-dir> <repo-root>" >&2
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

reviewer="codex"
model="${CODEX_REVIEW_MODEL:-default}"
output_file="$artifact_dir/codex.md"
session_file="$artifact_dir/codex-session.md"
exit_code_file="$artifact_dir/codex-exit-code"
stderr_file="$artifact_dir/codex-stderr.log"
events_file="$artifact_dir/codex-events.jsonl"
attempts_file="$artifact_dir/codex-attempts.md"
failure_file="$artifact_dir/codex-failure.md"

rm -f "$failure_file"
: > "$output_file"
: > "$stderr_file"
: > "$events_file"
init_attempt_log "$attempts_file" "$reviewer" "$prompt_file"

record_setup_failure() {
  local exit_code="$1"
  local detail="$2"
  printf '%s\n' "$detail" >> "$stderr_file"
  printf '%s\n' "$exit_code" > "$exit_code_file"
  append_attempt_log "$attempts_file" 1 "codex setup" "$exit_code" 0 "$(artifact_size "$stderr_file")" "no retry - deterministic setup failure"
  write_failure_artifact "$failure_file" "$reviewer" "$artifact_dir" 1 "deterministic setup failure" "stopped-blocked" "None" "$stderr_file" "$attempts_file" "$detail"
  cat > "$session_file" <<EOF
# Codex Review Session

- slug: codex
- transport: cli-session
- session_id: unavailable
- model: $model
- command: codex setup
- prompt_path: $prompt_file
- output_path: $output_file
- events_path: $events_file
- stderr_path: $stderr_file
- attempt_log_path: $attempts_file
- final_output_bytes: 0
- failure_artifact_path: $failure_file
EOF
  exit "$exit_code"
}

test -f "$prompt_file" || record_setup_failure 2 "error: prompt file not found: $prompt_file"
test -r "$prompt_file" || record_setup_failure 2 "error: prompt file not readable: $prompt_file"
test -s "$prompt_file" || record_setup_failure 2 "error: prompt file is empty: $prompt_file"
test -d "$repo_root" || record_setup_failure 2 "error: repo-root is not a directory: $repo_root"
command -v codex >/dev/null 2>&1 || record_setup_failure 3 "error: codex CLI not found on PATH"
command -v jq >/dev/null 2>&1 || record_setup_failure 3 "error: jq not found on PATH"

attempt=1
max_attempts=2
final_exit_code=1
final_session_id=""
failure_class="transient launcher failure"
failure_detail="unknown launcher failure"

while [ "$attempt" -le "$max_attempts" ]; do
  attempt_stderr="$(mktemp)"
  attempt_events="$(mktemp)"
  : > "$output_file"
  append_stderr_header "$stderr_file" "$attempt"
  command_shape="codex -C $repo_root -s read-only -a never <model> exec --json -o <output-file> - < <prompt-file-stdin>"

  set +e
  if [ "$model" = "default" ]; then
    codex -C "$repo_root" -s read-only -a never exec --json -o "$output_file" - \
      < "$prompt_file" > "$attempt_events" 2> "$attempt_stderr"
  else
    codex -C "$repo_root" -s read-only -a never -m "$model" exec --json -o "$output_file" - \
      < "$prompt_file" > "$attempt_events" 2> "$attempt_stderr"
  fi
  exit_code=$?
  set -e

  cat "$attempt_events" >> "$events_file"
  cat "$attempt_stderr" >> "$stderr_file"
  output_bytes="$(artifact_size "$output_file")"
  session_id="$(jq -r 'select(.type == "thread.started") | .thread_id // .thread.id // empty' "$attempt_events" 2>/dev/null | tail -n 1)"
  final_session_id="$session_id"

  classify_reviewer_attempt "$exit_code" "$output_bytes" "$attempt_stderr" "$attempt" "$max_attempts" \
    "retry - empty stdout" "retry - retryable launcher stderr" "retry - usage drift"
  final_exit_code="$review_final_exit_code"
  failure_class="$review_failure_class"
  failure_detail="$review_failure_detail"
  retry_decision="$review_retry_decision"

  if [ "$exit_code" -eq 0 ] && [ "$output_bytes" -gt 0 ] && [ -n "$session_id" ]; then
    retry_decision="no retry - completed"
    append_attempt_log "$attempts_file" "$attempt" "$command_shape" 0 "$output_bytes" "$(artifact_size "$attempt_stderr")" "$retry_decision"
    rm -f "$attempt_stderr" "$attempt_events"
    final_exit_code=0
    break
  fi

  if [ "$exit_code" -eq 0 ] && [ "$output_bytes" -gt 0 ] && [ -z "$session_id" ]; then
    final_exit_code=6
    failure_class="session metadata failure"
    failure_detail="codex output did not include a thread.started session id"
    retry_decision="no retry - missing session id"
  fi
  append_attempt_log "$attempts_file" "$attempt" "$command_shape" "$final_exit_code" "$output_bytes" "$(artifact_size "$attempt_stderr")" "$retry_decision"
  rm -f "$attempt_stderr" "$attempt_events"
  case "$retry_decision" in retry*) attempt=$((attempt + 1)); continue ;; esac
  break
done

printf '%s\n' "$final_exit_code" > "$exit_code_file"
failure_path="None"
if [ "$final_exit_code" -ne 0 ]; then
  failure_path="$failure_file"
  write_failure_artifact "$failure_file" "$reviewer" "$artifact_dir" "$attempt" "$failure_class" "stopped-blocked" "None" "$stderr_file" "$attempts_file" "$failure_detail"
fi

cat > "$session_file" <<EOF
# Codex Review Session

- slug: codex
- transport: cli-session
- session_id: ${final_session_id:-unavailable}
- model: $model
- command: codex -C <repo-root> -s read-only -a never <model> exec --json -o <output-file> - < <prompt-file-stdin>
- prompt_path: $prompt_file
- output_path: $output_file
- events_path: $events_file
- stderr_path: $stderr_file
- attempt_log_path: $attempts_file
- final_output_bytes: $(artifact_size "$output_file")
- failure_artifact_path: $failure_path
EOF

echo "codex review finished with exit code $final_exit_code (output: $output_file)"
exit "$final_exit_code"
