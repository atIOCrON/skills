#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "usage: github.sh <remote> <operation> [arguments...]" >&2
  exit 2
fi

remote="$1"
operation="$2"
shift 2
script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
# shellcheck source=common.bash
. "$script_dir/common.bash"

require_command gh
require_command jq
load_remote "$remote"
repo="$PROVIDER_HOST/$PROVIDER_PATH"

get_change() {
  local selector="$1" pr settings reviews target_id target status_policy
  pr="$(gh pr view "$selector" -R "$repo" --json number,url,state,headRefName,headRefOid,baseRefName,baseRefOid,reviewDecision,latestReviews,mergeable,mergeStateStatus,statusCheckRollup,mergeCommit,isCrossRepository)" ||
    die "cannot resolve GitHub pull request: $selector"
  settings="$(gh repo view "$repo" --json squashMergeAllowed,deleteBranchOnMerge)" || die "cannot read GitHub repository settings"
  reviews="$(gh api --hostname "$PROVIDER_HOST" --paginate --slurp \
    "repos/$PROVIDER_PATH/pulls/$(printf '%s' "$pr" | jq -r '.number')/reviews?per_page=100" | jq 'add // []')" ||
    die "cannot read GitHub pull request reviews"
  target_id="$(printf '%s' "$(printf '%s' "$pr" | jq -r '.baseRefName')" | jq -sRr @uri)"
  target="$(gh api --hostname "$PROVIDER_HOST" "repos/$PROVIDER_PATH/branches/$target_id")" ||
    die "cannot read GitHub target branch protection"
  status_policy="$(gh api --hostname "$PROVIDER_HOST" \
    "repos/$PROVIDER_PATH/branches/$target_id/protection/required_status_checks")" ||
    die "target branch lacks readable required-status-check protection"

  jq -n --argjson pr "$pr" --argjson settings "$settings" --argjson reviews "$reviews" \
    --argjson target "$target" --argjson status_policy "$status_policy" '
    def state:
      if . == "OPEN" then "open"
      elif . == "MERGED" then "merged"
      elif . == "CLOSED" then "closed"
      else "unknown" end;
    def review:
      if .reviewDecision == "APPROVED" then "approved"
      elif .reviewDecision == "CHANGES_REQUESTED" then "blocked"
      elif .reviewDecision == "REVIEW_REQUIRED" then "pending"
      elif any(.latestReviews[]?; .state == "CHANGES_REQUESTED") then "blocked"
      elif any(.latestReviews[]?; .state == "APPROVED") then "approved"
      elif (.latestReviews | length) > 0 then "pending"
      else "unknown" end;
    def effective_reviews:
      reduce ($reviews | sort_by(.submitted_at // "", .id // 0)[]) as $review
        ({}; .[$review.user.login] = $review) | [.[]];
    def approval_head:
      [effective_reviews[] | select(.state == "APPROVED")] as $approvals |
      if .reviewDecision == "APPROVED" and ($approvals | length) > 0 and
        all($approvals[]; .commit_id == $pr.headRefOid)
      then $pr.headRefOid else null end;
    def check_value: (.conclusion // .state // .status // "UNKNOWN") | ascii_upcase;
    def checks:
      if length == 0 then "missing"
      elif any(.[]; (check_value == "FAILURE" or check_value == "ERROR" or check_value == "CANCELLED" or check_value == "TIMED_OUT" or check_value == "ACTION_REQUIRED" or check_value == "STALE" or check_value == "STARTUP_FAILURE" or check_value == "SKIPPED")) then "failed"
      elif any(.[]; (check_value == "PENDING" or check_value == "EXPECTED" or check_value == "QUEUED" or check_value == "IN_PROGRESS" or check_value == "WAITING" or check_value == "REQUESTED")) then "pending"
      elif all(.[]; (check_value == "SUCCESS" or check_value == "COMPLETED" or check_value == "NEUTRAL")) then "passed"
      else "unknown" end;
    def mergeability:
      if .mergeable == "CONFLICTING" or .mergeStateStatus == "DIRTY" then "conflict"
      elif .mergeStateStatus == "BEHIND" then "stale"
      elif .mergeable == "UNKNOWN" or .mergeStateStatus == "UNKNOWN" then "checking"
      elif .mergeStateStatus == "BLOCKED" then "blocked"
      elif .mergeable == "MERGEABLE" then "mergeable"
      else "unknown" end;
    {
      provider: "github",
      id: ($pr.number | tostring),
      url: $pr.url,
      state: ($pr.state | state),
      source_branch: $pr.headRefName,
      target_branch: $pr.baseRefName,
      head_sha: $pr.headRefOid,
      base_sha: $pr.baseRefOid,
      target_protected: ($target.protected == true),
      target_policy_enforced: ($status_policy.strict == true),
      review_status: ($pr | review),
      approval_head_sha: ($pr | approval_head),
      checks_status: ($pr.statusCheckRollup | checks),
      checks_head_sha: $pr.headRefOid,
      mergeability: ($pr | mergeability),
      squash_allowed: ($settings.squashMergeAllowed == true),
      cross_repository: ($pr.isCrossRepository == true),
      source_branch_auto_delete: ($settings.deleteBranchOnMerge == true),
      landed_sha: ($pr.mergeCommit.oid // null)
    }'
}

case "$operation" in
  auth-check)
    gh auth status --hostname "$PROVIDER_HOST" >/dev/null
    echo '{"provider":"github","authenticated":true}'
    ;;
  get-change)
    [ "$#" -eq 1 ] || die "usage: get-change <branch|url|id>"
    get_change "$1"
    ;;
  list-by-target)
    [ "$#" -eq 1 ] || die "usage: list-by-target <branch>"
    gh pr list -R "$repo" --base "$1" --state open --limit 100 \
      --json number,url,headRefName,baseRefName |
      jq '[.[] | {
        id: (.number | tostring),
        url,
        source_branch: .headRefName,
        target_branch: .baseRefName
      }]'
    ;;
  retarget)
    [ "$#" -eq 2 ] || die "usage: retarget <id> <branch>"
    gh pr edit "$1" -R "$repo" --base "$2" >/dev/null
    jq -n --arg id "$1" --arg target "$2" '{id: $id, target_branch: $target}'
    ;;
  merge)
    [ "$#" -eq 4 ] || die "usage: merge <id> <head-sha> <target> <base-sha>"
    id="$1"
    head_sha="$2"
    target="$3"
    base_sha="$4"
    require_sha "$head_sha" "expected head"
    require_sha "$base_sha" "expected base"
    change="$(get_change "$id")"
    printf '%s' "$change" | jq -e --arg head "$head_sha" --arg target "$target" --arg base "$base_sha" \
      '
        .state == "open" and .head_sha == $head and .target_branch == $target and
        .base_sha == $base and .review_status == "approved" and
        .approval_head_sha == $head and .target_protected == true and
        .target_policy_enforced == true and
        .mergeability == "mergeable" and
        .squash_allowed == true and .cross_repository == false and
        .checks_status == "passed" and .checks_head_sha == $head' >/dev/null ||
      die "GitHub pull request $id failed the exact-head, target, approval, checks, or mergeability gate"
    [ "$(printf '%s' "$change" | jq -r '.source_branch_auto_delete')" = false ] ||
      die "GitHub auto-deletes merged branches; disable it before this workflow"
    result="$(GH_REPO="$repo" gh api -X PUT "repos/{owner}/{repo}/pulls/$id/merge" \
      -f sha="$head_sha" -f merge_method=squash)" || die "GitHub failed to merge pull request $id"
    printf '%s' "$result" | jq -e '.merged == true and (.sha | type == "string")' >/dev/null ||
      die "GitHub did not confirm an immediate squash merge for pull request $id"
    printf '%s' "$result" | jq '{status: "merged", merge_method: "squash", landed_sha: .sha}'
    ;;
  *) die "unsupported GitHub operation: $operation" ;;
esac
