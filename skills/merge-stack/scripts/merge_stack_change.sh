#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 8 ]; then
  echo "usage: merge_stack_change.sh <provider> <remote> <change-id> <head-sha> <target> <base-sha> <successor-id-or-null> <journal>" >&2
  exit 2
fi

provider="$1"
remote="$2"
change_id="$3"
head_sha="$4"
target="$5"
base_sha="$6"
successor_id="$7"
journal="$8"
script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"

case "$head_sha" in ''|*[!0-9a-fA-F]*) echo "error: head SHA must be hexadecimal" >&2; exit 2 ;; esac
case "$base_sha" in ''|*[!0-9a-fA-F]*) echo "error: base SHA must be hexadecimal" >&2; exit 2 ;; esac

change="$("$script_dir/provider.sh" "$provider" "$remote" get-change "$change_id")" || exit 3

assert_field() {
  local expression="$1" message="$2"
  printf '%s' "$change" | jq -e --arg sha "$head_sha" "$expression" >/dev/null || {
    echo "error: $message" >&2
    exit 4
  }
}

assert_field '.state == "open"' "change $change_id is not open"
assert_field '.head_sha == $sha' "change $change_id is not at reviewed head $head_sha"
printf '%s' "$change" | jq -e --arg target "$target" --arg base "$base_sha" \
  '.target_branch == $target and .base_sha == $base' >/dev/null || {
  echo "error: change $change_id target or base moved" >&2
  exit 4
}
assert_field '.cross_repository == false' "fork-based change requests are unsupported"
assert_field '.target_protected == true' "target branch is not protected"
assert_field '.target_policy_enforced == true' "target does not enforce up-to-date merge-result checks"
assert_field '.review_status == "approved"' "change $change_id is not approved"
assert_field '.approval_head_sha == $sha' "approval does not cover head $head_sha"
assert_field '.squash_allowed == true' "squash merging is unavailable for change $change_id"
assert_field '.mergeability == "mergeable"' "change $change_id is not mergeable"

assert_field '.checks_status == "passed"' "checks are not passing"
assert_field '.checks_head_sha == $sha' "checks do not cover head $head_sha"

"$script_dir/journal_event.sh" "$journal" merge-planned \
  "$(jq -nc --arg id "$change_id" --arg head "$head_sha" --arg target "$target" \
    --arg base "$base_sha" --arg successor "$successor_id" \
    '{change_id:$id,head_sha:$head,target_branch:$target,base_sha:$base,successor_id:$successor}')"
result="$("$script_dir/provider.sh" "$provider" "$remote" merge \
  "$change_id" "$head_sha" "$target" "$base_sha")" || exit 5
printf '%s' "$result" | jq -e '
  (.status == "merged" or .status == "submitted") and
  .merge_method == "squash"' >/dev/null || {
    echo "error: provider did not confirm a squash merge request" >&2
    exit 5
  }
"$script_dir/journal_event.sh" "$journal" merge-submitted \
  "$(jq -nc --arg id "$change_id" --arg head "$head_sha" --arg status "$(printf '%s' "$result" | jq -r '.status')" \
    '{change_id:$id,head_sha:$head,status:$status}')"
echo "merge_status=$(printf '%s' "$result" | jq -r '.status')"
echo "merge_method=squash"
echo "landed_sha=$(printf '%s' "$result" | jq -r '.landed_sha // "null"')"
echo "source_branch_mode=preserve"
