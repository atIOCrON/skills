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
        self.repo.mkdir()
        self.pack = self.repo / "plans" / "test.reviews" / "code-review-pack"
        self.pack.mkdir(parents=True)
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
        self.write_hash_manifest()

    def write_hash_manifest(self) -> None:
        entries = []
        for path in sorted(self.pack.rglob("*")):
            if path.is_file() and path != self.pack / "hash-manifest.sha256":
                name = path.relative_to(self.pack).as_posix()
                entries.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {name}")
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

    def test_rejects_link_outside_reviewer_workspace(self) -> None:
        external = self.root / "effective-result.php"
        external.write_text("outside sandbox\n")
        (self.pack / "index.md").write_text(
            f"Review: {self.review_sha}\n[effective result]({external})\n"
        )
        self.write_manifest()
        self.assertEqual(self.validate(), 1)

    def test_accepts_pinned_effective_result_in_pack(self) -> None:
        effective = self.pack / "effective-result.php"
        effective.write_text("inside sandbox\n")
        (self.pack / "index.md").write_text(
            f"Review: {self.review_sha}\n[effective result]({effective.name})\n"
        )
        self.write_manifest()
        self.assertEqual(self.validate(), 0)

    def test_accepts_pinned_effective_result_in_nested_directory(self) -> None:
        effective = self.pack / "effective-result" / "applepay-js.phtml"
        effective.parent.mkdir()
        effective.write_text("inside sandbox\n")
        (self.pack / "index.md").write_text(
            f"Review: {self.review_sha}\n"
            "[effective result](effective-result/applepay-js.phtml)\n"
        )
        self.write_manifest()
        self.assertEqual(self.validate(), 0)

    def test_hash_manifest_must_cover_nested_files(self) -> None:
        self.write_manifest()
        effective = self.pack / "effective-result" / "applepay-js.phtml"
        effective.parent.mkdir()
        effective.write_text("unhashed\n")
        self.assertEqual(self.validate(), 1)

    def test_rejects_evidence_path_outside_pack(self) -> None:
        self.write_manifest()
        external = self.repo / "run.log"
        external.write_text("passed\n")
        manifest_path = self.pack / "evidence-manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["checks"][0]["log_path"] = "../../../run.log"
        manifest["checks"][0]["log_sha256"] = hashlib.sha256(
            external.read_bytes()
        ).hexdigest()
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
        self.write_hash_manifest()
        self.assertEqual(self.validate(), 1)

    def test_rejects_file_uri_outside_reviewer_workspace(self) -> None:
        external = self.root / "effective-result.php"
        external.write_text("outside sandbox\n")
        (self.pack / "index.md").write_text(
            f"Review: {self.review_sha}\n[effective result]({external.as_uri()})\n"
        )
        self.write_manifest()
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
                    "review_progress": {
                        "status": "pending",
                        "completed_passes": 0,
                        "pass_limit": 5,
                        "evidence": None,
                    },
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
        manifest["branches"][0]["review_progress"].update(
            {
                "status": "clean",
                "completed_passes": 1,
                "evidence": "reviews/code-review-triage-ledger.md",
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

    def test_release_review_accepts_cap_reached(self) -> None:
        manifest = self.manifest()
        manifest["branches"][0]["review_progress"].update(
            {
                "status": "review_cap_reached",
                "completed_passes": 5,
                "evidence": "reviews/code-review-triage-ledger.md",
            }
        )
        self.assertEqual(release_validator.validate(manifest), [])

    def test_release_review_rejects_early_cap(self) -> None:
        manifest = self.manifest()
        manifest["branches"][0]["review_progress"].update(
            {
                "status": "review_cap_reached",
                "completed_passes": 4,
                "evidence": "reviews/code-review-triage-ledger.md",
            }
        )
        errors = release_validator.validate(manifest)
        self.assertTrue(any("requires completed_passes equal pass_limit" in error for error in errors))

    def test_trim_review_requires_current_tip_and_evidence(self) -> None:
        manifest = self.manifest()
        branch = manifest["branches"][0]
        branch["trim_review"] = {
            "status": "proportionate",
            "sha": "c" * 40,
            "evidence": None,
        }
        errors = release_validator.validate(manifest)
        self.assertTrue(any("trim_review.sha must match tip_sha" in error for error in errors))
        self.assertTrue(any("trim_review.evidence is required" in error for error in errors))
        branch["trim_review"].update(sha=branch["tip_sha"], evidence="reviews/trim-review-ledger.md")
        self.assertEqual(release_validator.validate(manifest), [])

    def test_released_waiver_is_complete_without_claiming_clean_review(self) -> None:
        manifest = self.manifest()
        branch = manifest["branches"][0]
        tip = branch["tip_sha"]
        manifest.update(
            state="released",
            accepted_gaps=["User waived automated reviews."],
            completion={
                "mode": "authorized_waiver",
                "authorized_by": "user",
                "recorded_at": "2026-09-24T00:00:00Z",
                "evidence": "reviews/review-waiver.md",
            },
            integration={"landed_sha": "f" * 40},
        )
        branch["change_request"] = {"url": "https://example.com/pr/1", "state": "merged"}
        branch["review_progress"].update(status="waived", evidence="reviews/review-waiver.md")
        branch["trim_review"] = {
            "status": "waived",
            "sha": tip,
            "evidence": "reviews/review-waiver.md",
        }
        for review in branch["reviews"]:
            review.update(status="waived", sha=tip, evidence="reviews/review-waiver.md")
        self.assertEqual(release_validator.validate(manifest), [])
        branch["reviews"][0]["sha"] = "a" * 40
        self.assertTrue(any("waived sha must match tip_sha" in error for error in release_validator.validate(manifest)))
        branch["reviews"][0]["sha"] = tip
        manifest.pop("completion")
        self.assertTrue(any("must be complete on tip_sha" in error for error in release_validator.validate(manifest)))

    def test_provisional_descendant_cannot_have_ready_request(self) -> None:
        manifest = self.manifest()
        parent = manifest["branches"][0]
        child = json.loads(json.dumps(parent))
        child.update(
            source="feature/child",
            target=parent["source"],
            parent={"branch": parent["source"], "sha": parent["tip_sha"]},
            dependency_reason="needs parent",
            tip_sha="e" * 40,
        )
        child["review_progress"]["status"] = "clean"
        for check in child["checks"]:
            check.update(sha=child["tip_sha"], method="direct", origin_sha=child["tip_sha"])
        for review in child["reviews"]:
            review.update(
                status="clean",
                sha=child["tip_sha"],
                method="direct",
                origin_sha=child["tip_sha"],
                evidence="evidence/review.md",
            )
        manifest["branches"].append(child)
        self.assertEqual(release_validator.validate(manifest), [])
        child["change_request"]["state"] = "ready"
        errors = release_validator.validate(manifest)
        self.assertTrue(any("requires clean ancestors" in error for error in errors))
        parent["review_progress"]["status"] = "clean"
        for review in parent["reviews"]:
            review.update(
                status="clean",
                sha=parent["tip_sha"],
                method="direct",
                origin_sha=parent["tip_sha"],
                evidence="evidence/review.md",
            )
        self.assertEqual(release_validator.validate(manifest), [])


if __name__ == "__main__":
    unittest.main()
