#!/usr/bin/env python3
"""Validate branch-description rows and write the standard timestamped CSV."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


FIELDS = (
    "Branch",
    "Operator problem",
    "Solution",
    "Suggested operator test path",
    "Pass condition",
)
SUFFIX = "-branch-problem-solution-test-descriptions.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Write a validated branch problem/solution/test CSV."
    )
    parser.add_argument("rows_json", type=Path, help="JSON array containing CSV rows")
    parser.add_argument(
        "--output-dir",
        required=True,
        type=Path,
        help="Directory in which to create the CSV",
    )
    parser.add_argument(
        "--timestamp",
        help=(
            "Optional deterministic filename timestamp in "
            "YYYY-MM-DDTHH-MM-SS+ZZZZ form"
        ),
    )
    return parser.parse_args()


def load_rows(path: Path) -> list[dict[str, str]]:
    try:
        raw: Any = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from exc

    if not isinstance(raw, list) or not raw:
        raise ValueError("input must be a non-empty JSON array")

    expected = set(FIELDS)
    rows: list[dict[str, str]] = []
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

        row: dict[str, str] = {}
        for field in FIELDS:
            value = item[field]
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"row {number} field {field!r} must be non-empty text")
            if "\x00" in value or "\r" in value or "\n" in value:
                raise ValueError(
                    f"row {number} field {field!r} must not contain NUL or newlines"
                )
            row[field] = value.strip()

        branch = row["Branch"]
        if branch in seen_branches:
            raise ValueError(f"duplicate branch in row {number}: {branch}")
        seen_branches.add(branch)
        rows.append(row)

    return rows


def filename_timestamp(raw: str | None) -> str:
    if raw is None:
        return datetime.now().astimezone().strftime("%Y-%m-%dT%H-%M-%S%z")

    try:
        parsed = datetime.strptime(raw, "%Y-%m-%dT%H-%M-%S%z")
    except ValueError as exc:
        raise ValueError(
            "--timestamp must use YYYY-MM-DDTHH-MM-SS+ZZZZ format"
        ) from exc
    return parsed.strftime("%Y-%m-%dT%H-%M-%S%z")


def write_csv(rows: list[dict[str, str]], output_dir: Path, timestamp: str) -> Path:
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
        timestamp = filename_timestamp(args.timestamp)
        output_path = write_csv(rows, args.output_dir, timestamp)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
