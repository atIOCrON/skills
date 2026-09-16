#!/usr/bin/env bash
set -euo pipefail

remote="$1"
operation="$2"
shift 2

case "$operation" in
  auth-check) echo '{"provider":"test","authenticated":true}' ;;
  get-change)
    target="${FAKE_TARGET:-develop}"
    if [ -n "${FAKE_TARGET_FILE:-}" ] && [ -f "$FAKE_TARGET_FILE" ]; then
      target="$(<"$FAKE_TARGET_FILE")"
    fi
    jq -n \
      --arg id "$1" \
      --arg head "${FAKE_HEAD:?}" \
      --arg state "${FAKE_STATE:-open}" \
      --arg review "${FAKE_REVIEW:-approved}" \
      --arg approval_head "${FAKE_APPROVAL_HEAD:-$FAKE_HEAD}" \
      --arg target "$target" \
      --arg base "${FAKE_BASE:-$FAKE_HEAD}" \
      --arg checks "${FAKE_CHECKS:-passed}" \
      --arg checks_head "${FAKE_CHECKS_HEAD:-$FAKE_HEAD}" \
      --argjson protected "${FAKE_PROTECTED:-true}" \
      --argjson policy "${FAKE_TARGET_POLICY:-true}" \
      --arg landed "${FAKE_LANDED:-}" \
      '{provider:"test", id:$id, url:"https://example.test/change/1", state:$state,
        source_branch:"first", target_branch:$target, head_sha:$head, base_sha:$base,
        target_protected:$protected, target_policy_enforced:$policy,
        review_status:$review,
        approval_head_sha:(if $review == "approved" then $approval_head else null end),
        checks_status:$checks,
        checks_head_sha:(if $checks == "passed" then $checks_head else null end),
        mergeability:"mergeable",
        squash_allowed:true, cross_repository:false,
        landed_sha:(if $landed == "" then null else $landed end)}'
    ;;
  list-by-target) printf '%s\n' "${FAKE_LIST:-[]}" ;;
  retarget)
    if [ -n "${FAKE_TARGET_FILE:-}" ]; then printf '%s' "$2" > "$FAKE_TARGET_FILE"; fi
    jq -n --arg id "$1" --arg target "$2" '{id:$id,target_branch:$target}'
    ;;
  merge)
    [ "$#" -eq 4 ]
    [ "$3" = "${FAKE_TARGET:-develop}" ]
    [ "$4" = "${FAKE_BASE:-$FAKE_HEAD}" ]
    jq -n --arg landed "${FAKE_LANDED:-$FAKE_HEAD}" \
      '{status:"merged",merge_method:"squash",landed_sha:$landed}'
    ;;
  *) exit 2 ;;
esac
