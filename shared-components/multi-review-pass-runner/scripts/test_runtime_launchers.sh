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
  *"Preflight probe"*) result="REVIEWER_SMOKE_OK" ;;
  *"Run these read-only commands"*) result="ORCHESTRATE_SESSION_SMOKE $(git rev-parse HEAD)" ;;
  *"CLOSURE"*) result="CODEX_CLOSURE_OK" ;;
  *"Do not repeat the review"*) result=$'## Blockers\n- None\n\n## Should-fix\n- None\n\n## Nits\n- None\n\n## Contradictions\n- None\n\n## Related Existing Issues\n- None\n\n## Proportionality\n- Proportionate - no material concerns\n\n## Skill Feedback\n- None\n\nReview pass clean' ;;
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
  *"Preflight probe"*) echo "REVIEWER_SMOKE_OK" ;;
  *"Run these read-only commands"*) echo "ORCHESTRATE_SESSION_SMOKE $(git rev-parse HEAD)" ;;
  *"CLOSURE"*) echo "CLAUDE_CLOSURE_OK" ;;
  *"EMPTY_INITIAL"*) : ;;
  *"Do not repeat the review"*) printf '%s\n' '## Blockers' '- None' '' '## Should-fix' '- None' '' '## Nits' '- None' '' '## Contradictions' '- None' '' '## Related Existing Issues' '- None' '' '## Proportionality' '- Proportionate - no material concerns' '' '## Skill Feedback' '- None' '' 'Review pass clean' ;;
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
  *"Preflight probe"*) echo "REVIEWER_SMOKE_OK" ;;
  *"Run these read-only commands"*) echo "ORCHESTRATE_SESSION_SMOKE $(git rev-parse HEAD)" ;;
  *"CLOSURE"*) echo "CURSOR_CLOSURE_OK" ;;
  *"Do not repeat the review"*) printf '%s\n' '## Blockers' '- None' '' '## Should-fix' '- None' '' '## Nits' '- None' '' '## Contradictions' '- None' '' '## Related Existing Issues' '- None' '' '## Proportionality' '- Proportionate - no material concerns' '' '## Skill Feedback' '- None' '' 'Review pass clean' ;;
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

for provider in codex claude cursor; do
  repair_dir="$tmp_root/code-review-pass2/$provider"
  mkdir -p "$repair_dir"
  printf 'REVIEW\n' > "$repair_dir/$provider-prompt.md"
  case "$provider" in
    codex) "$script_dir/launch_codex_review.sh" "$repair_dir/$provider-prompt.md" "$repair_dir" "$repo_root" ;;
    claude) "$script_dir/launch_claude_review.sh" "$repair_dir/$provider-prompt.md" "$repair_dir" ;;
    cursor) "$script_dir/launch_cursor_review.sh" "$repair_dir/$provider-prompt.md" "$repair_dir" "$repo_root" ;;
  esac
  "$script_dir/repair_code_review_output.sh" "$provider" "$repair_dir" "$repo_root" 2
  test -s "$repair_dir/$provider-raw-attempt1.md"
  test -s "$repair_dir/$provider-format-repair-round1-prompt.md"
  test -s "$repair_dir/$provider-format-repair-round1.md"
  grep -qF 'classification: valid' "$repair_dir/$provider-format-repair-round1-validation.md"
  grep -qF 'Review pass clean' "$repair_dir/$provider.md"
done

validator="$script_dir/validate_code_review_output.py"
valid_review="$tmp_root/code-review-pass2/cursor/cursor.md"
python3 "$validator" "$valid_review" cursor 2 >/dev/null

printf 'Preamble\n' > "$tmp_root/format-invalid.md"
sed -n '1,$p' "$valid_review" >> "$tmp_root/format-invalid.md"
set +e
python3 "$validator" "$tmp_root/format-invalid.md" cursor 2 > "$tmp_root/format-invalid-validation.md"
validation_exit=$?
set -e
test "$validation_exit" -eq 10
grep -qF 'classification: format-repairable' "$tmp_root/format-invalid-validation.md"

grep -vF '## Skill Feedback' "$valid_review" > "$tmp_root/completion-invalid.md"
set +e
python3 "$validator" "$tmp_root/completion-invalid.md" cursor 2 > "$tmp_root/completion-invalid-validation.md"
validation_exit=$?
set -e
test "$validation_exit" -eq 11
grep -qF 'classification: completion-repairable' "$tmp_root/completion-invalid-validation.md"

empty_dir="$tmp_root/code-review-pass3/claude"
mkdir -p "$empty_dir"
printf 'EMPTY_INITIAL\n' > "$empty_dir/claude-prompt.md"
set +e
"$script_dir/launch_claude_review.sh" "$empty_dir/claude-prompt.md" "$empty_dir"
empty_launch_exit=$?
set -e
test "$empty_launch_exit" -eq 5
"$script_dir/repair_code_review_output.sh" claude "$empty_dir" "$repo_root" 3
empty_session_id="$(sed -nE 's/^- session_id: (.*)$/\1/p' "$empty_dir/claude-session.md")"
grep -qF -- "--resume $empty_session_id" "$STUB_ARGS_LOG"
grep -qF 'Review pass clean' "$empty_dir/claude.md"

"$script_dir/launch_codex_review.sh" "$artifact_dir/codex-prompt.md" "$artifact_dir" "$repo_root"
"$script_dir/launch_claude_review.sh" "$artifact_dir/claude-prompt.md" "$artifact_dir"
"$script_dir/launch_cursor_review.sh" "$artifact_dir/cursor-prompt.md" "$artifact_dir" "$repo_root"

for provider in codex claude cursor; do
  test -s "$artifact_dir/$provider-raw-attempt1.md"
  test -s "$artifact_dir/$provider-session.md"
  printf 'CLOSURE\n' > "$artifact_dir/$provider-closure-prompt.md"
  "$script_dir/resume_review.sh" "$provider" "$artifact_dir/$provider-closure-prompt.md" "$artifact_dir" "$repo_root"
  test -s "$artifact_dir/$provider-closure.md"
  "$script_dir/resume_review.sh" "$provider" "$artifact_dir/$provider-closure-prompt.md" "$artifact_dir" "$repo_root" closure-round2
  test -s "$artifact_dir/$provider-closure-round2.md"
done

preflight_script="$script_dir/run_reviewer_preflight.sh"
if [ ! -x "$preflight_script" ]; then
  preflight_script="$repo_root/shared-components/reviewer-preflight/scripts/run_reviewer_preflight.sh"
fi
"$preflight_script" codex "$repo_root" >/dev/null
"$preflight_script" claude "$repo_root" >/dev/null
"$preflight_script" cursor "$repo_root" >/dev/null

grep -qF -- '-s read-only -a never' "$STUB_ARGS_LOG"
grep -qF -- '--permission-mode plan' "$STUB_ARGS_LOG"
grep -qF -- '--auto-review --sandbox enabled' "$STUB_ARGS_LOG"
grep -qF -- '--model grok-4.7-high' "$STUB_ARGS_LOG"
if grep -qF -- '--mode ask' "$STUB_ARGS_LOG"; then
  echo "cursor launchers must use default agent mode, not ask mode" >&2
  exit 1
fi
grep -qF 'CODEX_CLOSURE_OK' "$artifact_dir/codex-closure.md"
grep -qF 'CLAUDE_CLOSURE_OK' "$artifact_dir/claude-closure.md"
grep -qF 'CURSOR_CLOSURE_OK' "$artifact_dir/cursor-closure.md"

echo "runtime launcher tests passed"
