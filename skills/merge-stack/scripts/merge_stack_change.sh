#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 8 ] || [ "$#" -gt 9 ]; then
  echo "usage: merge_stack_change.sh <provider> <remote> <change-id> <head-sha> <target> <base-sha> <successor-id-or-null> <journal> [squash|merge-commit]" >&2
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
method="${9:-merge-commit}"
case "$method" in squash|merge-commit) ;; *) echo "error: unsupported merge method" >&2; exit 2 ;; esac
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
assert_field '.mergeability == "mergeable"' "change $change_id is not mergeable"

if ! printf '%s' "$change" | jq -e '.provider == "bitbucket-cloud"' >/dev/null; then
  assert_field '.target_protected == true' "target branch is not protected"
  assert_field '.target_policy_enforced == true' "target does not enforce up-to-date merge-result checks"
  assert_field '.review_status == "approved"' "change $change_id is not approved"
  assert_field '.approval_head_sha == $sha' "approval does not cover head $head_sha"
  if [ "$method" = squash ]; then
    assert_field '.squash_allowed == true' "squash merging is unavailable for change $change_id"
  else
    assert_field '.merge_commit_allowed == true' "merge commits are unavailable for change $change_id"
  fi
  assert_field '.checks_status == "passed"' "checks are not passing"
  assert_field '.checks_head_sha == $sha' "checks do not cover head $head_sha"
else
  [[ "$head_sha" =~ ^[0-9a-f]{40}$ && "$base_sha" =~ ^[0-9a-f]{40}$ ]] || {
    echo "error: release assembly requires full commit SHAs" >&2; exit 4;
  }
  jq -se --arg id "$change_id" --arg head "$head_sha" --arg target "$target" --arg method "$method" '
    any(.[]; .event == "merge-authorized" and .authorized_by == "user" and
      (.merge_method // "merge-commit") == $method and
      (.evidence | type == "string" and length > 0) and
      any(.changes[]?; .change_id == $id and .head_sha == $head and .target_branch == $target))
  ' "$journal" >/dev/null || {
    echo "error: user authorization does not cover this PR, head, and target" >&2; exit 4;
  }
  if [ "$method" = squash ]; then
    assert_field '.squash_allowed == true' "squash merging is unavailable"
  else
    assert_field '.merge_commit_allowed == true' "merge commits are unavailable"
  fi
  assert_field '.source_branch_auto_delete == false' "source retention is not confirmed"
  assert_field '.policy_status == "passed"' "configured merge checks or permissions are not satisfied"
  assert_field '(.checks_status == "passed" and .checks_head_sha == $sha) or .checks_status == "not-required"' \
    "required checks do not cover this head"
fi

"$script_dir/journal_event.sh" "$journal" merge-planned \
  "$(jq -nc --arg id "$change_id" --arg head "$head_sha" --arg target "$target" \
    --arg base "$base_sha" --arg successor "$successor_id" --arg method "$method" \
    '{change_id:$id,head_sha:$head,target_branch:$target,base_sha:$base,successor_id:$successor,merge_method:$method}')"
merge_args=("$change_id" "$head_sha" "$target" "$base_sha")
merge_args+=("$method")
result="$("$script_dir/provider.sh" "$provider" "$remote" merge "${merge_args[@]}")" || exit 5
printf '%s' "$result" | jq -e --arg method "$method" '
  (.status == "merged" or .status == "submitted") and
  .merge_method == $method' >/dev/null || {
    echo "error: provider did not confirm the requested merge method" >&2
    exit 5
  }
"$script_dir/journal_event.sh" "$journal" merge-submitted \
  "$(jq -nc --arg id "$change_id" --arg head "$head_sha" --arg status "$(printf '%s' "$result" | jq -r '.status')" \
    '{change_id:$id,head_sha:$head,status:$status}')"
echo "merge_status=$(printf '%s' "$result" | jq -r '.status')"
echo "merge_method=$method"
echo "landed_sha=$(printf '%s' "$result" | jq -r '.landed_sha // "null"')"
echo "source_branch_mode=preserve"
