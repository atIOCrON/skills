#!/usr/bin/env bash
# Resolve glab and jq for the calling shell, falling back to Homebrew's
# shellenv when the invoking shell did not load the user's profile. A child
# process cannot mutate its parent's PATH, so run this as
#   eval "$(.agents/skills/<skill>/scripts/ensure_glab.sh)"
# at the start of every shell invocation that uses glab. Emits an
# `export PATH=...` line on stdout; prints diagnostics and the resolved glab
# path on stderr.
# Exit codes: 2 = glab unavailable, 3 = jq unavailable.
set -euo pipefail

if ! command -v glab >/dev/null 2>&1; then
  if [ -x /opt/homebrew/bin/brew ]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
  fi
fi

if ! command -v glab >/dev/null 2>&1; then
  echo "error: glab not found on PATH (Homebrew shellenv fallback checked)" >&2
  exit 2
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "error: jq not found on PATH" >&2
  exit 3
fi

command -v glab >&2
printf 'export PATH=%q\n' "$PATH"
