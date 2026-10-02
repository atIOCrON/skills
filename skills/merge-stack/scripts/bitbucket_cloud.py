#!/usr/bin/env python3
"""Bitbucket Cloud publication and merge adapter; credentials stay in memory."""

import base64
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

API = "https://api.bitbucket.org/2.0"
SHA = re.compile(r"[0-9a-f]{40}")


def require(condition, message):
    if not condition:
        raise ValueError(message)


class SafeRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        require(newurl.startswith(API + "/"), "unexpected API redirect")
        return super().redirect_request(request, fp, code, msg, headers, newurl)


class Bitbucket:
    def __init__(self, remote):
        address = subprocess.check_output(
            ["git", "remote", "get-url", remote], text=True, stderr=subprocess.DEVNULL
        ).strip()
        if address.startswith("git@bitbucket.org:"):
            repository = address.split(":", 1)[1]
        else:
            parsed = urlparse(address)
            require(parsed.scheme in {"https", "ssh"} and parsed.hostname == "bitbucket.org",
                    "remote must identify a Bitbucket Cloud repository")
            repository = parsed.path.lstrip("/")
        self.repository = repository.removesuffix(".git")
        require(re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", self.repository),
                "remote must contain one workspace and repository slug")
        self.root = f"{API}/repositories/{self.repository}"
        token = os.environ.get("BITBUCKET_TOKEN")
        require(token, "set BITBUCKET_TOKEN; API tokens also require BITBUCKET_EMAIL")
        email = os.environ.get("BITBUCKET_EMAIL")
        self.authorization = (
            "Basic " + base64.b64encode(f"{email}:{token}".encode()).decode()
            if email else "Bearer " + token
        )
        self.opener = build_opener(SafeRedirect())

    def request(self, path, method="GET", body=None):
        url = path if path.startswith("https://") else self.root + "/" + path
        require(url.startswith(self.root + "/") or url in {self.root, API + "/user"},
                "unexpected API resource")
        data = None if body is None else json.dumps(body).encode()
        request = Request(url, data=data, method=method, headers={
            "Authorization": self.authorization, "Accept": "application/json",
            "Content-Type": "application/json",
        })
        with self.opener.open(request, timeout=30) as response:
            payload = response.read()
            return json.loads(payload) if payload else {}

    def pages(self, path):
        values = []
        visited = set()
        while path:
            require(path not in visited, "repeated pagination URL")
            visited.add(path)
            page = self.request(path)
            require(isinstance(page.get("values"), list), "missing paginated values")
            values.extend(page["values"])
            path = page.get("next")
        return values

    def auth(self):
        user = self.request(API + "/user")
        repo = self.request(self.root)
        require(user.get("uuid") and repo.get("full_name", "").lower() == self.repository.lower(),
                "cannot verify authenticated user and repository")
        return user["uuid"]

    def branch(self, name):
        branch = self.request("refs/branches/" + quote(name, safe=""))
        require(SHA.fullmatch(branch.get("target", {}).get("hash", "")), "missing full branch SHA")
        return branch

    def resolve(self, selector):
        if selector.isdigit():
            return selector
        if selector.startswith("https://"):
            parsed = urlparse(selector)
            match = re.fullmatch(r"/" + re.escape(self.repository) + r"/pull-requests/(\d+)/?", parsed.path)
            require(parsed.hostname == "bitbucket.org" and match, "PR URL is outside this repository")
            return match[1]
        matches = [p for p in self.pages("pullrequests?state=OPEN&pagelen=100")
                   if p.get("source", {}).get("branch", {}).get("name") == selector]
        require(len(matches) == 1, "source branch must identify exactly one open PR")
        return str(matches[0]["id"])

    def identity(self, pr):
        for side in ("source", "destination"):
            value = pr.get(side, {})
            require(value.get("repository", {}).get("full_name", "").lower() == self.repository.lower(),
                    "cross-repository PRs are unsupported")
            require(value.get("branch", {}).get("name") and
                    SHA.fullmatch(value.get("commit", {}).get("hash", "")), "incomplete PR identity")
        require(pr.get("links", {}).get("html", {}).get("href"), "missing PR URL")

    def get_change(self, selector):
        id_ = self.resolve(selector)
        pr = self.request(f"pullrequests/{id_}")
        self.identity(pr)
        source = pr["source"]["branch"]["name"]
        target = pr["destination"]["branch"]["name"]
        head = pr["source"]["commit"]["hash"]
        branch = self.branch(target)
        checks = []
        policy = "unknown"
        mergeability = "unknown"
        statuses = "unknown"
        if pr.get("state") == "OPEN" and pr.get("draft") is False:
            source_head = self.branch(source)["target"]["hash"]
            require(source_head == head, "PR source differs from current branch")
            checks = self.pages(f"pullrequests/{id_}/mergeability/checks")
            required_types = {"pullrequest_state_check", "current_user_permission_check", "git_mergeability_check"}
            require(required_types <= {c.get("type") for c in checks}, "incomplete mergeability checks")
            for check in checks:
                require(check.get("status") in {"PASSED", "FAILED", "PENDING", "SKIPPED", "UNKNOWN"} and
                        isinstance(check.get("required"), bool) and isinstance(check.get("blocking"), bool),
                        "incomplete mergeability check")
            queue = any(c["type"] == "merge_queue_check" and c["required"] for c in checks)
            eligible = all(not c["blocking"] and
                           (not (c["required"] or c["type"] in required_types) or c["status"] == "PASSED")
                           for c in checks)
            git_checks = [c for c in checks if c["type"] == "git_mergeability_check"]
            git_clean = all(c["status"] == "PASSED" and c.get("reason") == "clean" for c in git_checks)
            policy = "queue-required" if queue else "passed" if eligible else "blocked"
            mergeability = "mergeable" if git_clean and policy == "passed" else "blocked"
            builds = [c for c in checks if c["required"] and
                      c.get("check", {}).get("kind") in {"minimum_successful_builds", "failed_builds"}]
            statuses = "passed" if builds and all(c["status"] == "PASSED" for c in builds) else (
                "failed" if builds else "not-required")
            keys = [k for k in os.environ.get("BITBUCKET_REQUIRED_STATUS_KEYS", "").split(",") if k]
            if keys:
                values = self.pages(f"commit/{head}/statuses?pagelen=100")
                selected = {s.get("key"): s for s in values}
                expected = [selected.get(k) for k in keys]
                if any(s is None for s in expected):
                    statuses = "missing"
                elif any(s.get("commit", {}).get("hash") != head for s in expected):
                    statuses = "unknown"
                elif any(s.get("state") in {"FAILED", "STOPPED"} for s in expected):
                    statuses = "failed"
                elif all(s.get("state") == "SUCCESSFUL" for s in expected):
                    statuses = "passed"
                else:
                    statuses = "pending"
        participants = pr.get("participants", [])
        review = "blocked" if any(p.get("state") == "changes_requested" for p in participants) else (
            "approved" if any(p.get("approved") is True for p in participants) else "pending")
        return {
            "provider": "bitbucket-cloud", "id": id_, "url": pr["links"]["html"]["href"],
            "state": {"OPEN": "open", "MERGED": "merged", "DECLINED": "closed", "SUPERSEDED": "closed"}.get(pr.get("state"), "unknown"),
            "draft": pr.get("draft"), "author_uuid": pr.get("author", {}).get("uuid"),
            "source_branch": source, "target_branch": target, "head_sha": head,
            "base_sha": branch["target"]["hash"], "target_protected": None,
            "target_policy_enforced": None, "policy_status": policy, "policy_checks": checks,
            "review_status": review, "approval_head_sha": None,
            "checks_status": statuses, "checks_head_sha": head if statuses == "passed" else None,
            "mergeability": mergeability, "cross_repository": False,
            "squash_allowed": "squash" in branch.get("merge_strategies", []),
            "merge_commit_allowed": "merge_commit" in branch.get("merge_strategies", []),
            "source_branch_auto_delete": pr.get("close_source_branch"),
            "landed_sha": (pr.get("merge_commit") or {}).get("hash"),
        }

    def create(self, source, target, head, base, body_file):
        author = self.auth()
        require(self.branch(source)["target"]["hash"] == head and
                self.branch(target)["target"]["hash"] == base, "publication inputs moved")
        require("merge_commit" in self.branch(target).get("merge_strategies", []), "merge commits unavailable")
        existing = [p for p in self.pages("pullrequests?state=OPEN&pagelen=100")
                    if p.get("source", {}).get("branch", {}).get("name") == source]
        require(not existing, "open PR already uses this source; reconcile the recorded run")
        metadata = json.loads(Path(body_file).read_text())
        require(isinstance(metadata.get("title"), str) and metadata["title"].strip() and
                isinstance(metadata.get("description"), str), "body file needs title and description")
        body = {"title": metadata["title"], "description": metadata["description"],
                "source": {"branch": {"name": source}}, "destination": {"branch": {"name": target}},
                "draft": False, "close_source_branch": False}
        # Reviewers are opt-in; an existing repository default remains the provider's responsibility.
        if "reviewers" in metadata:
            require(isinstance(metadata["reviewers"], list) and
                    all(isinstance(r, dict) and r.get("uuid") for r in metadata["reviewers"]),
                    "reviewers must be UUID objects")
            body["reviewers"] = metadata["reviewers"]
        pr = self.request("pullrequests", "POST", body)
        require(isinstance(pr.get("id"), int), "creation returned no PR ID; reconcile before retrying")
        observed = self.request(f"pullrequests/{pr['id']}")
        self.identity(observed)
        require(observed.get("state") == "OPEN" and observed.get("draft") is False and
                observed.get("close_source_branch") is False and observed.get("author", {}).get("uuid") == author and
                observed.get("title") == metadata["title"] and observed.get("description") == metadata["description"] and
                observed["source"]["branch"]["name"] == source and
                observed["destination"]["branch"]["name"] == target and
                observed["source"]["commit"]["hash"] == head and
                observed["destination"]["commit"]["hash"] == base and
                self.branch(source)["target"]["hash"] == head and
                self.branch(target)["target"]["hash"] == base,
                "created PR differs from publication inputs; reconcile before retrying")
        matches = [p for p in self.pages("pullrequests?state=OPEN&pagelen=100")
                   if p.get("source", {}).get("branch", {}).get("name") == source]
        require(len(matches) == 1 and matches[0]["id"] == pr["id"], "duplicate PR after creation")
        return {"id": str(pr["id"]), "url": observed["links"]["html"]["href"],
                "source_branch": source, "target_branch": target, "head_sha": head,
                "base_sha": base, "draft": False, "author_uuid": author}

    def merge(self, id_, head, target, base, method="merge-commit"):
        require(method in {"merge-commit", "squash"}, "unsupported merge method")
        before = self.get_change(id_)
        require(before["state"] == "open" and before["draft"] is False and
                before["head_sha"] == head and before["target_branch"] == target and before["base_sha"] == base and
                before["squash_allowed" if method == "squash" else "merge_commit_allowed"] and
                before["source_branch_auto_delete"] is False and
                before["policy_status"] == "passed" and before["mergeability"] == "mergeable" and
                before["checks_status"] in {"passed", "not-required"}, "PR failed the merge gate")
        # The API has no caller-supplied expected head/base: verify both parents after landing.
        result = self.request(f"pullrequests/{id_}/merge", "POST", {
            "type": "pullrequest_merge_parameters",
            "merge_strategy": "squash" if method == "squash" else "merge_commit", "close_source_branch": False,
        })
        if result.get("state") == "MERGED":
            require(self.branch(before["source_branch"])["target"]["hash"] == head, "source moved during merge")
            return {"status": "merged", "merge_method": method,
                    "landed_sha": (result.get("merge_commit") or {}).get("hash")}
        return {"status": "submitted", "merge_method": method, "landed_sha": None}

    def run(self, operation, args):
        if operation == "auth-check" and not args:
            return {"provider": "bitbucket-cloud", "authenticated": True, "author_uuid": self.auth()}
        if operation == "get-change" and len(args) == 1:
            return self.get_change(args[0])
        if operation == "list-by-target" and len(args) == 1:
            return [{"id": str(p["id"]), "url": p["links"]["html"]["href"],
                     "source_branch": p["source"]["branch"]["name"], "target_branch": args[0]}
                    for p in self.pages("pullrequests?state=OPEN&pagelen=100")
                    if p["destination"]["branch"]["name"] == args[0]]
        if operation == "retarget" and len(args) == 2:
            before = self.get_change(args[0])
            require(before["state"] == "open", "only open PRs can be retargeted")
            self.request(f"pullrequests/{before['id']}", "PUT", {"destination": {"branch": {"name": args[1]}}})
            after = self.get_change(before["id"])
            require(after["target_branch"] == args[1] and after["head_sha"] == before["head_sha"], "retarget identity changed")
            return after
        if operation == "create" and len(args) == 5:
            return self.create(*args)
        if operation == "merge" and len(args) in {4, 5}:
            return self.merge(*args)
        raise ValueError("unsupported operation or argument count")


def main():
    try:
        require(len(sys.argv) >= 3, "usage: bitbucket_cloud.py <remote> <operation> [arguments...]")
        print(json.dumps(Bitbucket(sys.argv[1]).run(sys.argv[2], sys.argv[3:])))
    except HTTPError as error:
        print(f"error: Bitbucket HTTP {error.code}; reconcile any attempted mutation before retrying", file=sys.stderr)
        return 3
    except (ValueError, KeyError, TypeError, OSError, URLError, subprocess.CalledProcessError) as error:
        # Network exception strings may contain credential-bearing URLs; keep them out of logs.
        message = str(error) if isinstance(error, ValueError) else type(error).__name__
        print(f"error: {message}", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
