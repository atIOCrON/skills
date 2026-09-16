#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 5 ]; then
  echo "usage: retarget_change.sh <provider> <remote> <change-id> <target> <journal>" >&2
  exit 2
fi

provider="$1"
remote="$2"
change_id="$3"
target="$4"
journal="$5"
script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"

before="$("$script_dir/provider.sh" "$provider" "$remote" get-change "$change_id")"
head="$(printf '%s' "$before" | jq -er '.head_sha')"
old_target="$(printf '%s' "$before" | jq -er '.target_branch')"
"$script_dir/journal_event.sh" "$journal" retarget-planned \
  "$(jq -nc --arg id "$change_id" --arg head "$head" --arg old "$old_target" --arg target "$target" \
    '{change_id:$id,head_sha:$head,old_target:$old,target_branch:$target}')"

"$script_dir/provider.sh" "$provider" "$remote" retarget "$change_id" "$target" >/dev/null
after="$("$script_dir/provider.sh" "$provider" "$remote" get-change "$change_id")"
printf '%s' "$after" | jq -e --arg head "$head" --arg target "$target" \
  '.state == "open" and .head_sha == $head and .target_branch == $target' >/dev/null || {
  echo "error: retargeted change does not match the expected head and target" >&2
  exit 4
}
"$script_dir/journal_event.sh" "$journal" retargeted \
  "$(jq -nc --arg id "$change_id" --arg head "$head" --arg target "$target" \
    '{change_id:$id,head_sha:$head,target_branch:$target}')"
