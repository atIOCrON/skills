#!/usr/bin/env python3
"""Repair presentation locally or record a coordinator's substantive assessment."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from validate_code_review_output import FINDING_SECTIONS, HEADINGS, FORMAT_REPAIRABLE, validate


def normalize_headings(text: str) -> str:
    """Repair recognizable Markdown headings without inventing absent sections."""
    names = {heading[3:].casefold(): heading for heading in HEADINGS}
    names["should fix"] = "## Should-fix"
    lines = text.splitlines(keepends=True)
    for index, line in enumerate(lines):
        match = re.fullmatch(r"\s*#{1,6}\s+(.+?)\s*#*\s*", line.rstrip("\r\n"))
        if match:
            name = match.group(1).strip().strip("*").rstrip(":").casefold()
            if name in names:
                ending = line[len(line.rstrip("\r\n")):]
                lines[index] = names[name] + ending
    return "".join(lines)


def normalize(text: str, reviewer: str, pass_number: int) -> tuple[str, dict[str, str]]:
    if re.search(r"^\s*(?:`{3,}|~{3,})", text, re.MULTILINE):
        raise ValueError("fenced source/evidence needs coordinator normalization")
    canonical = re.compile(rf"code-p{pass_number}-{reviewer}-\d{{2}}")
    legacy = re.compile(rf"{reviewer}-\d+")
    lines = normalize_headings(text).splitlines(keepends=True)
    definitions: list[tuple[int, str]] = []
    section = ""
    for index, line in enumerate(lines):
        if line.startswith("## "):
            section = line.rstrip("\r\n")
        if section in FINDING_SECTIONS and line.startswith("- ["):
            match = re.match(r"- \[([^]]+)]", line)
            if not match:
                raise ValueError("ambiguous finding definition")
            finding_id = match.group(1)
            if not (canonical.fullmatch(finding_id) or legacy.fullmatch(finding_id)):
                raise ValueError("ID does not belong unambiguously to this reviewer and pass")
            definitions.append((index, finding_id))

    ids = [finding_id for _, finding_id in definitions]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate finding IDs cannot be normalized")
    reserved = set(ids)
    mapping: dict[str, str] = {}
    for _, finding_id in definitions:
        if canonical.fullmatch(finding_id):
            continue
        new_id = next(
            (f"code-p{pass_number}-{reviewer}-{number:02d}" for number in range(1, 100)
             if f"code-p{pass_number}-{reviewer}-{number:02d}" not in reserved),
            None,
        )
        if new_id is None:
            raise ValueError("no unused two-digit finding ID")
        mapping[finding_id] = new_id
        reserved.add(new_id)

    for index, finding_id in definitions:
        if finding_id in mapping:
            lines[index] = lines[index].replace(f"- [{finding_id}]", f"- [{mapping[finding_id]}]", 1)

    # Only the identity field and proportionality references may change. Never
    # rewrite quoted code, evidence, paths, commands, or recommendations.
    if mapping:
        tokens = re.compile(r"(?<![\w-])(?:" + "|".join(map(re.escape, mapping)) + r")(?![\w-])")
        section = ""
        for index, line in enumerate(lines):
            if line.startswith("## "):
                section = line.rstrip("\r\n")
            if section == "## Proportionality":
                lines[index] = tokens.sub(lambda match: mapping[match.group()], line)
            elif tokens.search(line):
                raise ValueError("legacy ID outside a safe identity/reference field; coordinator repair required")
    return "".join(lines), mapping


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assessed_output(args: argparse.Namespace) -> tuple[str, dict]:
    assessment = json.loads(args.assessment.read_text())
    if not isinstance(assessment, dict):
        raise ValueError("assessment must be a JSON object")
    candidate = Path(assessment.get("normalized_path", ""))
    if not candidate.is_absolute() or not candidate.is_file():
        raise ValueError("assessment must identify a nonempty absolute normalized_path")
    source_text, candidate_text = args.source.read_text(), candidate.read_text()
    if not candidate_text.strip():
        raise ValueError("assessment must identify a nonempty absolute normalized_path")
    expected = {
        "source_sha256": digest(args.source),
        "output_sha256": digest(candidate),
        "reviewer": args.reviewer,
        "pass_number": args.pass_number,
        "review_sha": args.review_sha,
        "semantic_complete": True,
        "all_findings_preserved": True,
        "identity_confirmed": True,
    }
    if not args.review_sha or not source_text.strip():
        raise ValueError("assessment cannot accept missing review content or pinned identity")
    for key, value in expected.items():
        if assessment.get(key) != value or type(assessment.get(key)) is not type(value):
            raise ValueError(f"assessment mismatch or missing confirmation: {key}")
    for key in ("review_scope", "scope_identity_evidence", "completeness_reason", "preservation_reason"):
        if not isinstance(assessment.get(key), str) or not assessment[key].strip():
            raise ValueError(f"assessment needs an explanation: {key}")
    for key in ("finding_ids", "changes"):
        if not isinstance(assessment.get(key), list):
            raise ValueError(f"assessment needs an explicit list: {key}")
    # A formatting decision cannot silently bless an explicit commit conflict.
    for text in (source_text, candidate_text):
        pins = re.findall(r"Pinned SHA:\s*([0-9a-f]{40})", text)
        if any(pin != args.review_sha for pin in pins):
            raise ValueError("conflicting pinned commit identity requires clarification")
    return candidate_text, assessment


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("mapping", type=Path)
    parser.add_argument("reviewer", choices=("claude", "codex", "cursor"))
    parser.add_argument("pass_number", type=int)
    parser.add_argument("review_sha", nargs="?")
    parser.add_argument("--assessment", type=Path,
                        help="coordinator JSON assessment of a locally repaired complete review")
    args = parser.parse_args()
    if args.pass_number < 1:
        parser.error("pass_number must be positive")
    if args.review_sha and not re.fullmatch(r"[0-9a-f]{40}", args.review_sha):
        parser.error("review_sha must be a full lowercase SHA")
    if len({path.resolve() for path in (args.source, args.output, args.mapping)}) != 3:
        parser.error("source, output, and mapping must be distinct")
    if args.output.exists() or args.mapping.exists():
        parser.error("refusing to overwrite normalization artifacts")
    code, errors = validate(args.source, args.reviewer, args.pass_number, args.review_sha)
    if not args.assessment and code not in (0, FORMAT_REPAIRABLE):
        print("coordinator assessment required: diagnostics may indicate missing substance")
        for error in errors:
            print(f"- {error}")
        return code
    try:
        if args.assessment:
            normalized, assessment = assessed_output(args)
            mapping = assessment["finding_ids"]
        else:
            source_text = args.source.read_text()
            normalized, mapping = normalize(source_text, args.reviewer, args.pass_number)
            assessment = None
    except (ValueError, OSError, TypeError) as error:
        print(f"coordinator attention required: {error}")
        return FORMAT_REPAIRABLE
    if not args.assessment and normalized == source_text and code != 0:
        print("coordinator normalization required; no automatic safe transformation")
        return FORMAT_REPAIRABLE
    args.output.write_text(normalized)
    code, errors = validate(args.output, args.reviewer, args.pass_number, args.review_sha)
    args.mapping.write_text(json.dumps({
        "source": str(args.source.resolve()),
        "source_sha256": digest(args.source),
        "output": str(args.output.resolve()),
        "output_sha256": digest(args.output),
        "reviewer": args.reviewer,
        "pass_number": args.pass_number,
        "review_sha": args.review_sha,
        "finding_ids": mapping,
        "validation_code": code,
        "validation_errors": errors,
        "acceptance": "coordinator-substantive-assessment" if assessment else "serialization-valid",
        "assessment": assessment,
        "assessment_path": str(args.assessment.resolve()) if args.assessment else None,
        "assessment_sha256": digest(args.assessment) if args.assessment else None,
    }, indent=2) + "\n")
    accepted = code == 0 or assessment is not None
    print("classification: accepted" if accepted else "coordinator normalization required")
    for error in errors:
        print(f"- {error}")
    return 0 if accepted else code


if __name__ == "__main__":
    raise SystemExit(main())
