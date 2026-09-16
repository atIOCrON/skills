#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 5 ]; then
  echo "usage: delete_branch_if_unreferenced.sh <provider> <remote> <source-branch> <expected-sha> <journal>" >&2
  exit 2
fi

provider="$1"
remote="$2"
source_branch="$3"
expected_sha="$4"
journal="$5"
script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"

case "$expected_sha" in
  ''|*[!0-9a-fA-F]*) echo "error: expected SHA must be hexadecimal" >&2; exit 2 ;;
esac
git check-ref-format --branch "$source_branch" >/dev/null || {
  echo "error: invalid source branch: $source_branch" >&2
  exit 2
}

open_changes() {
  "$script_dir/provider.sh" "$provider" "$remote" list-by-target "$source_branch"
}

changes="$(open_changes)" || {
  echo "error: cannot query changes targeting $source_branch" >&2
  exit 4
}
count="$(printf '%s' "$changes" | jq -r 'length')"
[ "$count" -eq 0 ] || {
  echo "error: cannot delete $source_branch; open changes still target it:" >&2
  printf '%s' "$changes" | jq -r '.[] | "  id=\(.id) source=\(.source_branch)"' >&2
  exit 5
}

remote_line="$(git ls-remote --heads "$remote" "refs/heads/$source_branch")"
if [ -z "$remote_line" ]; then
  "$script_dir/journal_event.sh" "$journal" remote-branch-already-deleted \
    "$(jq -nc --arg branch "$source_branch" --arg expected "$expected_sha" \
      '{branch:$branch,expected_sha:$expected}')"
  echo "already_deleted_branch=$source_branch"
  exit 0
fi
remote_sha="${remote_line%%[[:space:]]*}"
[ "$remote_sha" = "$expected_sha" ] || {
  echo "error: $remote/$source_branch moved to $remote_sha; expected $expected_sha" >&2
  exit 6
}

# Close the provider-query race as far as the APIs allow. The SHA lease below
# independently rejects a source-branch update between this query and deletion.
changes="$(open_changes)" || {
  echo "error: cannot recheck changes targeting $source_branch" >&2
  exit 4
}
count="$(printf '%s' "$changes" | jq -r 'length')"
[ "$count" -eq 0 ] || {
  echo "error: cannot delete $source_branch; an open change now targets it" >&2
  exit 5
}

"$script_dir/journal_event.sh" "$journal" remote-branch-delete-planned \
  "$(jq -nc --arg branch "$source_branch" --arg expected "$expected_sha" \
    '{branch:$branch,expected_sha:$expected}')"
git push --force-with-lease="refs/heads/$source_branch:$expected_sha" \
  "$remote" ":refs/heads/$source_branch" || {
  echo "error: remote rejected deletion of $source_branch" >&2
  exit 7
}
"$script_dir/journal_event.sh" "$journal" remote-branch-deleted \
  "$(jq -nc --arg branch "$source_branch" --arg expected "$expected_sha" \
    '{branch:$branch,expected_sha:$expected}')"
echo "deleted_branch=$source_branch"
