#!/usr/bin/env bash
# Confirm that an MR merged from the reviewed head with squash enabled and that
# GitLab's resulting squash commit landed in the expected target branch.
# Exit codes: 2 = usage, 3 = glab/jq unavailable, 4 = invalid arguments,
# 5 = GitLab API query failed, 6 = MR metadata mismatch or merge not complete,
# 7 = target branch or landed squash commit cannot be verified.
set -euo pipefail

if [ "$#" -ne 3 ]; then
  echo "usage: confirm_squash_merge.sh <mr-iid> <reviewed-head-sha> <base-target-branch>" >&2
  exit 2
fi

mr_iid="$1"
reviewed_head_sha="$2"
target="$3"
script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"

if ! eval "$("$script_dir/ensure_glab.sh")"; then
  exit 3
fi

case "$mr_iid" in
  ''|*[!0-9]*)
    echo "error: MR IID must be numeric" >&2
    exit 4
    ;;
esac
case "$reviewed_head_sha" in
  ''|*[!0-9a-fA-F]*)
    echo "error: reviewed head SHA must be hexadecimal" >&2
    exit 4
    ;;
esac
if [ -z "$target" ]; then
  echo "error: base target branch must not be empty" >&2
  exit 4
fi

mr_json=""
attempt=1
while [ "$attempt" -le 20 ]; do
  if ! mr_json="$(glab api "projects/:id/merge_requests/$mr_iid")"; then
    echo "error: failed to refresh MR $mr_iid after merge" >&2
    exit 5
  fi
  if printf '%s\n' "$mr_json" | jq -e '.state == "merged"' >/dev/null; then
    break
  fi
  if [ "$attempt" -eq 20 ]; then
    echo "error: MR $mr_iid did not reach merged state within 60 seconds" >&2
    exit 6
  fi
  sleep 3
  attempt=$((attempt + 1))
done

if ! printf '%s\n' "$mr_json" |
  jq -e --arg sha "$reviewed_head_sha" --arg target "$target" \
    '.sha == $sha and .target_branch == $target and .squash_on_merge == true' >/dev/null; then
  echo "error: merged MR $mr_iid does not match reviewed head $reviewed_head_sha, target $target, and effective squash-on-merge=true" >&2
  exit 6
fi

squash_commit_sha="$(printf '%s\n' "$mr_json" | jq -r '.squash_commit_sha // empty')"
merge_commit_sha="$(printf '%s\n' "$mr_json" | jq -r '.merge_commit_sha // empty')"
if [ -z "$squash_commit_sha" ]; then
  echo "error: merged MR $mr_iid has no squash_commit_sha" >&2
  exit 6
fi

git fetch --prune origin
if ! git rev-parse --verify --quiet "origin/$target" >/dev/null; then
  echo "error: cannot resolve origin/$target after MR $mr_iid merged" >&2
  exit 7
fi
if ! git cat-file -e "${squash_commit_sha}^{commit}" 2>/dev/null; then
  echo "error: cannot resolve squash commit $squash_commit_sha locally" >&2
  exit 7
fi
if ! git merge-base --is-ancestor "$squash_commit_sha" "origin/$target"; then
  echo "error: squash commit $squash_commit_sha is not in origin/$target" >&2
  exit 7
fi

echo "merged_head_sha=$reviewed_head_sha"
echo "squash_commit_sha=$squash_commit_sha"
echo "merge_commit_sha=${merge_commit_sha:-null}"
echo "landed_sha=$squash_commit_sha"
echo "target_head_sha=$(git rev-parse "origin/$target")"
