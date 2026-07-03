#!/usr/bin/env bash
# Smoke-test reviewer launchers with stubbed Claude and Cursor CLIs.
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/../../../../" && pwd)"
tmp_root="$(mktemp -d)"
stub_bin="$tmp_root/home/.local/bin"
mkdir -p "$stub_bin"

cleanup() {
  rm -rf "$tmp_root"
}
trap cleanup EXIT

cat > "$stub_bin/claude" <<'STUB'
#!/usr/bin/env bash
set -euo pipefail

if [ "${1:-}" = "--help" ]; then
  echo "usage: claude -p, --print <prompt>"
  exit 0
fi

count_file="${STUB_STATE_DIR}/claude-${STUB_MODE}.count"
count=0
if [ -f "$count_file" ]; then
  count="$(cat "$count_file")"
fi
count=$((count + 1))
printf '%s\n' "$count" > "$count_file"

stdin_text="$(cat)"
if [ -n "${STUB_EXPECT_STDIN_MARKER:-}" ]; then
  case "$stdin_text" in
    *"$STUB_EXPECT_STDIN_MARKER"*) ;;
    *)
      echo "expected prompt marker on stdin" >&2
      exit 98
      ;;
  esac
  case "$*" in
    *"$STUB_EXPECT_STDIN_MARKER"*)
      echo "prompt marker leaked into argv" >&2
      exit 97
      ;;
  esac
fi

case "$STUB_MODE" in
  success)
    echo "CLAUDE_OK"
    ;;
  empty_then_success)
    if [ "$count" -eq 1 ]; then
      echo "empty output from claude" >&2
      exit 0
    fi
    echo "CLAUDE_RETRY_OK"
    ;;
  retryable_stderr_then_success)
    if [ "$count" -eq 1 ]; then
      echo "connection reset by peer" >&2
      exit 70
    fi
    echo "CLAUDE_RETRYABLE_STDERR_RETRY_OK"
    ;;
  empty_always)
    echo "empty output from claude" >&2
    exit 0
    ;;
  empty_auth)
    echo "authentication required" >&2
    exit 0
    ;;
  usage_then_success)
    if printf '%s\n' "$*" | grep -q -- ' -p '; then
      echo "unknown option: -p" >&2
      exit 64
    fi
    echo "CLAUDE_USAGE_RETRY_OK"
    ;;
  required_prompt_then_success)
    if [ "$count" -eq 1 ]; then
      echo "usage: claude -p <prompt>" >&2
      echo "error: the following arguments are required: prompt" >&2
      exit 64
    fi
    echo "CLAUDE_REQUIRED_PROMPT_RETRY_OK"
    ;;
  quota_usage_failure)
    echo "account usage limit exceeded" >&2
    exit 64
    ;;
  *)
    echo "unexpected STUB_MODE: $STUB_MODE" >&2
    exit 99
    ;;
esac
STUB

cat > "$stub_bin/cursor-agent" <<'STUB'
#!/usr/bin/env bash
set -euo pipefail

if [ "${1:-}" = "--help" ]; then
  echo "usage: cursor-agent -p, --print <prompt>"
  exit 0
fi

if [ "${1:-}" = "create-chat" ]; then
  chat_count_file="${STUB_STATE_DIR}/cursor-chat.count"
  chat_count=0
  if [ -f "$chat_count_file" ]; then
    chat_count="$(cat "$chat_count_file")"
  fi
  chat_count=$((chat_count + 1))
  printf '%s\n' "$chat_count" > "$chat_count_file"
  if [ "${STUB_MODE}" = "create_chat_timeout_then_success" ] && [ "$chat_count" -eq 1 ]; then
    echo "timeout creating chat" >&2
    exit 70
  fi
  if [ "${STUB_MODE}" = "create_chat_empty" ] && [ "$chat_count" -eq 1 ]; then
    exit 0
  fi
  echo "chat-${chat_count}"
  exit 0
fi

count_file="${STUB_STATE_DIR}/cursor-${STUB_MODE}.count"
count=0
if [ -f "$count_file" ]; then
  count="$(cat "$count_file")"
fi
count=$((count + 1))
printf '%s\n' "$count" > "$count_file"

stdin_text="$(cat)"
if [ -n "${STUB_EXPECT_STDIN_MARKER:-}" ]; then
  case "$stdin_text" in
    *"$STUB_EXPECT_STDIN_MARKER"*) ;;
    *)
      echo "expected prompt marker on stdin" >&2
      exit 98
      ;;
  esac
  case "$*" in
    *"$STUB_EXPECT_STDIN_MARKER"*)
      echo "prompt marker leaked into argv" >&2
      exit 97
      ;;
  esac
