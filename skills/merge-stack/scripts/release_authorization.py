#!/usr/bin/env python3
"""Check exact-head permission or a scoped, verified squash restack."""

import argparse
import json
from pathlib import Path
import subprocess
import sys

from merge_message import read_message


def require(condition, message):
    if not condition:
        raise ValueError(message)


def git(*args):
    return subprocess.check_output(["git", *args], text=True, stderr=subprocess.PIPE).strip()


def ancestor(parent, head):
    return subprocess.run(["git", "merge-base", "--is-ancestor", parent, head],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0


def authorize(events, change_id, head, target, base, method, source, message_file=None,
              restack_parent=None):
    matches = [(index, event, change) for index, event in enumerate(events)
               if event.get("event") == "merge-authorized" and event.get("authorized_by") == "user"
               and isinstance(event.get("evidence"), str) and event["evidence"].strip()
               and event.get("merge_method", "merge-commit") == method
               for change in event.get("changes", [])
               if change.get("change_id") == change_id and change.get("target_branch") == target]
    require(matches, "user authorization does not cover this PR, strategy and target")
    index, authorization, selected = matches[-1]
    scoped = "integration_start_sha" in authorization
    if scoped:
        require(selected.get("source_branch") == source, "authorized source branch differs")
        if method == "squash":
            require(selected.get("message_sha256"), "authorization lacks a squash message hash")
        expected_base = authorization["integration_start_sha"]
        for predecessor in authorization["changes"]:
            if predecessor is selected:
                break
            completions = [event for event in events[index + 1:]
                           if event.get("event") == "merge-confirmed"
                           and event.get("change_id") == predecessor["change_id"]
                           and event.get("target_branch") == target
                           and event.get("merge_method") == method
                           and event.get("landed_parent_sha") == expected_base]
            require(completions, "an earlier selected PR lacks a confirmed merge")
            expected_base = completions[-1]["landed_sha"]
        require(base == expected_base, "integration moved outside the confirmed release sequence")

    if message_file:
        message_hash = read_message(message_file)["sha256"]
        require(not selected.get("message_sha256") or selected["message_sha256"] == message_hash,
                "squash message changed after authorization")
    elif scoped and method == "squash" and restack_parent is None:
        raise ValueError("squash requires the recorded message file")

    original = selected["head_sha"]
    if restack_parent is not None or head != original:
        require(scoped and method == "squash" and authorization.get("allow_verified_restacks") is True,
                "authorization does not cover rewritten source heads")
        parent = selected.get("parent_sha")
        require(parent and ancestor(parent, original), "missing or invalid authorized parent pin")
        if restack_parent is not None:
            require(head == original and restack_parent == parent, "restack inputs differ from authorized pins")
            return {"authorization_head_sha": original, "restack": "permitted"}
        proofs = [event for event in events[index + 1:]
                  if event.get("event") == "rebase-verified"
                  and event.get("branch") == source and event.get("target_branch") == target
                  and event.get("old_remote_sha") == original
                  and event.get("old_base_sha") == parent
                  and event.get("expected_base_sha") == base
                  and event.get("rebased_head_sha") == head
                  and event.get("patch_set") == "equivalent"]
        require(proofs, "rewritten source has no matching verified-restack evidence")
        require(any(event.get("event") == "force-pushed" and event.get("branch") == source
                    and event.get("old_remote_sha") == original and event.get("rebased_head_sha") == head
                    for event in events[index + 1:]), "verified restack was not confirmed pushed")
        require(ancestor(base, head), "restacked source does not contain the current integration tip")
        expected_tree = git("merge-tree", "--write-tree", f"--merge-base={parent}", base, original)
        require(git("rev-parse", f"{head}^{{tree}}") == expected_tree,
                "restack differs from the authorized feature change")
    if method == "squash":
        require(ancestor(base, head), "squash source must be restacked onto the current integration tip")
    return {"authorization_head_sha": original, "effective_head_sha": head}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("journal", "change_id", "head", "target", "base", "method", "source"):
        parser.add_argument(name)
    parser.add_argument("--message-file")
    parser.add_argument("--restack-parent")
    args = parser.parse_args()
    events = [json.loads(line) for line in Path(args.journal).read_text().splitlines() if line.strip()]
    print(json.dumps(authorize(events, args.change_id, args.head, args.target, args.base,
                               args.method, args.source, args.message_file, args.restack_parent)))


if __name__ == "__main__":
    try:
        main()
    except (KeyError, OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(4)
