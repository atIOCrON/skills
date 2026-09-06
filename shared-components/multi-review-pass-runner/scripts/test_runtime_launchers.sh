#!/usr/bin/env bash
# Test all provider launch/resume paths with local stubs.
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/../../.." && pwd)"
tmp_root="$(mktemp -d)"
stub_bin="$tmp_root/home/.local/bin"
mkdir -p "$stub_bin"
trap 'rm -rf "$tmp_root"' EXIT

cat > "$stub_bin/codex" <<'STUB'
#!/usr/bin/env bash
set -euo pipefail
printf 'codex %s\n' "$*" >> "$STUB_ARGS_LOG"
prompt="$(cat)"
output=""
previous=""
for arg in "$@"; do
  if [ "$previous" = "-o" ]; then output="$arg"; break; fi
  previous="$arg"
done
case "$prompt" in
  *"Remember token"*) result="REVIEWER_SMOKE_OK" ;;
  *"Return exactly the token"*) result="ORCHESTRATE_SESSION_SMOKE" ;;
  *"CLOSURE"*) result="CODEX_CLOSURE_OK" ;;
  *) result="CODEX_REVIEW_OK" ;;
esac
printf '%s\n' "$result" > "$output"
printf '{"type":"thread.started","thread_id":"codex-session-1"}\n'
STUB

cat > "$stub_bin/claude" <<'STUB'
#!/usr/bin/env bash
set -euo pipefail
printf 'claude %s\n' "$*" >> "$STUB_ARGS_LOG"
prompt="$(cat) $*"
case "$prompt" in
  *"Remember token"*) echo "REVIEWER_SMOKE_OK" ;;
  *"Return exactly the token"*) echo "ORCHESTRATE_SESSION_SMOKE" ;;
  *"CLOSURE"*) echo "CLAUDE_CLOSURE_OK" ;;
  *) echo "CLAUDE_REVIEW_OK" ;;
esac
STUB

cat > "$stub_bin/cursor-agent" <<'STUB'
#!/usr/bin/env bash
set -euo pipefail
printf 'cursor %s\n' "$*" >> "$STUB_ARGS_LOG"
if [ "${1:-}" = "create-chat" ]; then echo "cursor-session-1"; exit 0; fi
prompt="$(cat) $*"
case "$prompt" in
  *"Remember token"*) echo "REVIEWER_SMOKE_OK" ;;
  *"Return exactly the token"*) echo "ORCHESTRATE_SESSION_SMOKE" ;;
  *"CLOSURE"*) echo "CURSOR_CLOSURE_OK" ;;
  *) echo "CURSOR_REVIEW_OK" ;;
esac
STUB

chmod +x "$stub_bin/codex" "$stub_bin/claude" "$stub_bin/cursor-agent"
export HOME="$tmp_root/home"
export PATH="$stub_bin:$PATH"
export STUB_ARGS_LOG="$tmp_root/args.log"

artifact_dir="$tmp_root/artifacts"
mkdir -p "$artifact_dir"
for provider in codex claude cursor; do
  printf 'REVIEW\n' > "$artifact_dir/$provider-prompt.md"
done

"$script_dir/launch_codex_review.sh" "$artifact_dir/codex-prompt.md" "$artifact_dir" "$repo_root"
"$script_dir/launch_claude_review.sh" "$artifact_dir/claude-prompt.md" "$artifact_dir"
"$script_dir/launch_cursor_review.sh" "$artifact_dir/cursor-prompt.md" "$artifact_dir" "$repo_root"

for provider in codex claude cursor; do
  test -s "$artifact_dir/$provider.md"
  test -s "$artifact_dir/$provider-session.md"
  printf 'CLOSURE\n' > "$artifact_dir/$provider-closure-prompt.md"
  "$script_dir/resume_review.sh" "$provider" "$artifact_dir/$provider-closure-prompt.md" "$artifact_dir" "$repo_root"
  test -s "$artifact_dir/$provider-closure.md"
done

"$repo_root/shared-components/reviewer-preflight/scripts/run_reviewer_preflight.sh" codex "$repo_root" >/dev/null
"$repo_root/shared-components/reviewer-preflight/scripts/run_reviewer_preflight.sh" claude "$repo_root" >/dev/null
"$repo_root/shared-components/reviewer-preflight/scripts/run_reviewer_preflight.sh" cursor "$repo_root" >/dev/null

grep -qF -- '-s read-only -a never' "$STUB_ARGS_LOG"
grep -qF -- '--permission-mode plan' "$STUB_ARGS_LOG"
grep -qF -- '--mode ask' "$STUB_ARGS_LOG"
grep -qF 'CODEX_CLOSURE_OK' "$artifact_dir/codex-closure.md"
grep -qF 'CLAUDE_CLOSURE_OK' "$artifact_dir/claude-closure.md"
grep -qF 'CURSOR_CLOSURE_OK' "$artifact_dir/cursor-closure.md"

echo "runtime launcher tests passed"
