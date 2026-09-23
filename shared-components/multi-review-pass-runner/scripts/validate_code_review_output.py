#!/usr/bin/env python3
"""Validate the machine-actionable code-review response schema."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


HEADINGS = (
    "## Blockers",
    "## Should-fix",
    "## Nits",
    "## Contradictions",
    "## Related Existing Issues",
    "## Proportionality",
    "## Skill Feedback",
)
FINDING_SECTIONS = HEADINGS[:5]
STATUSES = {
    "Fix blockers before next pass",
    "Resolve contradictions",
    "Address findings before next pass",
    "Review pass clean",
}
ALL_FINDING_ID = re.compile(r"code-p\d+-(?:claude|codex|cursor)-\d{2}")

FORMAT_REPAIRABLE = 10
COMPLETION_REPAIRABLE = 11
FRESH_RETRY_REQUIRED = 12


def section_lines(lines: list[str], heading: str) -> list[str]:
    start = lines.index(heading) + 1
    later = [lines.index(item) for item in HEADINGS if item in lines and lines.index(item) >= start]
    status_positions = [index for index, line in enumerate(lines) if line in STATUSES and index >= start]
    end_positions = later + status_positions
    end = min(end_positions) if end_positions else len(lines)
    return [line for line in lines[start:end] if line.strip()]


def validate(path: Path, reviewer: str, pass_number: int) -> tuple[int, list[str]]:
    if not path.is_file() or path.stat().st_size == 0:
        return FRESH_RETRY_REQUIRED, ["review output is missing or empty"]

    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    nonempty = [line for line in lines if line.strip()]
    if not nonempty:
        return FRESH_RETRY_REQUIRED, ["review output contains no content"]

    format_errors: list[str] = []
    completion_errors: list[str] = []
    heading_positions: list[int] = []

    for heading in HEADINGS:
        count = lines.count(heading)
        if count == 0:
            completion_errors.append(f"missing heading: {heading}")
        elif count > 1:
            format_errors.append(f"heading appears {count} times: {heading}")
        else:
            heading_positions.append(lines.index(heading))

    if len(heading_positions) == len(HEADINGS) and heading_positions != sorted(heading_positions):
        format_errors.append("headings are out of order")
    if nonempty[0] != HEADINGS[0]:
        format_errors.append("preamble or incorrect first heading")
    unexpected_headings = sorted({line for line in lines if line.startswith("## ") and line not in HEADINGS})
    if unexpected_headings:
        format_errors.append(f"unexpected headings: {', '.join(unexpected_headings)}")

    status_lines = [line for line in nonempty if line in STATUSES]
    if len(status_lines) != 1:
        format_errors.append(f"expected one permitted status line; found {len(status_lines)}")
    if not status_lines or nonempty[-1] != status_lines[-1]:
        format_errors.append("trailing text or missing final status line")

    expected_id = re.compile(rf"code-p{pass_number}-{re.escape(reviewer)}-\d{{2}}")
    found_ids = ALL_FINDING_ID.findall(text)
    wrong_ids = sorted({finding_id for finding_id in found_ids if not expected_id.fullmatch(finding_id)})
    if wrong_ids:
        format_errors.append(f"finding IDs use the wrong pass or reviewer: {', '.join(wrong_ids)}")

    if all(lines.count(heading) == 1 for heading in HEADINGS):
        for heading in HEADINGS:
            body = section_lines(lines, heading)
            if not body:
                completion_errors.append(f"empty section: {heading}; use - None")
                continue
            if "- None" in body and body != ["- None"]:
                format_errors.append(f"{heading} mixes - None with other content")

        for heading in FINDING_SECTIONS:
            body = section_lines(lines, heading)
            if body == ["- None"]:
                continue
            bullets = [line for line in body if line.startswith("- ")]
            if not bullets:
                completion_errors.append(f"{heading} contains no finding bullets")
                continue
            for bullet in bullets:
                match = re.match(r"^- \[([^]]+)]", bullet)
                if not match or not expected_id.fullmatch(match.group(1)):
                    format_errors.append(f"invalid finding ID in {heading}: {bullet[:100]}")
                if " - Evidence:" not in bullet:
                    completion_errors.append(f"finding lacks evidence in {heading}: {bullet[:100]}")
                if " - Recommendation:" not in bullet:
                    completion_errors.append(f"finding lacks recommendation in {heading}: {bullet[:100]}")

        proportionality = section_lines(lines, "## Proportionality")
        if len(proportionality) != 1 or not re.match(
            r"^- (?:Proportionate|Not proportionate)\s+-\s+\S", proportionality[0]
        ):
            format_errors.append("proportionality must contain exactly one permitted line")

    if completion_errors:
        return COMPLETION_REPAIRABLE, completion_errors + format_errors
    if format_errors:
        return FORMAT_REPAIRABLE, format_errors
    return 0, []


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("reviewer", choices=("claude", "codex", "cursor"))
    parser.add_argument("pass_number", type=int)
    args = parser.parse_args()

    code, errors = validate(args.output, args.reviewer, args.pass_number)
    labels = {
        0: "valid",
        FORMAT_REPAIRABLE: "format-repairable",
        COMPLETION_REPAIRABLE: "completion-repairable",
        FRESH_RETRY_REQUIRED: "fresh-retry-required",
    }
    print(f"classification: {labels[code]}")
    for error in errors:
        print(f"- {error}")
    return code


if __name__ == "__main__":
    sys.exit(main())
