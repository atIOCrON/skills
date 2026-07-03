#!/usr/bin/env bash
# Delete a remote branch only after GitLab confirms no open MR targets it.
# Exit codes: 0 = deleted, 2 = usage, 3 = glab/jq unavailable,
# 4 = GitLab query failed, 5 = branch still targeted, 6 = delete failed.
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "usage: delete_branch_if_unreferenced.sh <source-branch>" >&2
  exit 2
fi

source_branch="$1"
script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"

if ! eval "$("$script_dir/ensure_glab.sh")"; then
  exit 3
fi

if ! target_json="$(glab mr list --target-branch "$source_branch" --output json)"; then
  echo "error: failed to query open MRs targeting $source_branch" >&2
  exit 4
fi

target_count="$(printf '%s\n' "$target_json" | jq -r 'length')"
if [ "$target_count" -ne 0 ]; then
  echo "error: cannot delete $source_branch; open MRs still target it:" >&2
  printf '%s\n' "$target_json" | jq -r '.[] | "  iid=\(.iid) source=\(.source_branch // .sourceBranch // "unknown")"' >&2
  exit 5
fi

if ! git push origin --delete "$source_branch"; then
  echo "error: GitLab rejected deletion of $source_branch" >&2
  exit 6
fi

echo "deleted_branch=$source_branch"
