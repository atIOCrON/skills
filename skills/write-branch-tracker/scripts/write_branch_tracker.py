#!/usr/bin/env python3
"""Validate branch-tracker drafts and write a timestamped CSV."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


FIELDS = (
    "Sort",
    "Stack",
    "Target Branch",
    "Source Branch",
    "Status",
    "To Do",
    "Plan",
    "Operator problem",
    "Solution",
    "Suggested operator test path",
    "Pass condition",
    "Note",
    "Type(s)",
    "Change surface(s)",
    "Package(s)",
)
STATUSES = (
    "Draft", "Backlog", "To Do", "In Progress", "Review", "Merged", "Fulfilled",
    "Superseded", "Deprecated",
)
TYPES = ("Feature", "Fix", "Operations", "Tests", "Documentation", "Housekeeping")
SURFACES = (
    "First-party code", "Composer patch", "Theme", "Configuration",
    "Data/schema", "Tests", "Documentation", "Tooling",
)
OPERATOR_FIELDS = {"To Do", "Note"}
OPTIONAL_FIELDS = OPERATOR_FIELDS | {"Plan", "Package(s)"}
SUFFIX = "-branch-tracker.csv"
Row = dict[str, str | int]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a branch tracker or write its timestamped CSV."
    )
    parser.add_argument("rows_json", type=Path, help="JSON array containing CSV rows")
    destination = parser.add_mutually_exclusive_group(required=True)
    destination.add_argument(
        "--output-dir",
        type=Path,
        help="Directory in which to create the CSV",
    )
    destination.add_argument(
        "--validate-only", action="store_true",
        help="Print validated JSON without writing a CSV (for Google Sheets)",
    )
    parser.add_argument(
        "--timezone", default="Australia/Sydney",
        help="IANA timezone for automatic timestamps (default: Australia/Sydney)",
    )
    parser.add_argument(
        "--timestamp",
        help=(
            "Optional deterministic filename timestamp in "
            "YYYY-MM-DDTHH-MM-SS+ZZZZ form"
        ),
    )
    return parser.parse_args()


def list_value(value: str, field: str, number: int, allowed: tuple[str, ...] | None) -> str:
    if not value:
        return value
    items = [item.strip() for item in value.split(";")]
    if any(not item for item in items) or len(items) != len(set(items)):
        raise ValueError(f"row {number} field {field!r} has empty or duplicate entries")
    if allowed is not None and any(item not in allowed for item in items):
        raise ValueError(f"row {number} field {field!r} must use values from {allowed}")
    return "; ".join(items)


def load_rows(path: Path) -> list[Row]:
    try:
        raw: Any = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"cannot read {path}: {exc}") from exc
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from exc

    if not isinstance(raw, list) or not raw:
        raise ValueError("input must be a non-empty JSON array")

    expected = set(FIELDS)
    rows: list[Row] = []
    seen_branches: set[str] = set()

    for number, item in enumerate(raw, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"row {number} must be a JSON object")

        keys = set(item)
        if keys != expected:
            missing = sorted(expected - keys)
            extra = sorted(keys - expected)
            details = []
            if missing:
                details.append(f"missing {missing}")
            if extra:
                details.append(f"unexpected {extra}")
            raise ValueError(f"row {number} has invalid keys: {', '.join(details)}")

        row: Row = {}
        for field in FIELDS:
            value = item[field]
            if field in {"Sort", "Stack"}:
                if type(value) is not int or value < 1:
                    raise ValueError(f"row {number} field {field!r} must be a positive integer")
                row[field] = value
                continue
            if not isinstance(value, str):
                raise ValueError(f"row {number} field {field!r} must be text")
            if field not in OPTIONAL_FIELDS and not value.strip():
                raise ValueError(f"row {number} field {field!r} must be non-empty text")
            if "\x00" in value or "\r" in value or "\n" in value:
                raise ValueError(
                    f"row {number} field {field!r} must not contain NUL or newlines"
                )
            if field in OPERATOR_FIELDS and value != "":
                raise ValueError(f"row {number} field {field!r} must be empty in a draft")
            row[field] = value.strip()

        branch = row["Source Branch"]
        if branch in seen_branches:
            raise ValueError(f"duplicate branch in row {number}: {branch}")
        seen_branches.add(branch)
        if row["Status"] not in STATUSES:
            raise ValueError(f"row {number} Status must be one of {STATUSES}")
        list_fields = (
            ("Type(s)", TYPES),
            ("Change surface(s)", SURFACES),
            ("Package(s)", None),
        )
        for field, allowed in list_fields:
            row[field] = list_value(row[field], field, number, allowed)
        if row["Sort"] != number:
            raise ValueError(f"row {number} Sort must equal {number}")
        prior_stack = rows[-1]["Stack"] if rows else 0
        if row["Stack"] not in {prior_stack, prior_stack + 1}:
            raise ValueError(f"row {number} Stack must stay in its group or start the next number")
        rows.append(row)

    by_branch = {row["Source Branch"]: row for row in rows}
    for row in rows:
        parent = by_branch.get(row["Target Branch"])
        if parent is not None:
            if parent["Stack"] != row["Stack"]:
                raise ValueError(f"{row['Source Branch']}: requested parent must be in the same stack")
            if parent["Sort"] >= row["Sort"]:
                raise ValueError(f"{row['Source Branch']}: requested parent must precede its child")
    return rows


def filename_timestamp(raw: str | None, timezone: str = "Australia/Sydney") -> str:
    if raw is None:
        try:
            return datetime.now(ZoneInfo(timezone)).strftime("%Y-%m-%dT%H-%M-%S%z")
        except ZoneInfoNotFoundError as exc:
            raise ValueError(f"unknown timezone: {timezone}") from exc

    try:
        parsed = datetime.strptime(raw, "%Y-%m-%dT%H-%M-%S%z")
    except ValueError as exc:
        raise ValueError(
            "--timestamp must use YYYY-MM-DDTHH-MM-SS+ZZZZ format"
        ) from exc
    return parsed.strftime("%Y-%m-%dT%H-%M-%S%z")


def write_csv(rows: list[Row], output_dir: Path, timestamp: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{timestamp}{SUFFIX}"

    try:
        with output_path.open("x", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=FIELDS,
                extrasaction="raise",
                quoting=csv.QUOTE_ALL,
                lineterminator="\r\n",
            )
            writer.writeheader()
            writer.writerows(rows)
    except FileExistsError as exc:
        raise ValueError(f"refusing to overwrite existing file: {output_path}") from exc
    except OSError as exc:
        raise ValueError(f"cannot write {output_path}: {exc}") from exc

    return output_path


def main() -> int:
    args = parse_args()
    try:
        rows = load_rows(args.rows_json)
        if args.validate_only:
            print(json.dumps(rows, ensure_ascii=False, indent=2))
            return 0
        timestamp = filename_timestamp(args.timestamp, args.timezone)
        output_path = write_csv(rows, args.output_dir, timestamp)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
