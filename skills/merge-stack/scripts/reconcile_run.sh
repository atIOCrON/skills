#!/usr/bin/env bash
# Read-only recovery check for planned actions that lack a journaled completion.
set -euo pipefail

if [ "$#" -ne 3 ]; then
  echo "usage: reconcile_run.sh <provider> <remote> <journal>" >&2
  exit 2
fi

provider="$1"
remote="$2"
journal="$3"
script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"

[ -f "$journal" ] || {
  echo "error: journal not found: $journal" >&2
  exit 2
}
jq -se '.' "$journal" >/dev/null || {
  echo "error: journal is not valid JSON Lines" >&2
  exit 2
}

pending="$(jq -sc '
  reduce .[] as $e (
    {push:{}, merge:{}, retarget:{}, delete:{}};
    if $e.event == "force-push-planned" then .push[$e.branch] = $e
    elif $e.event == "force-pushed" then del(.push[$e.branch])
    elif $e.event == "merge-planned" then .merge[$e.change_id] = ($e + {submitted:false})
    elif $e.event == "merge-submitted" and .merge[$e.change_id] then
      .merge[$e.change_id].submitted = true
    elif $e.event == "merge-confirmed" then del(.merge[$e.change_id])
    elif $e.event == "retarget-planned" then .retarget[$e.change_id] = $e
    elif $e.event == "retargeted" then del(.retarget[$e.change_id])
    elif $e.event == "remote-branch-delete-planned" then .delete[$e.branch] = $e
    elif $e.event == "remote-branch-deleted" or $e.event == "remote-branch-already-deleted" then
      del(.delete[$e.branch])
    else . end
  ) |
  [.push[] | . + {action:"force-push"}] +
  [.merge[] | . + {action:"merge"}] +
  [.retarget[] | . + {action:"retarget"}] +
  [.delete[] | . + {action:"remote-delete"}]
' "$journal")"

blockers=0
while IFS= read -r item; do
  [ -n "$item" ] || continue
  action="$(printf '%s' "$item" | jq -r '.action')"
  case "$action" in
    force-push)
      branch="$(printf '%s' "$item" | jq -r '.branch')"
      lease="$(printf '%s' "$item" | jq -r '.lease_sha')"
      intended="$(printf '%s' "$item" | jq -r '.rebased_head_sha')"
      line="$(git ls-remote --heads "$remote" "refs/heads/$branch")"
      actual="${line%%[[:space:]]*}"
      if [ "$actual" = "$intended" ]; then status=applied-unrecorded
      elif [ "$actual" = "$lease" ]; then status=not-applied
      else status=blocker; blockers=$((blockers + 1)); fi
      jq -nc --arg action "$action" --arg branch "$branch" --arg status "$status" \
        --arg actual "$actual" '{action:$action,branch:$branch,status:$status,actual_sha:$actual}'
      ;;
    merge)
      id="$(printf '%s' "$item" | jq -r '.change_id')"
      expected_head="$(printf '%s' "$item" | jq -r '.head_sha')"
      expected_target="$(printf '%s' "$item" | jq -r '.target_branch')"
      submitted="$(printf '%s' "$item" | jq -r '.submitted')"
      change="$("$script_dir/provider.sh" "$provider" "$remote" get-change "$id")"
      if ! printf '%s' "$change" | jq -e --arg head "$expected_head" --arg target "$expected_target" \
        '.head_sha == $head and .target_branch == $target' >/dev/null; then
        status=blocker; blockers=$((blockers + 1))
      else
        state="$(printf '%s' "$change" | jq -r '.state')"
        if [ "$state" = merged ] || [ "$submitted" = true ]; then status=confirmation-required
        elif [ "$state" = open ]; then status=not-applied
        else status=blocker; blockers=$((blockers + 1)); fi
      fi
      jq -nc --arg action "$action" --arg id "$id" --arg status "$status" \
        '{action:$action,change_id:$id,status:$status}'
      ;;
    retarget)
      id="$(printf '%s' "$item" | jq -r '.change_id')"
      expected_head="$(printf '%s' "$item" | jq -r '.head_sha')"
      old_target="$(printf '%s' "$item" | jq -r '.old_target')"
      intended_target="$(printf '%s' "$item" | jq -r '.target_branch')"
      change="$("$script_dir/provider.sh" "$provider" "$remote" get-change "$id")"
      actual_head="$(printf '%s' "$change" | jq -r '.head_sha')"
      actual_target="$(printf '%s' "$change" | jq -r '.target_branch')"
      if [ "$actual_head" != "$expected_head" ]; then status=blocker; blockers=$((blockers + 1))
      elif [ "$actual_target" = "$intended_target" ]; then status=applied-unrecorded
      elif [ "$actual_target" = "$old_target" ]; then status=not-applied
      else status=blocker; blockers=$((blockers + 1)); fi
      jq -nc --arg action "$action" --arg id "$id" --arg status "$status" \
        --arg target "$actual_target" '{action:$action,change_id:$id,status:$status,actual_target:$target}'
      ;;
    remote-delete)
      branch="$(printf '%s' "$item" | jq -r '.branch')"
      expected="$(printf '%s' "$item" | jq -r '.expected_sha')"
      line="$(git ls-remote --heads "$remote" "refs/heads/$branch")"
      actual="${line%%[[:space:]]*}"
      if [ -z "$actual" ]; then status=applied-unrecorded
      elif [ "$actual" = "$expected" ]; then status=not-applied
      else status=blocker; blockers=$((blockers + 1)); fi
      jq -nc --arg action "$action" --arg branch "$branch" --arg status "$status" \
        --arg actual "$actual" '{action:$action,branch:$branch,status:$status,actual_sha:$actual}'
      ;;
  esac
done < <(printf '%s' "$pending" | jq -c '.[]')

[ "$blockers" -eq 0 ] || exit 4
