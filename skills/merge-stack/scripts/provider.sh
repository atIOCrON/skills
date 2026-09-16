#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 3 ]; then
  echo "usage: provider.sh <provider|auto> <remote> <operation> [arguments...]" >&2
  exit 2
fi

provider="$1"
remote="$2"
shift 2
script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
provider_dir="${MERGE_STACK_PROVIDER_DIR:-$script_dir/providers}"

if [ "$provider" = auto ]; then
  remote_url="$(git remote get-url "$remote" 2>/dev/null)" || {
    echo "error: unknown remote: $remote" >&2
    exit 3
  }
  case "$remote_url" in
    *github.com[:/]*) provider=github ;;
    *gitlab.com[:/]*) provider=gitlab ;;
    *)
      echo "error: cannot infer provider from $remote_url; specify it explicitly" >&2
      exit 3
      ;;
  esac
fi

case "$provider" in
  ''|*[!a-z0-9-]*)
    echo "error: invalid provider name: $provider" >&2
    exit 3
    ;;
esac

adapter="$provider_dir/$provider.sh"
if [ ! -x "$adapter" ]; then
  echo "error: provider adapter is missing or not executable: $adapter" >&2
  exit 3
fi

exec "$adapter" "$remote" "$@"
