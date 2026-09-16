#!/usr/bin/env bash
# Resolve the selected forge CLI and jq, falling back to Homebrew's
# shellenv when the invoking shell did not load the user's profile. A child
# process cannot mutate its parent's PATH, so run this as
#   eval "$(scripts/ensure_forge_cli.sh gitlab)"
# or
#   eval "$(scripts/ensure_forge_cli.sh github)"
# at the start of every shell invocation that uses the provider CLI. Emits an
# `export PATH=...` line on stdout and diagnostics on stderr.
# Exit codes: 2 = unsupported provider or CLI unavailable, 3 = jq unavailable.
set -euo pipefail

provider="${1:-}"
case "$provider" in
  gitlab) cli="glab" ;;
  github) cli="gh" ;;
  *)
    echo "usage: ensure_forge_cli.sh <gitlab|github>" >&2
    exit 2
    ;;
esac

if ! command -v "$cli" >/dev/null 2>&1; then
  if [ -x /opt/homebrew/bin/brew ]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
  fi
fi

if ! command -v "$cli" >/dev/null 2>&1; then
  echo "error: $cli not found on PATH (Homebrew shellenv fallback checked)" >&2
  exit 2
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "error: jq not found on PATH" >&2
  exit 3
fi

command -v "$cli" >&2
printf 'export PATH=%q\n' "$PATH"