fi

case "$STUB_MODE" in
  success)
    echo "CURSOR_OK"
    ;;
  empty_then_success)
    if [ "$count" -eq 1 ]; then
      echo "empty output from cursor" >&2
      exit 0
    fi
    echo "CURSOR_RETRY_OK"
    ;;
  retryable_stderr_then_success)
    if [ "$count" -eq 1 ]; then
      echo "connection reset by peer" >&2
      exit 70
    fi
    echo "CURSOR_RETRYABLE_STDERR_RETRY_OK"
    ;;
  empty_always)
    echo "empty output from cursor" >&2
    exit 0
    ;;
  empty_auth)
    echo "authentication required" >&2
    exit 0
    ;;
  create_chat_timeout_then_success)
    echo "CURSOR_CREATE_CHAT_RETRY_OK"
    ;;
  create_chat_empty)
    echo "CURSOR_CREATE_CHAT_EMPTY_SHOULD_NOT_RUN"
    ;;
  usage_then_success)
    if printf '%s\n' "$*" | grep -q -- ' -p '; then
      echo "unknown option: -p" >&2
      exit 64
    fi
    echo "CURSOR_USAGE_RETRY_OK"
    ;;
  required_prompt_then_success)
    if [ "$count" -eq 1 ]; then
      echo "usage: cursor-agent -p <prompt>" >&2
      echo "error: the following arguments are required: prompt" >&2
      exit 64
    fi
    echo "CURSOR_REQUIRED_PROMPT_RETRY_OK"
    ;;
  quota_usage_failure)
    echo "account usage limit exceeded" >&2
    exit 64
    ;;
  *)
    echo "unexpected STUB_MODE: $STUB_MODE" >&2
    exit 99
    ;;
esac
STUB

chmod +x "$stub_bin/claude" "$stub_bin/cursor-agent"

assert_file_contains() {
  local file="$1"
  local pattern="$2"

  if ! grep -qF "$pattern" "$file"; then
    echo "expected $file to contain: $pattern" >&2
    exit 1
  fi
}

assert_file_not_contains() {
  local file="$1"
  local pattern="$2"

  if grep -qF "$pattern" "$file"; then
    echo "expected $file not to contain: $pattern" >&2
    exit 1
  fi
}

assert_exit_code_file() {
  local file="$1"
  local expected="$2"
  local actual

  actual="$(cat "$file")"
  if [ "$actual" != "$expected" ]; then
    echo "expected $file to contain exit code $expected, got $actual" >&2
    exit 1
  fi
}

run_launcher() {
  local reviewer="$1"
  local prompt_file="$2"
  local artifact_dir="$3"

  if [ "$reviewer" = "cursor" ]; then
    "$script_dir/launch_cursor_review.sh" "$prompt_file" "$artifact_dir" "$repo_root"
  else
    "$script_dir/launch_claude_review.sh" "$prompt_file" "$artifact_dir"
  fi
}

run_success_case() {
  local reviewer="$1"
  local mode="$2"
  local artifact_dir="$tmp_root/${reviewer}-${mode}"
  local prompt_file="$artifact_dir/${reviewer}-prompt.md"
  local marker="PROMPT_STDIN_MARKER_${reviewer}_${mode}"

  mkdir -p "$artifact_dir"
  printf 'Reply OK\n%s\n' "$marker" > "$prompt_file"
  printf 'stale failure\n' > "$artifact_dir/${reviewer}-failure.md"

  (
    export STUB_MODE="$mode"
    export STUB_STATE_DIR="$artifact_dir"
    export STUB_EXPECT_STDIN_MARKER="$marker"
    export HOME="$tmp_root/home"
    export PATH="$stub_bin:$PATH"
    run_launcher "$reviewer" "$prompt_file" "$artifact_dir"
  )

  test -s "$artifact_dir/${reviewer}.md"
  test -f "$artifact_dir/${reviewer}-stderr.log"
  test -f "$artifact_dir/${reviewer}-attempts.md"
  test ! -f "$artifact_dir/${reviewer}-failure.md"
  assert_exit_code_file "$artifact_dir/${reviewer}-exit-code" "0"
  assert_file_contains "$artifact_dir/${reviewer}-session.md" "stderr_path:"
  assert_file_contains "$artifact_dir/${reviewer}-session.md" "attempt_log_path:"
  assert_file_contains "$artifact_dir/${reviewer}-attempts.md" "<prompt-file-stdin>"
  assert_file_contains "$artifact_dir/${reviewer}-session.md" "<prompt-file-stdin>"
  assert_file_not_contains "$artifact_dir/${reviewer}-attempts.md" "<prompt-file-contents>"
  assert_file_not_contains "$artifact_dir/${reviewer}-session.md" "<prompt-file-contents>"
  assert_file_not_contains "$artifact_dir/${reviewer}-attempts.md" "$marker"
  assert_file_not_contains "$artifact_dir/${reviewer}-session.md" "$marker"
  if [ "$reviewer" = "cursor" ]; then
    assert_file_contains "$artifact_dir/${reviewer}-attempts.md" "<chat-id>"
  else
    assert_file_contains "$artifact_dir/${reviewer}-attempts.md" "<session-id>"
  fi
}

