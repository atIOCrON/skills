#!/usr/bin/env python3
"""Exercise publication, policy gates, ref drift, and async merge handling offline."""

import base64
import copy
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from bitbucket_cloud import API, Bitbucket

HEAD = "a" * 40
BASE = "b" * 40
LANDED = "c" * 40
REPO = "workspace/repo"


class MemoryBitbucket(Bitbucket):
    def __init__(self):
        self.repository = REPO
        self.root = f"{API}/repositories/{REPO}"
        self.branches = {"feature/a": HEAD, "integration": BASE}
        self.prs = {}
        self.calls = []
        self.checks = [{"type": type_, "required": True, "blocking": False,
                        "status": "PASSED", **({"reason": "clean"} if type_ == "git_mergeability_check" else {})}
                       for type_ in ("pullrequest_state_check", "current_user_permission_check", "git_mergeability_check")]
        self.async_merge = False
        self.statuses = []
        self.strategies = ["merge_commit", "squash"]

    def pr(self, id_="1", target="integration"):
        return {"id": int(id_), "title": "Change A", "description": "Tested change",
                "state": "OPEN", "draft": False, "close_source_branch": False,
                "author": {"uuid": "author"}, "participants": [],
                "links": {"html": {"href": f"https://bitbucket.org/{REPO}/pull-requests/{id_}"}},
                "source": {"branch": {"name": "feature/a"}, "commit": {"hash": HEAD}, "repository": {"full_name": REPO}},
                "destination": {"branch": {"name": target}, "commit": {"hash": self.branches[target]},
                                "repository": {"full_name": REPO}}}

    def request(self, path, method="GET", body=None):
        self.calls.append((path, method, copy.deepcopy(body)))
        if path == API + "/user":
            return {"uuid": "author"}
        if path == self.root:
            return {"full_name": REPO}
        if path.startswith("refs/branches/"):
            from urllib.parse import unquote
            name = unquote(path[len("refs/branches/"):])
            return {"target": {"hash": self.branches[name]}, "merge_strategies": self.strategies}
        if path == "pullrequests?state=OPEN&pagelen=100":
            values = list(self.prs.values())
            return {"values": values[:1], **({"next": self.root + "/page2"} if len(values) > 1 else {})}
        if path == self.root + "/page2":
            return {"values": list(self.prs.values())[1:]}
        if path.endswith("/mergeability/checks"):
            return {"values": self.checks}
        if path.startswith("commit/"):
            return {"values": self.statuses}
        if path == "pullrequests" and method == "POST":
            pr = self.pr()
            pr.update({k: body[k] for k in ("title", "description", "draft", "close_source_branch")})
            self.prs["1"] = pr
            return pr
        if path.startswith("pullrequests/"):
            parts = path.split("/")
            pr = self.prs[parts[1]]
            if len(parts) == 3 and parts[2] == "merge":
                if self.async_merge:
                    return {}
                pr["state"] = "MERGED"
                pr["merge_commit"] = {"hash": LANDED}
                return pr
            if method == "PUT":
                pr["destination"]["branch"]["name"] = body["destination"]["branch"]["name"]
            return pr
        raise AssertionError(path)


