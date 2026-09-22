#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest


SCRIPT_DIR = Path(__file__).parent


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


review_validator = load_module(
    "validate_review_pack", SCRIPT_DIR / "validate_review_pack.py"
)
release_validator = load_module(
    "validate_release_manifest", SCRIPT_DIR / "validate_release_manifest.py"
)


class ReviewPackReuseTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.repo = self.root / "repo"
        self.pack = self.root / "pack"
        self.repo.mkdir()
        self.pack.mkdir()
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        subprocess.run(
            ["git", "-C", str(self.repo), "config", "user.email", "test@example.com"],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(self.repo), "config", "user.name", "Test"],
            check=True,
        )
        self.origin_sha = self.commit("one\n", "origin")
        self.review_sha = self.commit("two\n", "review")
        for name in (
            "changed-files.txt",
            "diff-stat.txt",
            "changes.diff",
            "ownership-map.md",
            "verification-summary.md",
            "acceptance-gates.md",
            "deterministic-checks.md",
        ):
            (self.pack / name).write_text("\n")
        (self.pack / "index.md").write_text(f"Review: {self.review_sha}\n")
        (self.pack / "run.log").write_text("passed\n")
        (self.pack / "reuse-proof.txt").write_text("identities match\n")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def commit(self, content: str, message: str) -> str:
        (self.repo / "file.txt").write_text(content)
        subprocess.run(["git", "-C", str(self.repo), "add", "file.txt"], check=True)
        subprocess.run(
            ["git", "-C", str(self.repo), "commit", "-q", "-m", message],
            check=True,
        )
        return subprocess.check_output(
            ["git", "-C", str(self.repo), "rev-parse", "HEAD"], text=True
        ).strip()

    def write_manifest(self, *, method: str = "identity_reuse") -> None:
        def digest(name: str) -> str:
            return hashlib.sha256((self.pack / name).read_bytes()).hexdigest()

        manifest = {
            "review_sha": self.review_sha,
            "checks": [
                {
                    "id": "focused-tests",
                    "kind": "agent",
                    "required": True,
                    "verified_sha": self.review_sha,
                    "last_run_sha": self.origin_sha,
                    "method": method,
                    "command": "test-command",
                    "runtime": "test-runtime",
                    "result": "passed",
                    "input_identity": "sha256:input",
                    "result_identity": "sha256:result",
                    "log_path": "run.log",
                    "log_sha256": digest("run.log"),
                    "reuse_evidence_path": "reuse-proof.txt",
                    "reuse_evidence_sha256": digest("reuse-proof.txt"),
                }
            ],
        }
        (self.pack / "evidence-manifest.json").write_text(
            json.dumps(manifest, indent=2) + "\n"
        )
        entries = []
        for path in sorted(self.pack.iterdir()):
            if path.is_file() and path.name != "hash-manifest.sha256":
                entries.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}")
        (self.pack / "hash-manifest.sha256").write_text("\n".join(entries) + "\n")

    def validate(self) -> int:
        with contextlib.redirect_stderr(io.StringIO()):
            return review_validator.main(self.pack, self.repo)

    def test_reused_check_verifies_current_tip(self) -> None:
        self.write_manifest()
        self.assertEqual(self.validate(), 0)

    def test_direct_check_cannot_claim_an_older_run(self) -> None:
        self.write_manifest(method="direct")
        self.assertEqual(self.validate(), 1)


class ReleaseManifestReuseTest(unittest.TestCase):
    def manifest(self) -> dict[str, object]:
        base_sha = "a" * 40
        tip_sha = "b" * 40
        origin_sha = "c" * 40
        return {
            "schema_version": 1,
            "release_id": "test-release",
            "state": "building",
            "base": {"branch": "main", "sha": base_sha},
            "freeze": {
                "frozen_at": None,
                "authorized_by": None,
                "scope_digest": None,
            },
            "branches": [
                {
                    "source": "feature/test",
                    "plan": "plans/test.md",
                    "target": "main",
                    "parent": {"branch": "main", "sha": base_sha},
                    "dependency_reason": "none",
                    "tip_sha": tip_sha,
                    "tree_sha": "d" * 40,
                    "surfaces": ["test"],
                    "checks": [
                        {
                            "id": "focused-tests",
                            "kind": "agent",
                            "status": "passed",
                            "sha": tip_sha,
                            "method": "identity_reuse",
                            "origin_sha": origin_sha,
                            "command": "test-command",
                            "evidence": "evidence/reuse.json",
                        }
                    ],
                    "reviews": [
                        {
                            "reviewer": reviewer,
                            "status": "pending",
                            "sha": None,
                            "method": None,
                            "origin_sha": None,
                            "evidence": None,
                        }
                        for reviewer in ("claude", "codex", "cursor")
                    ],
                    "change_request": {"url": None, "state": "none"},
                }
            ],
            "exclusions": [],
            "accepted_gaps": [],
            "integration": None,
        }

    def test_release_check_accepts_identity_reuse(self) -> None:
        manifest = self.manifest()
        manifest["state"] = "frozen"
        tip_sha = manifest["branches"][0]["tip_sha"]
        for review in manifest["branches"][0]["reviews"]:
            review.update(
                {
                    "status": "clean",
                    "sha": tip_sha,
                    "method": "direct",
                    "origin_sha": tip_sha,
                    "evidence": "evidence/review.md",
                }
            )
        manifest["freeze"] = {
            "frozen_at": "2026-09-22T00:00:00Z",
            "authorized_by": "test",
            "scope_digest": release_validator.scope_digest(manifest),
        }
        self.assertEqual(release_validator.validate(manifest), [])

    def test_release_check_rejects_same_sha_reuse(self) -> None:
        manifest = self.manifest()
        check = manifest["branches"][0]["checks"][0]
        check["origin_sha"] = check["sha"]
        errors = release_validator.validate(manifest)
        self.assertTrue(any("must map different SHAs" in error for error in errors))

    def test_release_review_accepts_test_only_closure(self) -> None:
        manifest = self.manifest()
        tip_sha = manifest["branches"][0]["tip_sha"]
        for review in manifest["branches"][0]["reviews"]:
            review.update(
                {
                    "status": "clean",
                    "sha": tip_sha,
                    "method": "test_only_closure",
                    "origin_sha": "e" * 40,
                    "evidence": "evidence/test-only-closure.md",
                }
            )
        self.assertEqual(release_validator.validate(manifest), [])

    def test_release_review_rejects_same_sha_test_only_closure(self) -> None:
        manifest = self.manifest()
        tip_sha = manifest["branches"][0]["tip_sha"]
        for review in manifest["branches"][0]["reviews"]:
            review.update(
                {
                    "status": "clean",
                    "sha": tip_sha,
                    "method": "test_only_closure",
                    "origin_sha": tip_sha,
                    "evidence": "evidence/test-only-closure.md",
                }
            )
        errors = release_validator.validate(manifest)
        self.assertTrue(
            any("test_only_closure must map different SHAs" in error for error in errors)
        )


if __name__ == "__main__":
    unittest.main()