run_large_prompt_stdin_case() {
  local reviewer="$1"
  local artifact_dir="$tmp_root/${reviewer}-large-prompt"
  local prompt_file="$artifact_dir/${reviewer}-prompt.md"
  local marker="LARGE_PROMPT_MARKER_17"
  local i

  mkdir -p "$artifact_dir"
  printf '%s\n' "$marker" > "$prompt_file"
  i=0
  while [ "$i" -lt 12000 ]; do
    printf 'large prompt line %05d padding padding padding padding padding\n' "$i" >> "$prompt_file"
    i=$((i + 1))
  done

  (
    export STUB_MODE="success"
    export STUB_STATE_DIR="$artifact_dir"
    export STUB_EXPECT_STDIN_MARKER="$marker"
    export HOME="$tmp_root/home"
    export PATH="$stub_bin:$PATH"
    run_launcher "$reviewer" "$prompt_file" "$artifact_dir"
  )

  test -s "$artifact_dir/${reviewer}.md"
  assert_exit_code_file "$artifact_dir/${reviewer}-exit-code" "0"
  assert_file_contains "$artifact_dir/${reviewer}-attempts.md" "<prompt-file-stdin>"
  assert_file_contains "$artifact_dir/${reviewer}-session.md" "<prompt-file-stdin>"
  assert_file_not_contains "$artifact_dir/${reviewer}-attempts.md" "$marker"
  assert_file_not_contains "$artifact_dir/${reviewer}-session.md" "$marker"
  assert_file_not_contains "$artifact_dir/${reviewer}-stderr.log" "$marker"
  test ! -f "$artifact_dir/${reviewer}-failure.md"
}

run_missing_prompt_case() {
  local reviewer="$1"
  local artifact_dir="$tmp_root/${reviewer}-missing-prompt"
  local prompt_file="$artifact_dir/missing.md"
  local exit_code

  mkdir -p "$artifact_dir"

  set +e
  (
    export STUB_MODE="success"
    export STUB_STATE_DIR="$artifact_dir"
    export HOME="$tmp_root/home"
    export PATH="$stub_bin:$PATH"
    run_launcher "$reviewer" "$prompt_file" "$artifact_dir"
  ) >/dev/null 2>&1
  exit_code=$?
  set -e

  if [ "$exit_code" -eq 0 ]; then
    echo "expected missing prompt case to fail for $reviewer" >&2
    exit 1
  fi
  test -f "$artifact_dir/${reviewer}-failure.md"
  assert_file_contains "$artifact_dir/${reviewer}-failure.md" "prompt file not found"
  assert_exit_code_file "$artifact_dir/${reviewer}-exit-code" "2"
}

run_empty_prompt_file_case() {
  local reviewer="$1"
  local artifact_dir="$tmp_root/${reviewer}-empty-prompt"
  local prompt_file="$artifact_dir/${reviewer}-prompt.md"
  local exit_code

  mkdir -p "$artifact_dir"
  : > "$prompt_file"

  set +e
  (
    export STUB_MODE="success"
    export STUB_STATE_DIR="$artifact_dir"
    export HOME="$tmp_root/home"
    export PATH="$stub_bin:$PATH"
    run_launcher "$reviewer" "$prompt_file" "$artifact_dir"
  ) >/dev/null 2>&1
  exit_code=$?
  set -e

  if [ "$exit_code" -ne 2 ]; then
    echo "expected empty prompt file to exit 2 for $reviewer, got $exit_code" >&2
    exit 1
  fi
  test -f "$artifact_dir/${reviewer}-failure.md"
  assert_file_contains "$artifact_dir/${reviewer}-failure.md" "prompt file is empty"
  assert_exit_code_file "$artifact_dir/${reviewer}-exit-code" "2"
}

