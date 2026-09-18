#!/usr/bin/env bash
# Sync shared orchestration components into the runnable skill bundles.
set -euo pipefail

mode="${1:---write}"
case "$mode" in --write|--check) ;; *) echo "usage: sync_bundled_skill.sh [--write|--check]" >&2; exit 2 ;; esac

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
branch_bundle="$repo_root/skills/build-branch-stack"
publish_bundle="$repo_root/skills/open-stack-requests"
merge_bundle="$repo_root/skills/merge-stack"
rebuild_bundle="$repo_root/skills/rebuild-staging-with-branches"
integration_bundle="$repo_root/skills/integrate-and-test-staging"
failed=0

sync_one() {
  local source="$repo_root/$1" target="$2/$3"
  if [ "$mode" = "--check" ]; then
    if ! cmp -s "$source" "$target"; then echo "bundle differs: $target" >&2; failed=1; fi
  else
    mkdir -p "$(dirname "$target")"
    cp "$source" "$target"
  fi
}

while IFS='|' read -r source target; do
  [ -n "$source" ] && sync_one "$source" "$branch_bundle" "$target"
done <<'EOF'
shared-components/code-review-closure/code-review-closure.md|references/code-review-closure.md
shared-components/code-review-pack/code-review-pack.md|references/code-review-pack.md
shared-components/code-review-pack/scripts/strict_patch_replay.sh|scripts/strict_patch_replay.sh
shared-components/code-review-pack/scripts/validate_review_pack.py|scripts/validate_review_pack.py
shared-components/code-review-loop/code-review-loop-closure-invocation.md|references/code-review-loop-closure-invocation.md
shared-components/code-review-loop/code-review-loop-code-review-invocation.md|references/code-review-loop-code-review-invocation.md
shared-components/code-review-loop/code-review-loop.md|references/code-review-loop.md
shared-components/code-review-triage/code-review-triage.md|references/code-review-triage.md
shared-components/code-review/code-review.md|references/code-review.md
shared-components/from-reviewed-plan-to-git-handoff/from-reviewed-plan-to-git-handoff.md|references/from-reviewed-plan-to-git-handoff.md
shared-components/git-branch-commit/git-branch-commit.md|references/git-branch-commit.md
shared-components/git-sync-branch/git-sync-branch.md|references/git-sync-branch.md
shared-components/git-commit-message/git-commit-message.md|references/git-commit-message.md
shared-components/implementation-dispatch/implementation-dispatch-fix-request.md|references/implementation-dispatch-fix-request.md
shared-components/implementation-dispatch/implementation-dispatch-plan-invocation.md|references/implementation-dispatch-plan-invocation.md
shared-components/implementation-dispatch/implementation-dispatch.md|references/implementation-dispatch.md
shared-components/multi-review-pass-runner/multi-review-pass-runner.md|references/multi-review-pass-runner.md
shared-components/orchestration-conventions/orchestration-conventions.md|references/orchestration-conventions.md
shared-components/orchestration-conventions/orchestration-definitions.md|references/orchestration-definitions.md
shared-components/orchestration-conventions/orchestration-finding-ids.md|references/orchestration-finding-ids.md
shared-components/orchestration-conventions/orchestration-plans-layout.md|references/orchestration-plans-layout.md
shared-components/orchestration-conventions/orchestration-triage-ledger-protocol.md|references/orchestration-triage-ledger-protocol.md
shared-components/orchestration-final-handoff/orchestration-final-handoff.md|references/orchestration-final-handoff.md
shared-components/orchestration-runtime/orchestration-runtime.md|references/orchestration-runtime.md
shared-components/plan-implement/plan-implement.md|references/plan-implement.md
shared-components/reviewer-preflight/reviewer-preflight.md|references/reviewer-preflight.md
shared-components/staged-diff-scope/staged-diff-scope.md|references/staged-diff-scope.md
shared-components/verification-runner/verification-runner.md|references/verification-runner.md
shared-components/multi-review-pass-runner/scripts/launch_claude_review.sh|scripts/launch_claude_review.sh
shared-components/multi-review-pass-runner/scripts/launch_codex_review.sh|scripts/launch_codex_review.sh
shared-components/multi-review-pass-runner/scripts/launch_cursor_review.sh|scripts/launch_cursor_review.sh
shared-components/multi-review-pass-runner/scripts/launcher_common.sh|scripts/launcher_common.sh
shared-components/multi-review-pass-runner/scripts/lib_review_launch.sh|scripts/lib_review_launch.sh
shared-components/multi-review-pass-runner/scripts/resume_review.sh|scripts/resume_review.sh
shared-components/multi-review-pass-runner/scripts/test_launch_reviewers.sh|scripts/test_launch_reviewers.sh
shared-components/multi-review-pass-runner/scripts/test_runtime_launchers.sh|scripts/test_runtime_launchers.sh
shared-components/reviewer-preflight/scripts/run_reviewer_preflight.sh|scripts/run_reviewer_preflight.sh
shared-components/release-manifest/release-manifest.md|references/release-manifest.md
shared-components/release-manifest/scripts/validate_release_manifest.py|scripts/validate_release_manifest.py
EOF

while IFS='|' read -r source target; do
  [ -n "$source" ] && sync_one "$source" "$publish_bundle" "$target"
done <<'EOF'
shared-components/change-request-description/change-request-description.md|references/change-request-description.md
shared-components/change-request-lifecycle/change-request-lifecycle.md|references/change-request-lifecycle.md
shared-components/change-request-lifecycle/gitlab.md|references/change-request-providers/gitlab.md
shared-components/change-request-lifecycle/github.md|references/change-request-providers/github.md
shared-components/change-request-lifecycle/bitbucket-cloud.md|references/change-request-providers/bitbucket-cloud.md
shared-components/orchestration-conventions/orchestration-change-requests.md|references/orchestration-change-requests.md
shared-components/orchestration-conventions/orchestration-plans-layout.md|references/orchestration-plans-layout.md
shared-components/forge-cli/scripts/ensure_forge_cli.sh|scripts/ensure_forge_cli.sh
shared-components/release-manifest/release-manifest.md|references/release-manifest.md
shared-components/release-manifest/scripts/validate_release_manifest.py|scripts/validate_release_manifest.py
EOF

sync_one shared-components/orchestration-conventions/orchestration-plans-layout.md \
  "$merge_bundle" references/orchestration-plans-layout.md
sync_one shared-components/release-manifest/release-manifest.md \
  "$merge_bundle" references/release-manifest.md
sync_one shared-components/release-manifest/scripts/validate_release_manifest.py \
  "$merge_bundle" scripts/validate_release_manifest.py

sync_one shared-components/release-manifest/release-manifest.md \
  "$rebuild_bundle" references/release-manifest.md
sync_one shared-components/release-manifest/scripts/validate_release_manifest.py \
  "$rebuild_bundle" scripts/validate_release_manifest.py

sync_one shared-components/release-manifest/release-manifest.md \
  "$integration_bundle" references/release-manifest.md
sync_one shared-components/release-manifest/scripts/validate_release_manifest.py \
  "$integration_bundle" scripts/validate_release_manifest.py

exit "$failed"
