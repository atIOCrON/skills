#!/usr/bin/env python3
"""Exercise scoped squash permission, restacks, messages and recovery offline."""

import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from merge_message import read_message
from release_authorization import authorize

SCRIPTS = Path(__file__).resolve().parent


class ReleaseSquashTests(unittest.TestCase):
    def run_command(self, *args, input=None, env=None, succeeds=True):
        result = subprocess.run(args, cwd=self.work, input=input, text=True, capture_output=True,
                                env={**os.environ, **(env or {})})
        if succeeds:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout)
        return result.stdout.strip()

    def git(self, *args, **kwargs):
        return self.run_command("git", *args, **kwargs)

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.work = self.root / "work"
        self.work.mkdir()
        self.git("init", "--bare", str(self.root / "remote.git"))
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Test")
        self.git("config", "user.email", "test@example.test")
        (self.work / "base.txt").write_text("base\n")
        self.git("add", ".")
        self.git("commit", "-m", "base")
        self.base = self.git("rev-parse", "HEAD")
        self.git("remote", "add", "origin", str(self.root / "remote.git"))
        self.git("push", "origin", "main", f"{self.base}:refs/heads/integration")
        self.sources = {}
        for branch, parent in (("first", self.base), ("second", None), ("independent", self.base)):
            if parent is None:
                parent = self.sources["first"]["head_sha"]
            self.git("switch", "-c", branch, parent)
            for number in (1, 2):
                (self.work / f"{branch}-{number}.txt").write_text(f"{branch} {number}\n")
                self.git("add", ".")
                self.git("commit", "-m", f"{branch} {number}")
            self.git("push", "origin", branch)
            self.sources[branch] = {"source_branch": branch, "parent_sha": parent,
                                    "head_sha": self.git("rev-parse", "HEAD")}
        self.git("switch", "--detach", self.base)
        providers = self.root / "providers"
        providers.mkdir()
        shutil.copy2(SCRIPTS / "testdata/fake-provider.sh", providers / "test.sh")
        self.environment = {"MERGE_STACK_PROVIDER_DIR": str(providers),
                            "FAKE_PROVIDER": "bitbucket-cloud", "FAKE_TARGET": "integration",
                            "MERGE_STACK_CONFIRM_WAIT": "0"}
        self.journal = self.root / "journal.jsonl"
        self.messages = {}
        changes = []
        for number, (branch, pins) in enumerate(self.sources.items(), 1):
            path = self.root / f"{branch} message.txt"
            path.write_text(f"Add {branch} changes\n\nImplement {branch} for the release.\nVerified offline.\n")
            self.messages[branch] = path
            changes.append({**pins, "change_id": str(number), "target_branch": "integration",
                            "message_sha256": read_message(path)["sha256"]})
        self.append({"event": "merge-authorized", "authorized_by": "user", "merge_method": "squash",
                     "integration_start_sha": self.base, "allow_verified_restacks": True,
                     "evidence": "Squash this release and proceed without pausing", "changes": changes})
        previous_directory = Path.cwd()
        self.addCleanup(os.chdir, previous_directory)
        os.chdir(self.work)

    def append(self, event):
        with self.journal.open("a") as stream:
            stream.write(json.dumps(event) + "\n")

    def events(self):
        return [json.loads(line) for line in self.journal.read_text().splitlines()]

    def restack(self, branch, number):
        self.run_command(str(SCRIPTS / "rebase_stack_branch.sh"), "origin", "integration", branch,
                         str(self.journal), self.sources[branch]["parent_sha"], str(number),
                         env=self.environment)
        return self.git("rev-parse", f"origin/{branch}")

    def merge(self, branch, number, head, base, confirm=True, message=None):
        path = self.messages[branch]
        landed = self.git("commit-tree", f"{head}^{{tree}}", "-p", base,
                          input=message or read_message(path)["message"])
        environment = {**self.environment, "FAKE_HEAD": head, "FAKE_BASE": base,
                       "FAKE_SOURCE": branch, "FAKE_LANDED": landed, "FAKE_MESSAGE_FILE": str(path)}
        self.run_command(str(SCRIPTS / "merge_stack_change.sh"), "test", "origin", str(number),
                         head, "integration", base, "null", str(self.journal), "squash", str(path),
                         env=environment)
        self.git("push", "origin", f"{landed}:refs/heads/integration")
        if confirm:
            self.confirm(number, head, base, environment)
        return landed, environment

    def confirm(self, number, head, base, environment, succeeds=True):
        return self.run_command(str(SCRIPTS / "confirm_merge.sh"), "test", "origin", str(number),
                                head, "integration", base, str(self.journal), "squash",
                                env={**environment, "FAKE_STATE": "merged"}, succeeds=succeeds)

    def test_entire_mixed_release_uses_one_authorization(self):
        base = self.base
        for number, branch in enumerate(self.sources, 1):
            head = self.sources[branch]["head_sha"] if number == 1 else self.restack(branch, number)
            base, _ = self.merge(branch, number, head, base)
        self.assertEqual(self.git("rev-list", "--count", f"{self.base}..{base}"), "3")
        self.assertEqual(sum(event["event"] == "merge-authorized" for event in self.events()), 1)
        self.assertEqual(sum(event["event"] == "merge-confirmed" for event in self.events()), 3)
        self.assertEqual(self.git("rev-parse", "origin/first"), self.sources["first"]["head_sha"])
        self.assertEqual(self.git("rev-list", "--count", "origin/integration^..origin/independent"), "2")

    def test_order_and_unexpected_source_changes_block_before_restack(self):
        self.run_command(str(SCRIPTS / "rebase_stack_branch.sh"), "origin", "integration", "second",
                         str(self.journal), self.sources["second"]["parent_sha"], "2",
                         env=self.environment, succeeds=False)
        events = self.events()
        events[0]["changes"][0]["head_sha"] = self.base
        with self.assertRaisesRegex(ValueError, "verified-restack"):
            authorize(events, "1", self.sources["first"]["head_sha"], "integration", self.base,
                      "squash", "first", str(self.messages["first"]))

    def test_changed_message_and_missing_permission_block_merge(self):
        path = self.messages["first"]
        path.write_text("Change scope\n\nA different explanation.\n")
        with self.assertRaisesRegex(ValueError, "message changed"):
            authorize(self.events(), "1", self.sources["first"]["head_sha"], "integration", self.base,
                      "squash", "first", str(path))
        with self.assertRaisesRegex(ValueError, "authorization"):
            authorize(self.events(), "9", self.sources["first"]["head_sha"], "integration", self.base,
                      "squash", "first", str(path))

    def test_restack_proof_does_not_cover_changed_tree_or_target(self):
        base, _ = self.merge("first", "1", self.sources["first"]["head_sha"], self.base)
        head = self.restack("second", "2")
        events = self.events()
        with self.assertRaisesRegex(ValueError, "integration moved"):
            authorize(events, "2", head, "integration", self.base, "squash", "second",
                      str(self.messages["second"]))
        changed = self.git("commit-tree", f"{base}^{{tree}}", "-p", base, input="wrong\n")
        for event in events:
            if event.get("rebased_head_sha") == head:
                event["rebased_head_sha"] = changed
        with self.assertRaisesRegex(ValueError, "feature change"):
            authorize(events, "2", changed, "integration", base, "squash", "second",
                      str(self.messages["second"]))
        missing_permission = copy.deepcopy(self.events())
        missing_permission[0]["allow_verified_restacks"] = False
        with self.assertRaisesRegex(ValueError, "rewritten"):
            authorize(missing_permission, "2", head, "integration", base, "squash", "second",
                      str(self.messages["second"]))

    def test_resume_confirms_existing_merge_with_recorded_message(self):
        head = self.sources["first"]["head_sha"]
        _, environment = self.merge("first", "1", head, self.base, confirm=False)
        output = self.run_command(str(SCRIPTS / "reconcile_run.sh"), "test", "origin", str(self.journal),
                                  env={**environment, "FAKE_STATE": "merged"})
        self.assertEqual(json.loads(output)["status"], "confirmation-required")
        self.confirm("1", head, self.base, environment)
        self.assertEqual(sum(event["event"] == "merge-planned" for event in self.events()), 1)

    def test_landed_message_mismatch_blocks_confirmation(self):
        head = self.sources["first"]["head_sha"]
        _, environment = self.merge("first", "1", head, self.base, confirm=False,
                                    message="Wrong message\n\nWrong explanation.\n")
        self.confirm("1", head, self.base, environment, succeeds=False)
        self.assertFalse(any(event["event"] == "merge-confirmed" for event in self.events()))


if __name__ == "__main__":
    unittest.main()