run_terminal_empty_case() {
  local reviewer="$1"
  local artifact_dir="$tmp_root/${reviewer}-empty-always"
  local prompt_file="$artifact_dir/${reviewer}-prompt.md"
  local exit_code

  mkdir -p "$artifact_dir"
  printf 'Reply OK\n' > "$prompt_file"

  set +e
  (
    export STUB_MODE="empty_always"
    export STUB_STATE_DIR="$artifact_dir"
    export HOME="$tmp_root/home"
    export PATH="$stub_bin:$PATH"
    run_launcher "$reviewer" "$prompt_file" "$artifact_dir"
  ) >/dev/null 2>&1
  exit_code=$?
  set -e

  if [ "$exit_code" -ne 5 ]; then
    echo "expected empty output exhaustion to exit 5 for $reviewer, got $exit_code" >&2
    exit 1
  fi
  test -f "$artifact_dir/${reviewer}-failure.md"
  assert_file_contains "$artifact_dir/${reviewer}-failure.md" "reviewer exited 0 with empty stdout"
  assert_exit_code_file "$artifact_dir/${reviewer}-exit-code" "5"
}

run_empty_deterministic_case() {
  local reviewer="$1"
  local artifact_dir="$tmp_root/${reviewer}-empty-auth"
  local prompt_file="$artifact_dir/${reviewer}-prompt.md"
  local exit_code

  mkdir -p "$artifact_dir"
  printf 'Reply OK\n' > "$prompt_file"

  set +e
  (
    export STUB_MODE="empty_auth"
    export STUB_STATE_DIR="$artifact_dir"
    export HOME="$tmp_root/home"
    export PATH="$stub_bin:$PATH"
    run_launcher "$reviewer" "$prompt_file" "$artifact_dir"
  ) >/dev/null 2>&1
  exit_code=$?
  set -e

  if [ "$exit_code" -ne 5 ]; then
    echo "expected deterministic empty stdout to exit 5 for $reviewer, got $exit_code" >&2
    exit 1
  fi
  assert_file_contains "$artifact_dir/${reviewer}-attempts.md" "no retry - deterministic setup failure"
  assert_file_contains "$artifact_dir/${reviewer}-failure.md" "deterministic setup failure"
}

run_nonretry_usage_word_case() {
  local reviewer="$1"
  local artifact_dir="$tmp_root/${reviewer}-quota-usage"
  local prompt_file="$artifact_dir/${reviewer}-prompt.md"
  local exit_code

  mkdir -p "$artifact_dir"
  printf 'Reply OK\n' > "$prompt_file"

  set +e
  (
    export STUB_MODE="quota_usage_failure"
    export STUB_STATE_DIR="$artifact_dir"
    export HOME="$tmp_root/home"
    export PATH="$stub_bin:$PATH"
    run_launcher "$reviewer" "$prompt_file" "$artifact_dir"
  ) >/dev/null 2>&1
  exit_code=$?
  set -e

  if [ "$exit_code" -ne 64 ]; then
    echo "expected non-retryable usage prose to exit 64 for $reviewer, got $exit_code" >&2
    exit 1
  fi
  assert_file_contains "$artifact_dir/${reviewer}-attempts.md" "no retry - non-retryable reviewer failure"
}

run_missing_cli_case() {
  local reviewer="$1"
  local artifact_dir="$tmp_root/${reviewer}-missing-cli"
  local prompt_file="$artifact_dir/${reviewer}-prompt.md"
  local isolated_home="$tmp_root/${reviewer}-missing-cli-home"
  local exit_code

  mkdir -p "$artifact_dir" "$isolated_home/.local/bin"
  printf 'Reply OK\n' > "$prompt_file"

  set +e
  (
    export STUB_MODE="success"
    export STUB_STATE_DIR="$artifact_dir"
    export HOME="$isolated_home"
    export PATH="/usr/bin:/bin"
    run_launcher "$reviewer" "$prompt_file" "$artifact_dir"
  ) >/dev/null 2>&1
  exit_code=$?
  set -e

  if [ "$exit_code" -ne 3 ]; then
    echo "expected missing CLI to exit 3 for $reviewer, got $exit_code" >&2
    exit 1
  fi
  test -f "$artifact_dir/${reviewer}-failure.md"
  assert_exit_code_file "$artifact_dir/${reviewer}-exit-code" "3"
}

