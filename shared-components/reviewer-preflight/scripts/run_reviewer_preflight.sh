#!/usr/bin/env bash
# Verify a provider CLI can create and resume a read-only review session.
set -euo pipefail

if [ "$#" -ne 2 ]; then
  echo "usage: run_reviewer_preflight.sh <codex|claude|cursor> <repo-root>" >&2
  exit 2
fi

provider="$1"
repo_root="$2"
smoke_token="ORCHESTRATE_SESSION_SMOKE"
ok_token="REVIEWER_SMOKE_OK"
tmp_root="$(mktemp -d)"
trap 'rm -rf "$tmp_root"' EXIT

test -d "$repo_root" || { echo "error: repo-root is not a directory: $repo_root" >&2; exit 2; }

last_non_empty_line() { awk 'NF { line = $0 } END { print line }'; }
assert_token() {
  local step="$1" expected="$2" file="$3" actual
  actual="$(last_non_empty_line < "$file")"
  test "$actual" = "$expected" || {
    echo "error: $provider preflight $step returned '$actual', expected '$expected'" >&2
    exit 1
  }
}

run_claude() {
  command -v claude >/dev/null 2>&1 || { echo "error: claude CLI not found on PATH" >&2; exit 3; }
  local session_id model
  session_id="$(uuidgen | tr '[:upper:]' '[:lower:]')"
  model="${CLAUDE_REVIEW_MODEL:-opus}"
  (
    cd "$repo_root"
    claude --model "$model" --permission-mode plan --session-id "$session_id" \
      -p "Remember token $smoke_token. Return exactly: $ok_token" --output-format text
  ) > "$tmp_root/first"
  assert_token "first prompt" "$ok_token" "$tmp_root/first"
  (
    cd "$repo_root"
    claude --model "$model" --permission-mode plan --resume "$session_id" \
      -p "Return exactly the token you were asked to remember." --output-format text
  ) > "$tmp_root/resume"
  assert_token "resume" "$smoke_token" "$tmp_root/resume"
  printf 'reviewer: claude\ncommand: claude\nmodel: %s\nsession_id: %s\npass: true\n' "$model" "$session_id"
}

run_cursor() {
  command -v cursor-agent >/dev/null 2>&1 || { echo "error: cursor-agent CLI not found on PATH" >&2; exit 3; }
  local chat_id model
  model="${CURSOR_REVIEW_MODEL:-composer-2.5}"
  chat_id="$(cursor-agent create-chat)"
  test -n "$chat_id" || { echo "error: cursor-agent create-chat returned no chat id" >&2; exit 4; }
  cursor-agent --model "$model" --trust --mode ask --workspace "$repo_root" --resume "$chat_id" \
    -p "Remember token $smoke_token. Return exactly: $ok_token" --output-format text > "$tmp_root/first"
  assert_token "first prompt" "$ok_token" "$tmp_root/first"
  cursor-agent --model "$model" --trust --mode ask --workspace "$repo_root" --resume "$chat_id" \
    -p "Return exactly the token you were asked to remember." --output-format text > "$tmp_root/resume"
  assert_token "resume" "$smoke_token" "$tmp_root/resume"
  printf 'reviewer: cursor\ncommand: cursor-agent\nmodel: %s\nchat_id: %s\npass: true\n' "$model" "$chat_id"
}

run_codex() {
  command -v codex >/dev/null 2>&1 || { echo "error: codex CLI not found on PATH" >&2; exit 3; }
  command -v jq >/dev/null 2>&1 || { echo "error: jq not found on PATH" >&2; exit 3; }
  local session_id model
  model="${CODEX_REVIEW_MODEL:-default}"
  if [ "$model" = "default" ]; then
    printf 'Remember token %s. Return exactly: %s\n' "$smoke_token" "$ok_token" |
      codex -C "$repo_root" -s read-only -a never exec --json \
        -o "$tmp_root/first" - > "$tmp_root/events"
  else
    printf 'Remember token %s. Return exactly: %s\n' "$smoke_token" "$ok_token" |
      codex -C "$repo_root" -s read-only -a never -m "$model" exec --json \
        -o "$tmp_root/first" - > "$tmp_root/events"
  fi
  assert_token "first prompt" "$ok_token" "$tmp_root/first"
  session_id="$(jq -r 'select(.type == "thread.started") | .thread_id // .thread.id // empty' "$tmp_root/events" | tail -n 1)"
  test -n "$session_id" || { echo "error: codex preflight returned no session id" >&2; exit 4; }
  if [ "$model" = "default" ]; then
    printf 'Return exactly the token you were asked to remember.\n' |
      codex -C "$repo_root" -s read-only -a never exec resume "$session_id" \
        --json -o "$tmp_root/resume" - > "$tmp_root/resume-events"
  else
    printf 'Return exactly the token you were asked to remember.\n' |
      codex -C "$repo_root" -s read-only -a never -m "$model" exec resume "$session_id" \
        --json -o "$tmp_root/resume" - > "$tmp_root/resume-events"
  fi
  assert_token "resume" "$smoke_token" "$tmp_root/resume"
  printf 'reviewer: codex\ncommand: codex\nmodel: %s\nsession_id: %s\npass: true\n' "$model" "$session_id"
}

case "$provider" in
  codex) run_codex ;;
  claude) run_claude ;;
  cursor) run_cursor ;;
  *) echo "error: provider must be codex, claude, or cursor: $provider" >&2; exit 2 ;;
esac
