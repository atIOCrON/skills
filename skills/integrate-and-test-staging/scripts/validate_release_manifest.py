#!/usr/bin/env python3
"""Validate the shared release-manifest contract."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import sys
from typing import Any


SHA_RE = re.compile(r"^[0-9a-f]{40,64}$")
STATES = {"building", "frozen", "staged", "accepted", "released"}
CHECK_KINDS = {"agent", "external"}
CHECK_STATES = {"passed", "failed", "pending", "blocked_by_environment"}
CHECK_METHODS = {"direct", "identity_reuse"}
REVIEW_STATES = {"pending", "clean", "changes_required", "waived"}
REVIEW_METHODS = {"direct", "equal_range_diff", "test_only_closure"}
REVIEW_PROGRESS_STATES = {"pending", "clean", "review_cap_reached", "waived"}
REVIEWERS = {"claude", "codex", "cursor"}
CR_STATES = {"none", "draft", "ready", "merged", "closed"}


def is_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def is_sha(value: Any) -> bool:
    return isinstance(value, str) and bool(SHA_RE.fullmatch(value))


def scope_payload(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "base": data.get("base"),
        "branches": [
            {
                "source": branch.get("source"),
                "plan": branch.get("plan"),
                "target": branch.get("target"),
                "parent": branch.get("parent"),
                "dependency_reason": branch.get("dependency_reason"),
                "tip_sha": branch.get("tip_sha"),
                "tree_sha": branch.get("tree_sha"),
                "surfaces": branch.get("surfaces"),
                "checks": [
                    {
                        "id": check.get("id"),
                        "kind": check.get("kind"),
                        "command": check.get("command"),
                    }
                    for check in branch.get("checks", [])
                    if isinstance(check, dict)
                ],
            }
            for branch in data.get("branches", [])
            if isinstance(branch, dict)
        ],
        "exclusions": data.get("exclusions", []),
    }


def scope_digest(data: dict[str, Any]) -> str:
    encoded = json.dumps(
        scope_payload(data), ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


def validate(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["manifest root must be an object"]

    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if not is_text(data.get("release_id")):
        errors.append("release_id must be a non-empty string")
    state = data.get("state")
    if state not in STATES:
        errors.append(f"state must be one of {sorted(STATES)}")
    completion = data.get("completion")
    waiver_completion = (
        state == "released"
        and isinstance(completion, dict)
        and completion.get("mode") == "authorized_waiver"
    )
    if completion is not None:
        if not waiver_completion:
            errors.append("completion requires released state and authorized_waiver mode")
        elif not all(is_text(completion.get(key)) for key in ("authorized_by", "recorded_at", "evidence")):
            errors.append("completion requires authorized_by, recorded_at, and evidence")

    base = data.get("base")
    if not isinstance(base, dict):
        errors.append("base must be an object")
        base = {}
    if not is_text(base.get("branch")):
        errors.append("base.branch must be a non-empty string")
    if not is_sha(base.get("sha")):
        errors.append("base.sha must be a full lowercase hexadecimal SHA")

    branches = data.get("branches")
    if not isinstance(branches, list) or not branches:
        errors.append("branches must be a non-empty array")
        branches = []

    seen: set[str] = set()
    saw_waived_review = False
    available = {base.get("branch")} if is_text(base.get("branch")) else set()
    clean_lineage: dict[str, bool] = {base.get("branch"): True} if is_text(base.get("branch")) else {}
    parent_tips = {base.get("branch"): base.get("sha")} if is_text(base.get("branch")) else {}
    for index, branch in enumerate(branches):
        prefix = f"branches[{index}]"
        if not isinstance(branch, dict):
            errors.append(f"{prefix} must be an object")
            continue
        source = branch.get("source")
        if not is_text(source):
            errors.append(f"{prefix}.source must be a non-empty string")
        elif source in seen:
            errors.append(f"{prefix}.source duplicates {source!r}")
        else:
            seen.add(source)
        for field in ("plan", "target", "dependency_reason"):
            if not is_text(branch.get(field)):
                errors.append(f"{prefix}.{field} must be a non-empty string")
        for field in ("tip_sha", "tree_sha"):
            if not is_sha(branch.get(field)):
                errors.append(f"{prefix}.{field} must be a full lowercase hexadecimal SHA")

        parent = branch.get("parent")
        if not isinstance(parent, dict):
            errors.append(f"{prefix}.parent must be an object")
            parent = {}
        parent_branch = parent.get("branch")
        if not is_text(parent_branch):
            errors.append(f"{prefix}.parent.branch must be a non-empty string")
        elif parent_branch not in available:
            errors.append(
                f"{prefix}.parent.branch must be the base or an earlier manifest branch"
            )
        if not is_sha(parent.get("sha")):
            errors.append(f"{prefix}.parent.sha must be a full lowercase hexadecimal SHA")
        if branch.get("target") != parent_branch:
            errors.append(f"{prefix}.target must equal parent.branch")

        surfaces = branch.get("surfaces")
        if not isinstance(surfaces, list) or not all(is_text(item) for item in surfaces):
            errors.append(f"{prefix}.surfaces must be an array of non-empty strings")

        review_progress = branch.get("review_progress")
        if review_progress is not None:
            progress_prefix = f"{prefix}.review_progress"
            if not isinstance(review_progress, dict):
                errors.append(f"{progress_prefix} must be an object")
                review_progress = {}
            progress_status = review_progress.get("status")
            completed_passes = review_progress.get("completed_passes")
            pass_limit = review_progress.get("pass_limit")
            progress_evidence = review_progress.get("evidence")
            if progress_status not in REVIEW_PROGRESS_STATES:
                errors.append(f"{progress_prefix}.status is invalid")
            if (
                not isinstance(completed_passes, int)
                or isinstance(completed_passes, bool)
                or completed_passes < 0
            ):
                errors.append(f"{progress_prefix}.completed_passes must be a non-negative integer")
            if (
                not isinstance(pass_limit, int)
                or isinstance(pass_limit, bool)
                or pass_limit < 1
            ):
                errors.append(f"{progress_prefix}.pass_limit must be a positive integer")
            if (
                isinstance(completed_passes, int)
                and not isinstance(completed_passes, bool)
                and isinstance(pass_limit, int)
                and not isinstance(pass_limit, bool)
                and completed_passes > pass_limit
            ):
                errors.append(f"{progress_prefix}.completed_passes exceeds pass_limit")
            if progress_evidence is not None and not is_text(progress_evidence):
                errors.append(f"{progress_prefix}.evidence must be null or a path")
            if progress_status == "review_cap_reached":
                if completed_passes != pass_limit:
                    errors.append(
                        f"{progress_prefix} cap status requires completed_passes equal pass_limit"
                    )
                if not is_text(progress_evidence):
                    errors.append(f"{progress_prefix}.evidence is required when cap is reached")
            if progress_status == "waived" and not is_text(progress_evidence):
                errors.append(f"{progress_prefix}.evidence is required when waived")

        trim_review = branch.get("trim_review")
        if trim_review is not None:
            trim_prefix = f"{prefix}.trim_review"
            if not isinstance(trim_review, dict):
                errors.append(f"{trim_prefix} must be an object")
                trim_review = {}
            trim_status = trim_review.get("status")
            if trim_status not in {"pending", "proportionate", "waived"}:
                errors.append(f"{trim_prefix}.status is invalid")
            if trim_status in {"proportionate", "waived"}:
                if trim_review.get("sha") != branch.get("tip_sha"):
                    errors.append(f"{trim_prefix}.sha must match tip_sha")
                if not is_text(trim_review.get("evidence")):
                    errors.append(f"{trim_prefix}.evidence is required when complete")
            elif trim_review.get("sha") is not None or trim_review.get("evidence") is not None:
                errors.append(f"{trim_prefix} pending status requires null sha and evidence")

        checks = branch.get("checks")
        if not isinstance(checks, list):
            errors.append(f"{prefix}.checks must be an array")
            checks = []
        check_ids: set[str] = set()
        for check_index, check in enumerate(checks):
            check_prefix = f"{prefix}.checks[{check_index}]"
            if not isinstance(check, dict):
                errors.append(f"{check_prefix} must be an object")
                continue
            check_id = check.get("id")
            if not is_text(check_id):
                errors.append(f"{check_prefix}.id must be a non-empty string")
            elif check_id in check_ids:
                errors.append(f"{check_prefix}.id duplicates {check_id!r}")
            else:
                check_ids.add(check_id)
            if check.get("kind") not in CHECK_KINDS:
                errors.append(f"{check_prefix}.kind must be agent or external")
            if check.get("status") not in CHECK_STATES:
                errors.append(f"{check_prefix}.status is invalid")
            if check.get("sha") is not None and not is_sha(check.get("sha")):
                errors.append(f"{check_prefix}.sha must be null or a full SHA")
            if not is_text(check.get("command")):
                errors.append(f"{check_prefix}.command must be a command or procedure")
            if check.get("evidence") is not None and not is_text(check.get("evidence")):
                errors.append(f"{check_prefix}.evidence must be null or a path")
            kind = check.get("kind")
            status = check.get("status")
            method = check.get("method")
            origin_sha = check.get("origin_sha")
            if kind == "agent" and status in {"passed", "failed"}:
                if method not in CHECK_METHODS:
                    errors.append(f"{check_prefix}.method is invalid")
                if not is_sha(origin_sha):
                    errors.append(f"{check_prefix}.origin_sha must be a full SHA")
                if not is_sha(check.get("sha")):
                    errors.append(f"{check_prefix}.sha is required when completed")
                if method == "direct" and origin_sha != check.get("sha"):
                    errors.append(f"{check_prefix} direct origin_sha must equal sha")
                if method == "identity_reuse":
                    if status != "passed":
                        errors.append(f"{check_prefix} only a passed check may be reused")
                    if origin_sha == check.get("sha"):
                        errors.append(
                            f"{check_prefix} identity_reuse must map different SHAs"
                        )
                if not is_text(check.get("evidence")):
                    errors.append(f"{check_prefix}.evidence is required when completed")
            elif method is not None or origin_sha is not None:
                errors.append(
                    f"{check_prefix} method and origin_sha require a completed agent check"
                )

        reviews = branch.get("reviews")
        if not isinstance(reviews, list):
            errors.append(f"{prefix}.reviews must be an array")
            reviews = []
        seen_reviewers: set[str] = set()
        for review_index, review in enumerate(reviews):
            review_prefix = f"{prefix}.reviews[{review_index}]"
            if not isinstance(review, dict):
                errors.append(f"{review_prefix} must be an object")
                continue
            reviewer = review.get("reviewer")
            if reviewer not in REVIEWERS:
                errors.append(f"{review_prefix}.reviewer is invalid")
            elif reviewer in seen_reviewers:
                errors.append(f"{review_prefix}.reviewer duplicates {reviewer!r}")
            else:
                seen_reviewers.add(reviewer)
            if review.get("status") not in REVIEW_STATES:
                errors.append(f"{review_prefix}.status is invalid")
            if review.get("sha") is not None and not is_sha(review.get("sha")):
                errors.append(f"{review_prefix}.sha must be null or a full SHA")
            method = review.get("method")
            origin_sha = review.get("origin_sha")
            if review.get("status") == "clean":
                if method not in REVIEW_METHODS:
                    errors.append(f"{review_prefix}.method is invalid")
                if not is_sha(origin_sha):
                    errors.append(f"{review_prefix}.origin_sha must be a full SHA")
                if method == "direct" and origin_sha != review.get("sha"):
                    errors.append(f"{review_prefix} direct origin_sha must equal sha")
                is_mapping = method in {"equal_range_diff", "test_only_closure"}
                if is_mapping and origin_sha == review.get("sha"):
                    errors.append(f"{review_prefix} {method} must map different SHAs")
            elif review.get("status") == "waived":
                if review.get("sha") != branch.get("tip_sha"):
                    errors.append(f"{review_prefix} waived sha must match tip_sha")
                if method is not None or origin_sha is not None:
                    errors.append(f"{review_prefix} waived review cannot claim a review method")
            elif method is not None or origin_sha is not None:
                errors.append(
                    f"{review_prefix} method and origin_sha must be null until clean"
                )
            if review.get("evidence") is not None and not is_text(review.get("evidence")):
                errors.append(f"{review_prefix}.evidence must be null or a path")
            if review.get("status") in {"clean", "waived"} and not is_text(review.get("evidence")):
                errors.append(f"{review_prefix}.evidence is required when clean or waived")
        if seen_reviewers != REVIEWERS:
            errors.append(f"{prefix}.reviews must contain claude, codex, and cursor")
        clean_on_tip = all(
            isinstance(review, dict)
            and review.get("status") == "clean"
            and review.get("sha") == branch.get("tip_sha")
            for review in reviews
        )
        reviewed_or_waived_on_tip = all(
            isinstance(review, dict)
            and review.get("status") in {"clean", "waived"}
            and review.get("sha") == branch.get("tip_sha")
            for review in reviews
        )
        has_waived_review = any(
            isinstance(review, dict) and review.get("status") == "waived"
            for review in reviews
        )
        saw_waived_review |= has_waived_review or (
            isinstance(trim_review, dict) and trim_review.get("status") == "waived"
        )
        if isinstance(review_progress, dict):
            progress_status = review_progress.get("status")
            if progress_status == "clean" and not clean_on_tip:
                errors.append(f"{prefix}.review_progress clean status requires clean reviews on tip_sha")
            if progress_status == "review_cap_reached" and clean_on_tip:
                errors.append(f"{prefix}.review_progress must be clean when all reviews are clean on tip_sha")
            if progress_status == "waived" and not (reviewed_or_waived_on_tip and has_waived_review):
                errors.append(f"{prefix}.review_progress waived status requires a waived review on tip_sha")
            if (
                progress_status == "clean"
                and isinstance(trim_review, dict)
                and trim_review.get("status") != "proportionate"
            ):
                errors.append(f"{prefix}.review_progress clean status requires a proportionate trim result")

        change_request = branch.get("change_request")
        if not isinstance(change_request, dict):
            errors.append(f"{prefix}.change_request must be an object")
        else:
            if change_request.get("state") not in CR_STATES:
                errors.append(f"{prefix}.change_request.state is invalid")
            if change_request.get("url") is not None and not is_text(change_request.get("url")):
                errors.append(f"{prefix}.change_request.url must be null or a URL")
            if change_request.get("state") == "ready" and not (
                clean_lineage.get(parent_branch, False)
                and parent.get("sha") == parent_tips.get(parent_branch)
            ):
                errors.append(f"{prefix}.change_request requires clean ancestors at pinned SHAs")
            if (
                change_request.get("state") == "ready"
                and isinstance(trim_review, dict)
                and trim_review.get("status") != "proportionate"
            ):
                errors.append(f"{prefix}.change_request requires a proportionate trim result")

        if state in {"frozen", "staged", "accepted", "released"}:
            tip_sha = branch.get("tip_sha")
            trim_states = {"proportionate", "waived"} if waiver_completion else {"proportionate"}
            review_states = {"clean", "waived"} if waiver_completion else {"clean"}
            if isinstance(trim_review, dict) and trim_review.get("status") not in trim_states:
                errors.append(f"{prefix}.trim_review is incomplete for release state {state}")
            if isinstance(review_progress, dict) and review_progress.get("status") not in review_states:
                errors.append(f"{prefix}.review_progress is incomplete for release state {state}")
            for review_index, review in enumerate(reviews):
                if not isinstance(review, dict):
                    continue
                if review.get("status") not in review_states or review.get("sha") != tip_sha:
                    errors.append(
                        f"{prefix}.reviews[{review_index}] must be complete on tip_sha"
                    )
            if waiver_completion and (
                not isinstance(change_request, dict)
                or change_request.get("state") != "merged"
            ):
                errors.append(f"{prefix}.change_request must be merged for waiver completion")
            for check_index, check in enumerate(checks):
                if isinstance(check, dict) and check.get("kind") == "agent":
                    if check.get("status") != "passed" or check.get("sha") != tip_sha:
                        errors.append(
                            f"{prefix}.checks[{check_index}] agent check must pass on tip_sha"
                        )

        if is_text(source):
            available.add(source)
            parent_tips[source] = branch.get("tip_sha")
            clean_lineage[source] = (
                clean_lineage.get(parent_branch, False)
                and parent.get("sha") == parent_tips.get(parent_branch)
                and clean_on_tip
                and (
                    not isinstance(trim_review, dict)
                    or trim_review.get("status") == "proportionate"
                )
                and (
                    not isinstance(review_progress, dict)
                    or review_progress.get("status") == "clean"
                )
            )

    exclusions = data.get("exclusions")
    if not isinstance(exclusions, list):
        errors.append("exclusions must be an array")
        exclusions = []
    excluded_sources: set[str] = set()
    for index, exclusion in enumerate(exclusions):
        prefix = f"exclusions[{index}]"
        if not isinstance(exclusion, dict):
            errors.append(f"{prefix} must be an object")
            continue
        source = exclusion.get("source")
        if not is_text(source) or not is_text(exclusion.get("reason")):
            errors.append(f"{prefix} requires non-empty source and reason")
        elif source in excluded_sources:
            errors.append(f"{prefix}.source duplicates {source!r}")
        else:
            excluded_sources.add(source)
        if source in seen:
            errors.append(f"{prefix}.source is also included in branches")

    if not isinstance(data.get("accepted_gaps"), list):
        errors.append("accepted_gaps must be an array")
    if waiver_completion and not data.get("accepted_gaps"):
        errors.append("authorized waiver completion requires accepted_gaps")
    if waiver_completion and not saw_waived_review:
        errors.append("authorized waiver completion requires a waived review")
    if data.get("integration") is not None and not isinstance(data.get("integration"), dict):
        errors.append("integration must be null or an object")
    integration = data.get("integration")
    if waiver_completion and not (
        isinstance(integration, dict) and is_sha(integration.get("landed_sha"))
    ):
        errors.append("authorized waiver completion requires integration.landed_sha")

    freeze = data.get("freeze")
    if not isinstance(freeze, dict):
        errors.append("freeze must be an object")
        freeze = {}
    if state in {"frozen", "staged", "accepted", "released"} and (
        not waiver_completion or any(freeze.values())
    ):
        for field in ("frozen_at", "authorized_by", "scope_digest"):
            if not is_text(freeze.get(field)):
                errors.append(f"freeze.{field} must be set for a frozen release")
        if is_text(freeze.get("scope_digest")) and freeze.get("scope_digest") != scope_digest(data):
            errors.append("freeze.scope_digest does not match the current release scope")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=pathlib.Path)
    parser.add_argument("--print-scope-digest", action="store_true")
    args = parser.parse_args()

    try:
        data = json.loads(args.manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"cannot read manifest: {exc}", file=sys.stderr)
        return 2

    if args.print_scope_digest:
        if not isinstance(data, dict):
            print("manifest root must be an object", file=sys.stderr)
            return 1
        print(scope_digest(data))
        return 0

    errors = validate(data)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"release manifest valid: {args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
