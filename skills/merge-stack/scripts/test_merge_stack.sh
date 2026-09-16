#!/usr/bin/env bash
set -euo pipefail

script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

git init --bare "$tmp_dir/remote.git" >/dev/null
git init -b develop "$tmp_dir/work" >/dev/null
cd "$tmp_dir/work"
git config user.name Test
git config user.email test@example.test
printf 'base\n' > file.txt
git add file.txt
git commit -m base >/dev/null
git remote add upstream "$tmp_dir/remote.git"
git push -u upstream develop >/dev/null
git --git-dir="$tmp_dir/remote.git" symbolic-ref HEAD refs/heads/develop
base_sha="$(git rev-parse HEAD)"
[ "$("$script_dir/resolve_base_branch.sh" upstream)" = develop ]
journal="$tmp_dir/merge-stack.jsonl"
"$script_dir/journal_event.sh" "$journal" run-start \
  "$(jq -nc --arg base "$base_sha" \
    '{run_id:"test-run",provider:"test",remote:"upstream",base_branch:"develop",base_sha:$base}')"

git switch -c first >/dev/null
printf 'first\n' >> file.txt
git commit -am first >/dev/null
git push -u upstream first >/dev/null
first_sha="$(git rev-parse HEAD)"

git switch -c second >/dev/null
printf 'second\n' >> file.txt
git commit -am second >/dev/null
git push -u upstream second >/dev/null
second_sha="$(git rev-parse HEAD)"

order="$("$script_dir/resolve_stack_order.sh" upstream develop chained second first)"
[ "$order" = "1 first
2 second" ] || {
  echo "unexpected stack order: $order" >&2
  exit 1
}
"$script_dir/rebase_stack_branch.sh" upstream develop first "$journal" >/dev/null