class BitbucketTests(unittest.TestCase):
    def setUp(self):
        self.api = MemoryBitbucket()
        self.environment = patch.dict(os.environ, {"BITBUCKET_REQUIRED_STATUS_KEYS": ""})
        self.environment.start()
        self.addCleanup(self.environment.stop)

    def open_pr(self):
        self.api.prs["1"] = self.api.pr()

    def metadata(self, folder):
        path = Path(folder) / "body.json"
        path.write_text(json.dumps({"title": "Change A", "description": "Tested change"}))
        return str(path)

    def test_authentication_modes(self):
        with patch("subprocess.check_output", return_value=f"git@bitbucket.org:{REPO}.git\n"):
            with patch.dict(os.environ, {"BITBUCKET_TOKEN": "secret", "BITBUCKET_EMAIL": "user@example.test"}):
                api = Bitbucket("origin")
                self.assertEqual(api.authorization, "Basic " + base64.b64encode(b"user@example.test:secret").decode())
            with patch.dict(os.environ, {"BITBUCKET_TOKEN": "oauth", "BITBUCKET_EMAIL": ""}):
                self.assertEqual(Bitbucket("origin").authorization, "Bearer oauth")

    def test_create_non_draft_retains_source_without_adding_reviewers(self):
        with tempfile.TemporaryDirectory() as folder:
            result = self.api.create("feature/a", "integration", HEAD, BASE, self.metadata(folder))
        self.assertFalse(result["draft"])
        body = next(b for p, method, b in self.api.calls if method == "POST")
        self.assertFalse(body["close_source_branch"])
        self.assertNotIn("reviewers", body)

    def test_duplicate_on_later_page_blocks_creation(self):
        other = self.api.pr("2")
        other["source"]["branch"]["name"] = "feature/other"
        self.api.prs = {"2": other, "1": self.api.pr()}
        with tempfile.TemporaryDirectory() as folder, self.assertRaisesRegex(ValueError, "open PR"):
            self.api.create("feature/a", "integration", HEAD, BASE, self.metadata(folder))
        self.assertFalse(any(method == "POST" for _, method, _ in self.api.calls))

    def test_moved_input_blocks_publication(self):
        self.api.branches["integration"] = LANDED
        with tempfile.TemporaryDirectory() as folder, self.assertRaisesRegex(ValueError, "inputs moved"):
            self.api.create("feature/a", "integration", HEAD, BASE, self.metadata(folder))

    def test_no_checks_does_not_invent_ci_or_approval(self):
        self.open_pr()
        change = self.api.get_change("1")
        self.assertEqual(change["checks_status"], "not-required")
        self.assertIsNone(change["checks_head_sha"])
        self.assertIsNone(change["approval_head_sha"])
        self.assertEqual(change["policy_status"], "passed")

    def test_required_checks_queue_and_unknown_permission_block_merge(self):
        for check in (
            {"type": "standard_merge_check", "required": True, "blocking": True, "status": "FAILED"},
            {"type": "custom_pre_merge_check", "required": True, "blocking": False, "status": "UNKNOWN"},
            {"type": "merge_queue_check", "required": True, "blocking": False, "status": "PASSED"},
        ):
            with self.subTest(check=check):
                api = MemoryBitbucket()
                api.prs["1"] = api.pr()
                api.checks.append(check)
                with self.assertRaises(ValueError):
                    api.merge("1", HEAD, "integration", BASE, "merge-commit")
                self.assertFalse(any(method == "POST" for _, method, _ in api.calls))
        self.open_pr()
        self.api.checks[1].update(status="UNKNOWN", required=False)
        self.assertEqual(self.api.get_change("1")["policy_status"], "blocked")

    def test_named_required_status_must_exist_and_match_head(self):
        self.open_pr()
        os.environ["BITBUCKET_REQUIRED_STATUS_KEYS"] = "pipeline"
        self.assertEqual(self.api.get_change("1")["checks_status"], "missing")
        self.api.statuses = [{"key": "pipeline", "state": "SUCCESSFUL", "commit": {"hash": BASE}}]
        self.assertEqual(self.api.get_change("1")["checks_status"], "unknown")
        self.api.statuses[0]["commit"]["hash"] = HEAD
        self.assertEqual(self.api.get_change("1")["checks_status"], "passed")

    def test_ref_drift_and_deleted_source_policy_block_merge(self):
        self.open_pr()
        for head, base in ((BASE, BASE), (HEAD, LANDED)):
            with self.assertRaises(ValueError):
                self.api.merge("1", head, "integration", base, "merge-commit")
        self.api.prs["1"]["close_source_branch"] = True
        with self.assertRaises(ValueError):
            self.api.merge("1", HEAD, "integration", BASE, "merge-commit")

    def test_merge_commit_and_async_submission(self):
        self.open_pr()
        self.api.async_merge = True
        result = self.api.merge("1", HEAD, "integration", BASE, "merge-commit")
        self.assertEqual(result["status"], "submitted")
        self.api.async_merge = False
        result = self.api.merge("1", HEAD, "integration", BASE, "merge-commit")
        self.assertEqual(result["landed_sha"], LANDED)
        body = [body for _, method, body in self.api.calls if method == "POST"][-1]
        self.assertEqual(body["merge_strategy"], "merge_commit")
        self.assertFalse(body["close_source_branch"])

    def test_default_and_explicit_squash_override(self):
        self.open_pr()
        result = self.api.run("merge", ["1", HEAD, "integration", BASE])
        self.assertEqual(result["merge_method"], "merge-commit")
        self.open_pr()
        result = self.api.run("merge", ["1", HEAD, "integration", BASE, "squash"])
        self.assertEqual(result["merge_method"], "squash")
        body = [body for _, method, body in self.api.calls if method == "POST"][-1]
        self.assertEqual(body["merge_strategy"], "squash")

    def test_no_implicit_squash_when_merge_commits_disabled(self):
        self.open_pr()
        self.api.strategies = ["squash"]
        with self.assertRaises(ValueError):
            self.api.run("merge", ["1", HEAD, "integration", BASE])
        self.assertFalse(any(method == "POST" for _, method, _ in self.api.calls))

    def test_foreign_pr_url_and_pagination_are_rejected(self):
        with self.assertRaises(ValueError):
            self.api.resolve("https://bitbucket.org/other/repo/pull-requests/1")
        with patch("subprocess.check_output", return_value=f"git@bitbucket.org:{REPO}.git\n"), \
                patch.dict(os.environ, {"BITBUCKET_TOKEN": "secret"}):
            with self.assertRaises(ValueError):
                Bitbucket("origin").request("https://other.test/steal-token")


if __name__ == "__main__":
    unittest.main()
