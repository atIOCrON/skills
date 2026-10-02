#!/usr/bin/env bash
# Compatibility entrypoint for existing squash callers.
set -euo pipefail
script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
[ "$#" -eq 7 ] || { echo "usage: confirm_squash_merge.sh <provider> <remote> <id> <head> <target> <base> <journal>" >&2; exit 2; }
exec "$script_dir/confirm_merge.sh" "$@" squash
