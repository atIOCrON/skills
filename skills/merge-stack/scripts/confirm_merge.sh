#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 7 ] || [ "$#" -gt 8 ]; then
  echo "usage: confirm_merge.sh <provider> <remote> <change-id> <head-sha> <target> <expected-base-sha> <journal> [squash|merge-commit]" >&2
  exit 2
fi

provider="$1"
remote="$2"
change_id="$3"
reviewed_head_sha="$4"
target="$5"
expected_base_sha="$6"
journal="$7"
method="${8:-merge-commit}"
case "$method" in squash|merge-commit) ;; *) echo "error: unsupported merge method" >&2; exit 2 ;; esac
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

if [ "$method" = squash ]; then
  landed_sha="$(printf '%s' "$change" | jq -r '.squash_commit_sha // .landed_sha')"
else
  landed_sha="$(printf '%s' "$change" | jq -r '.merge_commit_sha // .landed_sha')"
fi
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
  echo "error: merge landed on $landed_parent, expected $expected_base_sha" >&2
  exit 7
}
if [ "$method" = squash ]; then
  expected_tree="$(git rev-parse "${reviewed_head_sha}^{tree}")"
else
  parents="$(git show -s --format=%P "$landed_sha")"
  [ "$parents" = "$expected_base_sha $reviewed_head_sha" ] || {
    echo "error: merge parents differ from the pinned target and source" >&2; exit 7;
  }
  source="$(printf '%s' "$change" | jq -r '.source_branch')"
  [ "$(git rev-parse "$remote/$source")" = "$reviewed_head_sha" ] || {
    echo "error: source branch was deleted or moved" >&2; exit 7;
  }
  expected_tree="$(git merge-tree --write-tree "$expected_base_sha" "$reviewed_head_sha")" || {
    echo "error: cannot reproduce the merge tree; stop for conflict handling" >&2; exit 7;
  }
fi
[ "$(git rev-parse "${landed_sha}^{tree}")" = "$expected_tree" ] || {
  echo "error: landed tree differs from the expected merge result" >&2; exit 7;
}
"$script_dir/journal_event.sh" "$journal" merge-confirmed \
  "$(jq -nc --arg id "$change_id" --arg head "$reviewed_head_sha" --arg landed "$landed_sha" \
    --arg parent "$landed_parent" --arg method "$method" \
    '{change_id:$id,head_sha:$head,landed_sha:$landed,landed_parent_sha:$parent,merge_method:$method}')"

echo "merged_head_sha=$reviewed_head_sha"
echo "landed_sha=$landed_sha"
echo "landed_parent_sha=$landed_parent"
echo "target_head_sha=$(git rev-parse "$remote/$target")"
