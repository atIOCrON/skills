#!/usr/bin/env bash
set -euo pipefail
script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
staging_guard="$script_dir/../../rebuild-staging-with-branches/scripts/verify_candidate.sh"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

git init --bare "$tmp_dir/remote.git" >/dev/null
git init -b master "$tmp_dir/work" >/dev/null
cd "$tmp_dir/work"
git config user.name Test
git config user.email test@example.test
printf 'base\n' > base.txt
git add base.txt
git commit -m base >/dev/null
base="$(git rev-parse HEAD)"
git remote add origin "$tmp_dir/remote.git"
git push origin master >/dev/null
git switch -c first >/dev/null
printf 'first\n' > first.txt
git add first.txt
git commit -m first >/dev/null
first="$(git rev-parse HEAD)"
git push origin first >/dev/null
git switch -c second >/dev/null
printf 'second\n' > second.txt
git add second.txt
git commit -m second >/dev/null
second="$(git rev-parse HEAD)"
git push origin second >/dev/null
git push origin "$base:refs/heads/integration" >/dev/null
mkdir "$tmp_dir/providers"
cp "$script_dir/testdata/fake-provider.sh" "$tmp_dir/providers/test.sh"
chmod +x "$tmp_dir/providers/test.sh"
export MERGE_STACK_PROVIDER_DIR="$tmp_dir/providers" FAKE_TARGET=integration
export FAKE_PROVIDER=bitbucket-cloud
export FAKE_HEAD="$first" FAKE_BASE="$base" FAKE_REVIEW=pending
journal="$tmp_dir/journal.jsonl"
"$script_dir/journal_event.sh" "$journal" run-start '{}'

if "$script_dir/merge_stack_change.sh" test origin 1 "$first" integration "$base" null "$journal" merge-commit >/dev/null 2>&1; then
  echo 'merge ran without user authorization' >&2; exit 1
fi
"$script_dir/journal_event.sh" "$journal" merge-authorized \
  "$(jq -nc --arg first "$first" --arg second "$second" \
    '{authorized_by:"user",evidence:"confirm these assembly merges",changes:[
      {change_id:"1",head_sha:$first,target_branch:"integration"},
      {change_id:"2",head_sha:$second,target_branch:"integration"}]}')"
default_merge="$("$script_dir/merge_stack_change.sh" test origin 1 "$first" integration "$base" null "$journal")"
[[ "$default_merge" == *"merge_method=merge-commit"* ]]
if "$script_dir/merge_stack_change.sh" test origin 1 "$first" integration "$base" null "$journal" squash >/dev/null 2>&1; then
  echo 'merge-commit authorization covered an unapproved squash override' >&2; exit 1
fi
if "$script_dir/merge_stack_change.sh" test origin 3 "$first" integration "$base" null "$journal" merge-commit >/dev/null 2>&1; then
  echo 'authorization covered an unlisted PR' >&2; exit 1
fi
export FAKE_HEAD="$second"
if "$script_dir/merge_stack_change.sh" test origin 1 "$second" integration "$base" null "$journal" merge-commit >/dev/null 2>&1; then
  echo 'authorization covered a changed source head' >&2; exit 1
fi

first_merge="$(printf 'merge first\n' | git commit-tree "${first}^{tree}" -p "$base" -p "$first")"
git push origin "$first_merge:refs/heads/integration" >/dev/null
export FAKE_STATE=merged FAKE_HEAD="$first" FAKE_LANDED="$first_merge"
"$script_dir/confirm_merge.sh" test origin 1 "$first" integration "$base" "$journal" >/dev/null

# Integration's first merge is not an ancestor of the second source; no rebase is needed.
expected_tree="$(git merge-tree --write-tree "$first_merge" "$second")"
second_merge="$(printf 'merge second\n' | git commit-tree "$expected_tree" -p "$first_merge" -p "$second")"
git push origin "$second_merge:refs/heads/integration" >/dev/null
export FAKE_HEAD="$second" FAKE_SOURCE=second FAKE_LANDED="$second_merge"
"$script_dir/confirm_merge.sh" test origin 2 "$second" integration "$first_merge" "$journal" merge-commit >/dev/null
[ "$(git rev-parse origin/first)" = "$first" ]
[ "$(git rev-parse origin/second)" = "$second" ]
git merge-base --is-ancestor "$first_merge" "$second_merge"
git merge-base --is-ancestor "$second" "$second_merge"

# An independent source contains neither stacked feature: confirm the combined tree.
git switch --detach "$base" >/dev/null
git switch -c independent >/dev/null
printf 'independent\n' > independent.txt
git add independent.txt
git commit -m independent >/dev/null
independent="$(git rev-parse HEAD)"
git push origin independent >/dev/null
expected_tree="$(git merge-tree --write-tree "$second_merge" "$independent")"
third_merge="$(printf 'merge independent\n' | git commit-tree "$expected_tree" -p "$second_merge" -p "$independent")"
git push origin "$third_merge:refs/heads/integration" >/dev/null
export FAKE_HEAD="$independent" FAKE_SOURCE=independent FAKE_LANDED="$third_merge"
"$script_dir/confirm_merge.sh" test origin 3 "$independent" integration "$second_merge" "$journal" merge-commit >/dev/null
[ "$(git rev-parse "${third_merge}^{tree}")" != "$(git rev-parse "${independent}^{tree}")" ]

# A squash or a merge with changed inputs must not be accepted as a feature merge.
wrong="$(printf 'wrong\n' | git commit-tree "$expected_tree" -p "$third_merge")"
git push origin "$wrong:refs/heads/integration" >/dev/null
export FAKE_LANDED="$wrong"
if "$script_dir/confirm_merge.sh" test origin 3 "$independent" integration "$third_merge" "$journal" merge-commit >/dev/null 2>&1; then
  echo 'confirmation accepted the wrong merge parents' >&2; exit 1
fi
wrong_tree="$(printf 'wrong tree\n' | git commit-tree "${base}^{tree}" -p "$wrong" -p "$independent")"
git push origin "$wrong_tree:refs/heads/integration" >/dev/null
export FAKE_LANDED="$wrong_tree"
if "$script_dir/confirm_merge.sh" test origin 3 "$independent" integration "$wrong" "$journal" merge-commit >/dev/null 2>&1; then
  echo 'confirmation accepted an unexpected merge tree' >&2; exit 1
fi

"$staging_guard" "$base" "$second_merge" "$second_merge"
if "$staging_guard" "$base" "$second_merge" "$wrong" >/dev/null 2>&1; then
  echo 'staging guard accepted a rebuilt candidate' >&2; exit 1
fi
divergent="$(printf 'divergent\n' | git commit-tree "${base}^{tree}" -p "$base")"
if "$staging_guard" "$divergent" "$second_merge" "$second_merge" >/dev/null 2>&1; then
  echo 'staging guard accepted a divergent base' >&2; exit 1
fi
if "$staging_guard" "$base" "${second_merge:0:12}" "$second_merge" >/dev/null 2>&1; then
  echo 'staging guard accepted an abbreviated SHA' >&2; exit 1
fi
echo 'release assembly tests passed'
