#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 7 ]; then
  echo "usage: confirm_squash_merge.sh <provider> <remote> <change-id> <reviewed-head-sha> <base-branch> <expected-base-sha> <journal>" >&2
  exit 2
fi

provider="$1"
remote="$2"
change_id="$3"
reviewed_head_sha="$4"
target="$5"
expected_base_sha="$6"
journal="$7"
interval="${MERGE_STACK_CONFIRM_INTERVAL:-3}"
max_wait="${MERGE_STACK_CONFIRM_WAIT:-120}"
script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"

case "$reviewed_head_sha" in ''|*[!0-9a-fA-F]*) echo "error: reviewed head SHA must be hexadecimal" >&2; exit 2 ;; esac
case "$expected_base_sha" in ''|*[!0-9a-fA-F]*) echo "error: expected base SHA must be hexadecimal" >&2; exit 2 ;; esac

elapsed=0
while :; do
  change="$("$script_dir/provider.sh" "$provider" "$remote" get-change "$change_id")" || {
    echo "error: cannot refresh change $change_id after merge" >&2
    exit 5
  }
  state="$(printf '%s' "$change" | jq -r '.state // "unknown"')"
  [ "$state" = merged ] && break
  if [ "$elapsed" -ge "$max_wait" ]; then
    echo "error: change $change_id did not merge within ${max_wait}s" >&2
    exit 6
  fi
  sleep "$interval"
  elapsed=$((elapsed + interval))
done

printf '%s' "$change" | jq -e --arg sha "$reviewed_head_sha" --arg target "$target" \
  '.head_sha == $sha and .target_branch == $target and (.landed_sha | type == "string" and length > 0)' >/dev/null || {
    echo "error: merged change does not match the reviewed head, target, or landed commit" >&2
    exit 6
  }

landed_sha="$(printf '%s' "$change" | jq -r '.landed_sha')"
git fetch --prune "$remote"
git rev-parse --verify --quiet "$remote/$target" >/dev/null || {
  echo "error: cannot resolve $remote/$target" >&2
  exit 7
}
git cat-file -e "${landed_sha}^{commit}" 2>/dev/null || {
  echo "error: cannot resolve landed commit $landed_sha" >&2
  exit 7
}
git merge-base --is-ancestor "$landed_sha" "$remote/$target" || {
  echo "error: landed commit $landed_sha is not in $remote/$target" >&2
  exit 7
}
landed_parent="$(git rev-parse "$landed_sha^")"
[ "$landed_parent" = "$expected_base_sha" ] || {
  echo "error: squash landed on $landed_parent, expected $expected_base_sha" >&2
  exit 7
}
git diff --quiet "${reviewed_head_sha}^{tree}" "${landed_sha}^{tree}" || {
  echo "error: landed squash tree differs from reviewed head" >&2
  exit 7
}
"$script_dir/journal_event.sh" "$journal" merge-confirmed \
  "$(jq -nc --arg id "$change_id" --arg head "$reviewed_head_sha" --arg landed "$landed_sha" \
    --arg parent "$landed_parent" '{change_id:$id,head_sha:$head,landed_sha:$landed,landed_parent_sha:$parent}')"

echo "merged_head_sha=$reviewed_head_sha"
echo "landed_sha=$landed_sha"
echo "landed_parent_sha=$landed_parent"
echo "target_head_sha=$(git rev-parse "$remote/$target")"
