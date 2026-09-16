#!/usr/bin/env bash
# Shared artifact helpers for reviewer launcher scripts.

artifact_size() {
  if [ -f "$1" ]; then
    wc -c < "$1" | tr -d '[:space:]'
  else
    printf '0'
  fi
}

phase_and_pass_label() {
  local artifact_dir="$1"
  local base
  base="$(basename "$artifact_dir")"

  case "$base" in
    plan-review-pass*)
      printf 'plan-review, pass %s' "${base#plan-review-pass}"
      ;;
    code-review-pass*)
      printf 'code-review, pass %s' "${base#code-review-pass}"
      ;;
    *)
      printf 'launcher-level, pass unknown'
      ;;
  esac
}

init_attempt_log() {
  local attempts_file="$1"
  local reviewer="$2"
  local prompt_file="$3"

  cat > "$attempts_file" <<EOF
# ${reviewer} Launcher Attempts

- prompt_path: $prompt_file

EOF
}

append_attempt_log() {
  local attempts_file="$1"
  local attempt="$2"
  local command_shape="$3"
  local exit_code="$4"
  local output_bytes="$5"
  local stderr_bytes="$6"
  local retry_decision="$7"

  cat >> "$attempts_file" <<EOF
## Attempt $attempt

- command: $command_shape
- exit_code: $exit_code
- output_bytes: $output_bytes
- stderr_bytes: $stderr_bytes
- retry_decision: $retry_decision

EOF
}

write_failure_artifact() {
  local failure_file="$1"
  local reviewer="$2"
  local artifact_dir="$3"
  local attempt_count="$4"
  local failure_class="$5"
  local pass_outcome="$6"
  local override_reason="$7"
  local stderr_file="$8"
  local attempts_file="$9"
  local detail="${10}"

  cat > "$failure_file" <<EOF
# ${reviewer} Failure

## Reviewer
$reviewer

## Phase And Pass
$(phase_and_pass_label "$artifact_dir")

## Attempts
$attempt_count attempt(s). See attempt log: $attempts_file

## Elapsed / Status Checks
Launcher completed synchronously; stderr captured at: $stderr_file

## Failure Class
$failure_class

## Pass Outcome
$pass_outcome

## Override Reason
$override_reason

## Detail
$detail
EOF
}

is_deterministic_setup_error() {
  local stderr_file="$1"

  grep -Eiq \
    'authentication required|login required|required.*authentication|not authenticated|unauthorized|permission denied|workspace trust|not trusted|command not allowed|prompt file not found|prompt file not readable|prompt file is empty|not found on PATH|create-chat returned no chat id|inaccessible review scope|review scope.*inaccessible|cannot access.*review scope|interactive prompt|prompt request|requests? interactive prompt|waiting for prompt' \
    "$stderr_file"
}

is_retryable_launcher_error() {
  local stderr_file="$1"

  grep -Eiq \
    '(^|[[:space:]])usage:|unknown option|unknown flag|unrecognized option|invalid option|empty output|lost liveness|unresumable|could not resume|session expired|chat not found|timeout|timed out|temporar|connection reset|broken pipe|rate limit' \
    "$stderr_file"
}

append_stderr_header() {
  local stderr_file="$1"
  local attempt="$2"

  {
    printf '\n## Attempt %s stderr\n' "$attempt"
  } >> "$stderr_file"
}
