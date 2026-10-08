#!/usr/bin/env python3
"""Regression tests for preserving usable review output through format repair."""

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from normalize_code_review_output import normalize
from validate_code_review_output import validate


SHA = "a" * 40
SCRIPTS = Path(__file__).resolve().parent
REVIEW = f"""## Blockers
- None

## Should-fix
- [cursor-1] [tests/footer.ts:12] Stale footer expectation - Failure family: footer contract / UI / render / test failure - Evidence class: reproduced - Pinned SHA: {SHA} - Supported path: render footer - Existing facilities only: yes - Evidence: Reproduction: npm test; Artifact: footer.log; Observed: failed assertion - Recommendation: update stale expectation

## Nits
- [cursor-2] [src/footer.ts:4] Clarify comment - Evidence: source comment - Recommendation: clarify wording

## Contradictions
- None

## Related Existing Issues
- None

## Proportionality
- Not proportionate - cursor-1 needs correction

## Skill Feedback
- None

Address findings before next pass
"""


class ReviewNormalizationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

    def test_normalize_and_validate_preserves_evidence(self):
        result, mapping = normalize(REVIEW, "cursor", 1)
        self.assertEqual(mapping, {"cursor-1": "code-p1-cursor-01", "cursor-2": "code-p1-cursor-02"})
        expected = REVIEW.replace("cursor-1", "code-p1-cursor-01").replace("cursor-2", "code-p1-cursor-02")
        self.assertEqual(result, expected)
        output = self.root / "review.md"
        output.write_text(result)
        self.assertEqual(validate(output, "cursor", 1, SHA), (0, []))

    def test_preserves_valid_ids_and_avoids_collisions(self):
        result, mapping = normalize(REVIEW.replace("cursor-2", "code-p1-cursor-01"), "cursor", 1)
        self.assertEqual(mapping, {"cursor-1": "code-p1-cursor-02"})
        self.assertIn("- [code-p1-cursor-01] [src/footer.ts:4]", result)

    def test_declines_ambiguous_or_foreign_ids(self):
        for replacement in ("cursor-2", "claude-1", "code-p2-cursor-01", "code-p1-claude-01", "issue"):
            with self.subTest(replacement=replacement), self.assertRaises(ValueError):
                normalize(REVIEW.replace("cursor-1", replacement), "cursor", 1)

    def test_does_not_rewrite_evidence_tokens(self):
        with self.assertRaises(ValueError):
            normalize(REVIEW.replace("Artifact: footer.log", "Artifact: cursor-1.log"), "cursor", 1)

    def test_fenced_evidence_is_left_for_local_coordinator_repair(self):
        with self.assertRaises(ValueError):
            normalize(REVIEW + "\n```markdown\n### Should fix:\n```\n", "cursor", 1)

    def test_duplicate_canonical_definitions_fail_validation(self):
        output = self.root / "review.md"
        output.write_text(REVIEW.replace("cursor-1", "code-p1-cursor-01").replace("cursor-2", "code-p1-cursor-01"))
        code, errors = validate(output, "cursor", 1, SHA)
        self.assertEqual(code, 10)
        self.assertIn("duplicate finding ID: code-p1-cursor-01", errors)

    def invoke_normalizer(self, text):
        source, output, mapping = (self.root / name for name in ("raw.md", "normalized.md", "mapping.json"))
        source.write_text(text)
        proc = subprocess.run([sys.executable, str(SCRIPTS / "normalize_code_review_output.py"),
                               str(source), str(output), str(mapping), "cursor", "1", SHA], capture_output=True, text=True)
        return proc, source, output, mapping

    def test_mapping_hashes_and_original_are_preserved(self):
        proc, source, output, mapping = self.invoke_normalizer(REVIEW)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        receipt = json.loads(mapping.read_text())
        self.assertEqual(source.read_text(), REVIEW)
        self.assertEqual(receipt["source_sha256"], hashlib.sha256(source.read_bytes()).hexdigest())
        self.assertEqual(receipt["output_sha256"], hashlib.sha256(output.read_bytes()).hexdigest())
        self.assertEqual(receipt["validation_code"], 0)
        retry = subprocess.run(proc.args, capture_output=True)
        self.assertEqual(retry.returncode, 2)

    def test_missing_evidence_or_wrong_sha_cannot_be_normalized(self):
        for text in (REVIEW.replace(" - Evidence: Reproduction: npm test; Artifact: footer.log; Observed: failed assertion", ""),
                     REVIEW.replace(SHA, "b" * 40)):
            with self.subTest(text=text):
                proc, _, output, mapping = self.invoke_normalizer(text)
                self.assertEqual(proc.returncode, 11)
                self.assertFalse(output.exists())
                self.assertFalse(mapping.exists())

    def run_repair(self, text, resumable=False):
        scripts = self.root / "scripts"
        scripts.mkdir()
        for name in ("repair_code_review_output.sh", "normalize_code_review_output.py", "validate_code_review_output.py"):
            shutil.copy2(SCRIPTS / name, scripts / name)
        resume = scripts / "resume_review.sh"
        # Stub only the external session transport; exercise the actual repair
        # runner, validator, normalizer, artifact writes, and promotion logic.
        resume.write_text('#!/bin/bash\nprintf "called\\n" >> "$3/resumed"\ncp "$3/resume-response.md" "$3/$1-$5.md"\n')
        resume.chmod(0o755)
        artifacts = self.root / "artifacts"
        artifacts.mkdir()
        (artifacts / "cursor-raw-attempt1.md").write_text(text)
        (artifacts / "cursor-prompt.md").write_text(f"Review commit SHA: {SHA}\n")
        if resumable:
            (artifacts / "cursor-session.md").write_text("- chat_id: original-session\n")
        proc = subprocess.run(["bash", str(scripts / "repair_code_review_output.sh"), "cursor",
                               str(artifacts), str(self.root), "1"], capture_output=True, text=True)
        return proc, artifacts

    def test_runner_normalizes_without_session_or_reviewer_call(self):
        proc, artifacts = self.run_repair(REVIEW)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertFalse((artifacts / "resumed").exists())
        self.assertEqual((artifacts / "cursor-raw-attempt1.md").read_text(), REVIEW)
        self.assertEqual(validate(artifacts / "cursor.md", "cursor", 1, SHA), (0, []))
        self.assertEqual(len(list(artifacts.glob("*-normalization-round1.json"))), 1)

    def test_unrepaired_format_requests_local_coordinator_work(self):
        proc, artifacts = self.run_repair(REVIEW.replace("cursor-1", "claude-1"))
        self.assertEqual(proc.returncode, 10, proc.stderr)
        self.assertFalse((artifacts / "cursor.md").exists())
        self.assertFalse((artifacts / "resumed").exists())

    def test_possible_content_gap_requests_assessment_without_retry(self):
        proc, artifacts = self.run_repair(REVIEW.replace(" - Evidence class: reproduced", ""))
        self.assertEqual(proc.returncode, 11, proc.stderr)
        self.assertFalse((artifacts / "cursor.md").exists())

    def test_resumable_session_is_never_contacted_for_formatting(self):
        proc, artifacts = self.run_repair(REVIEW.replace("cursor-1", "claude-1"), True)
        self.assertEqual(proc.returncode, 10, proc.stderr)
        self.assertFalse((artifacts / "resumed").exists())
        self.assertFalse(list(artifacts.glob("*-format-repair*")))

    def test_recognizable_headings_are_repaired_without_inventing_sections(self):
        text = REVIEW.replace("## Should-fix", "### **Should fix:**")
        proc, artifacts = self.run_repair(text)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(validate(artifacts / "cursor.md", "cursor", 1, SHA), (0, []))
        self.assertFalse((artifacts / "resumed").exists())
        self.assertEqual((artifacts / "cursor-raw-attempt1.md").read_text(), text)

    def test_missing_heading_is_a_format_diagnostic_not_missing_substance(self):
        output = self.root / "review.md"
        output.write_text(REVIEW.replace("## Skill Feedback", "Feedback:"))
        self.assertEqual(validate(output, "cursor", 1, SHA)[0], 10)

    def assessment(self, artifacts, normalized):
        draft = artifacts / "coordinator-draft.md"
        draft.write_text(normalized)
        raw = artifacts / "cursor-raw-attempt1.md"
        value = {
            "normalized_path": str(draft),
            "source_sha256": hashlib.sha256(raw.read_bytes()).hexdigest(),
            "output_sha256": hashlib.sha256(draft.read_bytes()).hexdigest(),
            "reviewer": "cursor", "pass_number": 1, "review_sha": SHA,
            "review_scope": "saved pinned parent-to-tip scope",
            "scope_identity_evidence": str(artifacts / "cursor-prompt.md"),
            "semantic_complete": True, "all_findings_preserved": True,
            "identity_confirmed": True,
            "completeness_reason": "all coverage and evidence present in the raw review",
            "preservation_reason": "findings and evidence retained; headings/IDs repaired",
            "finding_ids": [{"source_occurrence": 1, "old": "cursor-1", "new": "code-p1-cursor-01"}],
            "changes": ["normalized finding identities; remaining heading diagnostic retained"],
        }
        path = artifacts / "assessment.json"
        path.write_text(json.dumps(value))
        return path, value

    def accept(self, artifacts, assessment):
        return subprocess.run([
            "bash", str(self.root / "scripts/repair_code_review_output.sh"), "cursor",
            str(artifacts), str(self.root), "1", "--coordinator-assessment", str(assessment)
        ], capture_output=True, text=True)

    def test_coordinator_acceptance_preserves_diagnostics_and_all_findings(self):
        raw = REVIEW.replace("## Should-fix", "Findings requiring correction:")
        proc, artifacts = self.run_repair(raw, True)
        self.assertEqual(proc.returncode, 10)
        normalized = raw.replace("cursor-1", "code-p1-cursor-01").replace("cursor-2", "code-p1-cursor-02")
        assessment, _ = self.assessment(artifacts, normalized)
        proc = self.accept(artifacts, assessment)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual((artifacts / "cursor.md").read_text(), normalized)
        self.assertEqual((artifacts / "cursor-raw-attempt1.md").read_text(), raw)
        self.assertFalse((artifacts / "resumed").exists())
        record = json.loads(next(artifacts.glob("*-normalization-round2.json")).read_text())
        self.assertEqual(record["acceptance"], "coordinator-substantive-assessment")
        self.assertEqual(record["validation_code"], 10)
        self.assertTrue(record["validation_errors"])
        self.assertEqual(record["assessment_sha256"], hashlib.sha256(assessment.read_bytes()).hexdigest())
        self.assertEqual(record["assessment"]["all_findings_preserved"], True)

    def test_assessment_requires_matching_hashes_and_substantive_confirmations(self):
        _, artifacts = self.run_repair(REVIEW.replace("cursor-1", "issue"))
        assessment, value = self.assessment(artifacts, REVIEW)
        for key, bad in (("source_sha256", "bad"), ("output_sha256", "bad"),
                         ("review_sha", "b" * 40), ("semantic_complete", False),
                         ("all_findings_preserved", False), ("identity_confirmed", False),
                         ("review_scope", ""), ("scope_identity_evidence", "")):
            with self.subTest(key=key):
                assessment.write_text(json.dumps(dict(value, **{key: bad})))
                proc = self.accept(artifacts, assessment)
                self.assertNotEqual(proc.returncode, 0)
                self.assertFalse((artifacts / "cursor.md").exists())
                self.assertFalse((artifacts / "resumed").exists())

    def test_assessment_cannot_bless_an_explicit_conflicting_commit(self):
        _, artifacts = self.run_repair(REVIEW.replace(SHA, "b" * 40))
        assessment, _ = self.assessment(artifacts, REVIEW)
        proc = self.accept(artifacts, assessment)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("conflicting pinned commit", proc.stdout)
        self.assertFalse((artifacts / "cursor.md").exists())

    def test_failed_repair_keeps_prior_canonical_evidence(self):
        _, artifacts = self.run_repair(REVIEW)
        canonical = (artifacts / "cursor.md").read_bytes()
        (artifacts / "cursor-raw-attempt2.md").write_text("ambiguous response")
        assessment, _ = self.assessment(artifacts, REVIEW)
        proc = self.accept(artifacts, assessment)
        self.assertNotEqual(proc.returncode, 0)
        self.assertEqual((artifacts / "cursor.md").read_bytes(), canonical)


if __name__ == "__main__":
    unittest.main()