git switch --detach "$base_sha" >/dev/null
git switch -c independent >/dev/null
printf 'independent\n' > independent.txt
git add independent.txt
git commit -m independent >/dev/null
git push -u upstream independent >/dev/null
independent_order="$("$script_dir/resolve_stack_order.sh" upstream develop base-targeted first independent)"
[ "$independent_order" = "1 first
2 independent" ]
if "$script_dir/resolve_stack_order.sh" upstream develop base-targeted first second >/dev/null 2>&1; then
  echo "base-targeted order accepted a hidden dependency" >&2
  exit 1
fi

git switch --detach "$base_sha" >/dev/null
git switch -c shared-base >/dev/null
printf 'shared\n' > shared.txt
git add shared.txt
git commit -m shared >/dev/null
git switch -c shared-left >/dev/null
printf 'left\n' > left.txt
git add left.txt
git commit -m left >/dev/null
git push -u upstream shared-left >/dev/null
git switch shared-base >/dev/null
git switch -c shared-right >/dev/null
printf 'right\n' > right.txt
git add right.txt
git commit -m right >/dev/null
git push -u upstream shared-right >/dev/null
if "$script_dir/resolve_stack_order.sh" upstream develop base-targeted shared-left shared-right >/dev/null 2>&1; then
  echo "base-targeted order accepted a shared unmerged base" >&2
  exit 1
fi

adapter_dir="$tmp_dir/providers"
mkdir -p "$adapter_dir"
adapter="$adapter_dir/test.sh"
cp "$script_dir/testdata/fake-provider.sh" "$adapter"
chmod +x "$adapter"

git remote add github git@github.com:example/repo.git
git remote add gitlab git@gitlab.com:example/repo.git
export TEST_HEAD="$first_sha" TEST_BASE="$base_sha"
github_view="$(PATH="$script_dir/testdata:$PATH" "$script_dir/provider.sh" github github get-change 1)"
printf '%s' "$github_view" | jq -e --arg head "$first_sha" --arg base "$base_sha" \
  '.approval_head_sha == $head and .checks_head_sha == $head and
    .base_sha == $base and .target_protected == true and
    .target_policy_enforced == true' >/dev/null
export TEST_APPROVAL_HEAD="$base_sha"
stale_github_view="$(PATH="$script_dir/testdata:$PATH" "$script_dir/provider.sh" github github get-change 1)"
printf '%s' "$stale_github_view" | jq -e '.approval_head_sha == null' >/dev/null
unset TEST_APPROVAL_HEAD
export TEST_STRICT_STATUS=false
unprotected_github_view="$(PATH="$script_dir/testdata:$PATH" "$script_dir/provider.sh" github github get-change 1)"
printf '%s' "$unprotected_github_view" | jq -e '.target_policy_enforced == false' >/dev/null
unset TEST_STRICT_STATUS
gitlab_view="$(PATH="$script_dir/testdata:$PATH" "$script_dir/provider.sh" gitlab gitlab get-change 1)"
printf '%s' "$gitlab_view" | jq -e --arg head "$first_sha" --arg base "$base_sha" \
  '.approval_head_sha == $head and .checks_head_sha == $head and
    .base_sha == $base and .target_protected == true and
    .target_policy_enforced == true' >/dev/null
export TEST_RESET_APPROVALS=false
stale_gitlab_view="$(PATH="$script_dir/testdata:$PATH" "$script_dir/provider.sh" gitlab gitlab get-change 1)"
printf '%s' "$stale_gitlab_view" | jq -e '.approval_head_sha == null' >/dev/null
unset TEST_RESET_APPROVALS
export TEST_MERGED_RESULTS=false
unprotected_gitlab_view="$(PATH="$script_dir/testdata:$PATH" "$script_dir/provider.sh" gitlab gitlab get-change 1)"
printf '%s' "$unprotected_gitlab_view" | jq -e '.target_policy_enforced == false' >/dev/null
unset TEST_MERGED_RESULTS
unset TEST_HEAD TEST_BASE

export MERGE_STACK_PROVIDER_DIR="$adapter_dir"
export FAKE_HEAD="$first_sha"
export FAKE_BASE="$base_sha"
export FAKE_LIST='[{"id":"2","url":"https://example.test/change/2","source_branch":"second","target_branch":"first"}]'

"$script_dir/provider.sh" test upstream auth-check >/dev/null
"$script_dir/validate_successor_change.sh" test upstream first 2 >/dev/null
"$script_dir/wait_for_change_checks.sh" test upstream 1 "$first_sha" >/dev/null
target_file="$tmp_dir/fake-target"
printf 'first' > "$target_file"
export FAKE_TARGET_FILE="$target_file"
"$script_dir/retarget_change.sh" test upstream 2 develop "$journal" >/dev/null
[ "$(<"$target_file")" = develop ]
unset FAKE_TARGET_FILE
"$script_dir/merge_stack_change.sh" test upstream 1 "$first_sha" develop "$base_sha" 2 "$journal" >/dev/null

export FAKE_REVIEW=unknown
if "$script_dir/merge_stack_change.sh" test upstream 1 "$first_sha" develop "$base_sha" 2 "$journal" >/dev/null 2>&1; then
  echo "merge accepted an unknown review state" >&2
  exit 1
fi
unset FAKE_REVIEW

export FAKE_APPROVAL_HEAD="$base_sha"
if "$script_dir/merge_stack_change.sh" test upstream 1 "$first_sha" develop "$base_sha" 2 "$journal" >/dev/null 2>&1; then
  echo "merge accepted a stale approval" >&2
  exit 1
fi
unset FAKE_APPROVAL_HEAD

export FAKE_CHECKS_HEAD="$base_sha"
if "$script_dir/merge_stack_change.sh" test upstream 1 "$first_sha" develop "$base_sha" 2 "$journal" >/dev/null 2>&1; then
  echo "merge accepted checks for another SHA" >&2
  exit 1
fi
unset FAKE_CHECKS_HEAD

export FAKE_PROTECTED=false
if "$script_dir/merge_stack_change.sh" test upstream 1 "$first_sha" develop "$base_sha" 2 "$journal" >/dev/null 2>&1; then
  echo "merge accepted an unprotected target" >&2
  exit 1
fi
unset FAKE_PROTECTED

export FAKE_TARGET_POLICY=false
if "$script_dir/merge_stack_change.sh" test upstream 1 "$first_sha" develop "$base_sha" 2 "$journal" >/dev/null 2>&1; then
  echo "merge accepted a target without stale-base protection" >&2
  exit 1
fi
unset FAKE_TARGET_POLICY

if "$script_dir/merge_stack_change.sh" test upstream 1 "$first_sha" wrong-target "$base_sha" 2 "$journal" >/dev/null 2>&1; then
  echo "merge accepted the wrong target" >&2
  exit 1
fi

export FAKE_CHECKS=failed
if "$script_dir/merge_stack_change.sh" test upstream 1 "$first_sha" develop "$base_sha" 2 "$journal" >/dev/null 2>&1; then
  echo "merge accepted failed remote checks" >&2
  exit 1
fi
unset FAKE_CHECKS

"$script_dir/journal_event.sh" "$journal" merge-planned \
  "$(jq -nc --arg sha "$first_sha" '{head_sha:$sha}')"
jq -e --arg sha "$first_sha" '.event == "merge-planned" and .head_sha == $sha' "$journal" >/dev/null

export FAKE_STATE=merged
export FAKE_TARGET=develop
squash_sha="$(printf 'squash\n' | git commit-tree "${first_sha}^{tree}" -p "$base_sha")"
git push upstream "$squash_sha:refs/heads/develop" >/dev/null
export FAKE_LANDED="$squash_sha"
"$script_dir/confirm_squash_merge.sh" test upstream 1 "$first_sha" develop "$base_sha" "$journal" >/dev/null

export FAKE_LIST='[]'
if "$script_dir/delete_branch_if_unreferenced.sh" test upstream second "$base_sha" "$journal" >/dev/null 2>&1; then
  echo "remote deletion accepted a stale source SHA" >&2
  exit 1
fi
[ -n "$(git ls-remote --heads upstream refs/heads/second)" ]
"$script_dir/delete_branch_if_unreferenced.sh" test upstream second "$second_sha" "$journal" >/dev/null
[ -z "$(git ls-remote --heads upstream refs/heads/second)" ]
reconcile_journal="$tmp_dir/reconcile.jsonl"
independent_sha="$(git rev-parse upstream/independent)"
"$script_dir/journal_event.sh" "$reconcile_journal" run-start \
  "$(jq -nc --arg base "$base_sha" \
    '{run_id:"reconcile-test",provider:"test",remote:"upstream",base_branch:"develop",base_sha:$base}')"
"$script_dir/journal_event.sh" "$reconcile_journal" force-push-planned \
  "$(jq -nc --arg lease "$independent_sha" --arg head "$base_sha" \
    '{branch:"independent",lease_sha:$lease,rebased_head_sha:$head}')"
reconcile_output="$("$script_dir/reconcile_run.sh" test upstream "$reconcile_journal")"
printf '%s' "$reconcile_output" | jq -e \
  '.action == "force-push" and .branch == "independent" and .status == "not-applied"' >/dev/null
record="$tmp_dir/cleanup-record"
printf 'first %s %s %s\n' "$first_sha" "$first_sha" "$squash_sha" > "$record"
# Exercise retry after an earlier cleanup advanced the local ref but could not
# delete it, while both source branches remain on the remote.
git branch recovered "$squash_sha"
git push upstream "$first_sha:refs/heads/recovered" >/dev/null
git fetch upstream recovered >/dev/null
git branch --set-upstream-to=upstream/recovered recovered >/dev/null
printf 'recovered %s %s %s\n' "$first_sha" "$first_sha" "$squash_sha" >> "$record"
printf 'dirty\n' > dirty.tmp
if "$script_dir/cleanup_merged_branches.sh" upstream develop "$record" >/dev/null 2>&1; then
  echo "local cleanup accepted a dirty checkout" >&2
  exit 1
fi
rm dirty.tmp
cleanup_output="$("$script_dir/cleanup_merged_branches.sh" upstream develop "$record")"
[[ "$cleanup_output" == *"deleted: first"* ]]
[[ "$cleanup_output" == *"deleted: recovered"* ]]
[ -z "$(git branch --list first recovered)" ]
[ -n "$(git ls-remote --heads upstream refs/heads/first)" ]
[ -n "$(git ls-remote --heads upstream refs/heads/recovered)" ]
"$script_dir/delete_branch_if_unreferenced.sh" test upstream first "$first_sha" "$journal" >/dev/null

echo "merge-stack tests passed"
