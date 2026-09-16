#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "usage: gitlab.sh <remote> <operation> [arguments...]" >&2
  exit 2
fi

remote="$1"
operation="$2"
shift 2
script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
# shellcheck source=common.bash
. "$script_dir/common.bash"

require_command glab
require_command jq
load_remote "$remote"
project_id="$(printf '%s' "$PROVIDER_PATH" | jq -sRr @uri)"

api() {
  glab api --hostname "$PROVIDER_HOST" "projects/$project_id/$1" "${@:2}"
}

get_change() {
  local selector="$1" view id mr approvals settings project target_id target
  view="$(glab mr view "$selector" -R "$PROVIDER_URL" --output json)" || die "cannot resolve GitLab merge request: $selector"
  id="$(printf '%s' "$view" | jq -r '.iid // empty')"
  [ -n "$id" ] || die "GitLab returned no merge request IID for $selector"
  mr="$(api "merge_requests/$id")" || die "cannot read GitLab merge request $id"
  approvals="$(api "merge_requests/$id/approvals")" || die "cannot read approvals for GitLab merge request $id"
  settings="$(api approvals)" || die "cannot read GitLab approval settings"
  project="$(glab api --hostname "$PROVIDER_HOST" "projects/$project_id")" || die "cannot read GitLab project settings"
  target_id="$(printf '%s' "$(printf '%s' "$mr" | jq -r '.target_branch')" | jq -sRr @uri)"
  target="$(api "repository/branches/$target_id")" || die "cannot read GitLab target branch"

  jq -n --argjson mr "$mr" --argjson approvals "$approvals" \
    --argjson settings "$settings" --argjson project "$project" --argjson target "$target" '
    def state:
      if . == "opened" then "open"
      elif . == "merged" then "merged"
      elif . == "closed" then "closed"
      else "unknown" end;
    def checks:
      if . == "success" then "passed"
      elif . == null or . == "" then "missing"
      elif . == "failed" or . == "canceled" or . == "cancelled" or . == "skipped" then "failed"
      elif . == "created" or . == "pending" or . == "preparing" or . == "running" or . == "waiting_for_resource" then "pending"
      else "unknown" end;
    def mergeability:
      if . == "mergeable" or . == "can_be_merged" then "mergeable"
      elif . == "conflict" then "conflict"
      elif . == "need_rebase" or . == "not_open" then "stale"
      elif . == "checking" or . == "approvals_syncing" or . == "unchecked" then "checking"
      elif . == "blocked_status" or . == "ci_must_pass" or . == "ci_still_running" or . == "discussions_not_resolved" or . == "draft_status" then "blocked"
      else "unknown" end;
    {
      provider: "gitlab",
      id: ($mr.iid | tostring),
      url: ($mr.web_url // ""),
      state: ($mr.state | state),
      source_branch: ($mr.source_branch // ""),
      target_branch: ($mr.target_branch // ""),
      head_sha: ($mr.sha // ""),
      base_sha: ($target.commit.id // ""),
      target_protected: ($target.protected == true),
      target_policy_enforced: (
        $target.protected == true and
        $project.only_allow_merge_if_pipeline_succeeds == true and
        $project.merge_pipelines_enabled == true
      ),
      review_status: (if $approvals.approved == true then "approved" else "pending" end),
      approval_head_sha: (if $approvals.approved == true and
        $settings.reset_approvals_on_push == true and
        $settings.merge_requests_disable_committers_approval == true
        then ($mr.sha // null) else null end),
      checks_status: (($mr.head_pipeline.status // null) | checks),
      checks_head_sha: ($mr.head_pipeline.sha // null),
      mergeability: (($mr.detailed_merge_status // $mr.merge_status // null) | mergeability),
      squash_allowed: ($mr.squash_on_merge == true),
      cross_repository: (($mr.source_project_id // $mr.target_project_id) != ($mr.target_project_id // $mr.source_project_id)),
      landed_sha: ($mr.squash_commit_sha // null)
    }'
}

case "$operation" in
  auth-check)
    glab auth status --hostname "$PROVIDER_HOST" >/dev/null
    echo '{"provider":"gitlab","authenticated":true}'
    ;;
  get-change)
    [ "$#" -eq 1 ] || die "usage: get-change <branch|url|id>"
    get_change "$1"
    ;;
  list-by-target)
    [ "$#" -eq 1 ] || die "usage: list-by-target <branch>"
    glab mr list -R "$PROVIDER_URL" --target-branch "$1" --output json |
      jq '[.[] | {
        id: ((.iid // .number) | tostring),
        url: (.web_url // .webUrl // .url // ""),
        source_branch: (.source_branch // .sourceBranch // ""),
        target_branch: (.target_branch // .targetBranch // "")
      }]'
    ;;
  retarget)
    [ "$#" -eq 2 ] || die "usage: retarget <id> <branch>"
    glab mr update "$1" -R "$PROVIDER_URL" --target-branch "$2" --yes >/dev/null
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
    validate_change() {
      local change="$1"
      printf '%s' "$change" | jq -e --arg head "$head_sha" --arg target "$target" --arg base "$base_sha" \
        '
          .state == "open" and .head_sha == $head and .target_branch == $target and
          .base_sha == $base and .review_status == "approved" and
          .approval_head_sha == $head and .target_protected == true and
          .target_policy_enforced == true and
          .mergeability == "mergeable" and
          .squash_allowed == true and .cross_repository == false and
          .checks_status == "passed" and .checks_head_sha == $head' >/dev/null ||
        die "GitLab merge request $id failed the exact-head, target, approval, checks, or mergeability gate"
    }
    change="$(get_change "$id")"
    validate_change "$change"
    api "merge_requests/$id" -X PUT -F remove_source_branch=false >/dev/null ||
      die "cannot clear source-branch removal for GitLab merge request $id"
    mr="$(api "merge_requests/$id")" || die "cannot verify source-branch handling for GitLab merge request $id"
    printf '%s' "$mr" | jq -e '(.should_remove_source_branch != true) and (.force_remove_source_branch != true)' >/dev/null ||
      die "GitLab may remove the source branch; disable removal before this workflow"
    validate_change "$(get_change "$id")"
    glab mr merge "$id" -R "$PROVIDER_URL" --sha "$head_sha" --squash --auto-merge=false --yes >/dev/null ||
      die "GitLab failed to merge change $id"
    jq -n '{status: "submitted", merge_method: "squash", landed_sha: null}'
    ;;
  *) die "unsupported GitLab operation: $operation" ;;
esac