run_create_chat_empty_case() {
  local artifact_dir="$tmp_root/cursor-create-chat-empty"
  local prompt_file="$artifact_dir/cursor-prompt.md"
  local exit_code

  mkdir -p "$artifact_dir"
  printf 'Reply OK\n' > "$prompt_file"

  set +e
  (
    export STUB_MODE="create_chat_empty"
    export STUB_STATE_DIR="$artifact_dir"
    export HOME="$tmp_root/home"
    export PATH="$stub_bin:$PATH"
    run_launcher "cursor" "$prompt_file" "$artifact_dir"
  ) >/dev/null 2>&1
  exit_code=$?
  set -e

  if [ "$exit_code" -ne 4 ]; then
    echo "expected empty create-chat to exit 4, got $exit_code" >&2
    exit 1
  fi
  assert_file_contains "$artifact_dir/cursor-stderr.log" "create-chat returned no chat id"
  assert_file_contains "$artifact_dir/cursor-attempts.md" "exit_code: 4"
  test -f "$artifact_dir/cursor-failure.md"
  assert_file_contains "$artifact_dir/cursor-failure.md" "deterministic setup failure"
}

run_success_case claude success
run_success_case cursor success
run_large_prompt_stdin_case claude
run_large_prompt_stdin_case cursor
run_success_case claude empty_then_success
assert_file_contains "$tmp_root/claude-empty_then_success/claude-attempts.md" "retry - empty stdout"
run_success_case cursor empty_then_success
assert_file_contains "$tmp_root/cursor-empty_then_success/cursor-attempts.md" "retry - empty stdout"
run_success_case claude retryable_stderr_then_success
assert_file_contains "$tmp_root/claude-retryable_stderr_then_success/claude.md" "CLAUDE_RETRYABLE_STDERR_RETRY_OK"
assert_file_contains "$tmp_root/claude-retryable_stderr_then_success/claude-stderr.log" "connection reset by peer"
assert_file_contains "$tmp_root/claude-retryable_stderr_then_success/claude-attempts.md" "retry - retryable launcher stderr"
assert_file_not_contains "$tmp_root/claude-retryable_stderr_then_success/claude-attempts.md" "usage drift"
run_success_case cursor retryable_stderr_then_success
assert_file_contains "$tmp_root/cursor-retryable_stderr_then_success/cursor.md" "CURSOR_RETRYABLE_STDERR_RETRY_OK"
assert_file_contains "$tmp_root/cursor-retryable_stderr_then_success/cursor-stderr.log" "connection reset by peer"
assert_file_contains "$tmp_root/cursor-retryable_stderr_then_success/cursor-attempts.md" "retry - retryable launcher stderr with fresh chat"
assert_file_not_contains "$tmp_root/cursor-retryable_stderr_then_success/cursor-attempts.md" "usage drift"
run_success_case claude usage_then_success
assert_file_contains "$tmp_root/claude-usage_then_success/claude-stderr.log" "unknown option"
assert_file_contains "$tmp_root/claude-usage_then_success/claude-attempts.md" "retry - usage drift"
run_success_case cursor usage_then_success
assert_file_contains "$tmp_root/cursor-usage_then_success/cursor-stderr.log" "unknown option"
assert_file_contains "$tmp_root/cursor-usage_then_success/cursor-attempts.md" "retry - usage drift"
run_success_case claude required_prompt_then_success
assert_file_contains "$tmp_root/claude-required_prompt_then_success/claude-attempts.md" "retry - usage drift"
run_success_case cursor required_prompt_then_success
assert_file_contains "$tmp_root/cursor-required_prompt_then_success/cursor-attempts.md" "retry - usage drift"
run_success_case cursor create_chat_timeout_then_success
assert_file_contains "$tmp_root/cursor-create_chat_timeout_then_success/cursor-attempts.md" "retry - retryable create-chat"
run_terminal_empty_case claude
run_terminal_empty_case cursor
run_empty_deterministic_case claude
run_empty_deterministic_case cursor
run_nonretry_usage_word_case claude
run_nonretry_usage_word_case cursor
run_create_chat_empty_case
run_missing_prompt_case claude
run_missing_prompt_case cursor
run_empty_prompt_file_case claude
run_empty_prompt_file_case cursor
run_missing_cli_case claude
run_missing_cli_case cursor

echo "reviewer launcher smoke tests passed"
