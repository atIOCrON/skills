#!/usr/bin/env bash
# Verify a reviewer CLI can start and resume the same conversation.
set -euo pipefail

if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
  echo "usage: run_reviewer_preflight.sh <claude|cursor> [repo-root]" >&2
  exit 2
fi

reviewer="$1"
repo_root="${2:-}"
smoke_token="ORCHESTRATE_SESSION_SMOKE"
ok_token="REVIEWER_SMOKE_OK"
claude_model="opus"
cursor_model="composer-2.5"

export PATH="$HOME/.local/bin:$PATH"

last_non_empty_line() {
  awk 'NF { line = $0 } END { print line }'
}

assert_smoke_token() {
  local reviewer_name="$1"
  local step="$2"
  local expected="$3"
  local raw_output="$4"
  local actual

  actual="$(last_non_empty_line <<< "$raw_output")"

  if [ "$actual" != "$expected" ]; then
    {
      echo "error: $reviewer_name preflight $step returned unexpected output"
      echo "expected final token line: $expected"
      echo "actual final token line: $actual"
      echo "raw output: $raw_output"
    } >&2
    exit 1
  fi
}

run_claude_preflight() {
  if ! command -v claude >/dev/null 2>&1; then
    echo "error: claude CLI not found on PATH" >&2
    exit 3
  fi

  local session_id
  session_id="$(uuidgen | tr '[:upper:]' '[:lower:]')"

  local first_output
  first_output="$(
    claude --model "$claude_model" --dangerously-skip-permissions \
      --session-id "$session_id" \
      -p "Remember token $smoke_token. Return exactly: $ok_token" \
      --output-format text
  )"
  assert_smoke_token "claude" "first prompt" "$ok_token" "$first_output"

  local resume_output
  resume_output="$(
    claude --model "$claude_model" --dangerously-skip-permissions \
      --resume "$session_id" \
      -p "Return exactly the token you were asked to remember." \
      --output-format text
  )"
  assert_smoke_token "claude" "resume prompt" "$smoke_token" "$resume_output"

  cat <<EOF
reviewer: claude
command: claude
model: $claude_model
session_id: $session_id
first_prompt: pass
resume: pass
pass: true
EOF
}

run_cursor_preflight() {
  if [ -z "$repo_root" ]; then
    echo "error: repo-root is required for cursor preflight" >&2
    exit 2
  fi
  if [ ! -d "$repo_root" ]; then
    echo "error: repo-root is not a directory: $repo_root" >&2
    exit 2
  fi
  if ! command -v cursor-agent >/dev/null 2>&1; then
    echo "error: cursor-agent CLI not found on PATH" >&2
    exit 3
  fi

  local chat_id
  chat_id="$(cursor-agent create-chat)"
  if [ -z "$chat_id" ]; then
    echo "error: cursor-agent create-chat returned no chat id" >&2
    exit 4
  fi

  local first_output
  first_output="$(
    cursor-agent --model "$cursor_model" --trust --force --workspace "$repo_root" \
      --resume "$chat_id" \
      -p "Remember token $smoke_token. Return exactly: $ok_token" \
      --output-format text
  )"
  assert_smoke_token "cursor" "first prompt" "$ok_token" "$first_output"

  local resume_output
  resume_output="$(
    cursor-agent --model "$cursor_model" --trust --force --workspace "$repo_root" \
      --resume "$chat_id" \
      -p "Return exactly the token you were asked to remember." \
      --output-format text
  )"
  assert_smoke_token "cursor" "resume prompt" "$smoke_token" "$resume_output"

  cat <<EOF
reviewer: cursor
command: cursor-agent
model: $cursor_model
chat_id: $chat_id
first_prompt: pass
resume: pass
pass: true
EOF
}

case "$reviewer" in
  claude)
    run_claude_preflight
    ;;
  cursor)
    run_cursor_preflight
    ;;
  *)
    echo "error: reviewer must be claude or cursor: $reviewer" >&2
    exit 2
    ;;
esac
