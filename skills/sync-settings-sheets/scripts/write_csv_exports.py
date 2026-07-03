#!/usr/bin/env python3
"""Write Google Drive CSV export results into data/settings."""

from __future__ import annotations

import argparse
import base64
import csv
import io
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any


CSV_MIME_TYPE = "text/csv"


class WriteResult:
    def __init__(self, path: Path, changed: bool) -> None:
        self.path = path
        self.changed = changed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Overwrite existing settings CSVs from Google Drive export JSON."
    )
    parser.add_argument(
        "--input",
        default="-",
        help="JSONL or JSON array file of connector export results; use '-' for stdin.",
    )
    parser.add_argument(
        "--target-dir",
        default="data/settings",
        help="Directory containing existing CSV files to overwrite.",
    )
    parser.add_argument(
        "--expected-count",
        type=int,
        default=21,
        help="Exact number of export records required.",
    )
    parser.add_argument(
        "--allow-new",
        action="store_true",
        help="Allow writing CSV files that do not already exist.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and print planned writes without modifying files.",
    )
    return parser.parse_args()


def read_input(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def load_records(raw_input: str) -> list[dict[str, Any]]:
    stripped = raw_input.strip()
    if not stripped:
        raise ValueError("No export records were provided.")

    if stripped[0] in "[{":
        try:
            parsed = json.loads(stripped)
        except json.JSONDecodeError:
            parsed = None
        if isinstance(parsed, list):
            return require_record_list(parsed)
        if isinstance(parsed, dict) and isinstance(parsed.get("records"), list):
            return require_record_list(parsed["records"])
        if isinstance(parsed, dict):
            return [parsed]

    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(raw_input.splitlines(), start=1):
        if not line.strip():
            continue
        parsed = json.loads(line)
        if not isinstance(parsed, dict):
            raise ValueError(f"Line {line_number} is not a JSON object.")
        records.append(parsed)
    return records


def require_record_list(values: list[Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for index, value in enumerate(values, start=1):
        if not isinstance(value, dict):
            raise ValueError(f"Record {index} is not a JSON object.")
        records.append(value)
    return records


def merged_record(record: dict[str, Any]) -> dict[str, Any]:
    structured = record.get("structuredContent")
    if isinstance(structured, dict):
        merged = dict(structured)
        merged.update({key: value for key, value in record.items() if value is not None})
        return merged
    return record


def record_title(record: dict[str, Any], index: int) -> str:
    title = record.get("title") or record.get("display_title")
    if not isinstance(title, str) or not title.strip():
        raise ValueError(f"Record {index} is missing a title.")
    if "/" in title or "\\" in title or title in {".", ".."}:
        raise ValueError(f"Record {index} has an unsafe title: {title!r}.")
    return title.strip()


def record_file_name(record: dict[str, Any], title: str) -> str:
    file_name = record.get("file_name")
    if isinstance(file_name, str) and file_name.strip():
        name = file_name.strip()
    else:
        name = f"{title}.csv"
    if "/" in name or "\\" in name or name in {".", ".."}:
        raise ValueError(f"Unsafe output filename for {title!r}: {name!r}.")
    if not name.endswith(".csv"):
        raise ValueError(f"Output filename for {title!r} is not a CSV: {name!r}.")
    return name


def record_payload(record: dict[str, Any], title: str) -> bytes:
    b64_string = record.get("b64_string")
    if isinstance(b64_string, str):
        return base64.b64decode(b64_string, validate=True)

    content = record.get("content")
    if isinstance(content, str):
        return content.encode("utf-8")

    payload_path = record.get("payload_path") or record.get("local_path")
    if isinstance(payload_path, str) and payload_path.strip():
        return Path(payload_path).read_bytes()

    download_url = record.get("download_url")
    file_uri = record.get("file_uri")
    if not download_url and isinstance(file_uri, dict):
        download_url = file_uri.get("download_url")
    if download_url:
        raise ValueError(
            f"Record for {title!r} contains only a volatile download_url. "
            "Download it immediately first and provide payload_path."
        )

    raise ValueError(
        f"Record for {title!r} has no durable payload. Expected b64_string, "
        "content, or payload_path."
    )


def csv_header(payload: bytes, label: str) -> list[str]:
    if not payload:
        raise ValueError(f"{label} is empty.")
    try:
        text = payload.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError(f"{label} is not valid UTF-8 CSV.") from exc

    try:
        reader = csv.reader(io.StringIO(text, newline=""), strict=True)
        header = next(reader)
        for _row in reader:
            pass
    except StopIteration as exc:
        raise ValueError(f"{label} has no header row.") from exc
    except csv.Error as exc:
        raise ValueError(f"{label} is not parseable CSV: {exc}") from exc

    if not any(cell.strip() for cell in header):
        raise ValueError(f"{label} has an empty header row.")
    return header


def validate_payload(payload: bytes, target_path: Path, title: str) -> None:
    exported_header = csv_header(payload, f"Export for {title!r}")
    target_header = csv_header(target_path.read_bytes(), f"Target {target_path}")
    if exported_header != target_header:
        raise ValueError(
            f"Header mismatch for {target_path}: "
            f"exported {exported_header!r}, target {target_header!r}."
        )


def validate_csv_mime(record: dict[str, Any], title: str) -> None:
    mime_values = {
        record.get("mimeType"),
        record.get("mime_type"),
    }
    file_uri = record.get("file_uri")
    if isinstance(file_uri, dict):
        mime_values.add(file_uri.get("mime_type"))
    present = {value for value in mime_values if isinstance(value, str)}
    if present and CSV_MIME_TYPE not in present:
        raise ValueError(f"Record for {title!r} is not a CSV export: {sorted(present)}.")


def atomic_write(path: Path, payload: bytes) -> None:
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as temp_file:
        temp_name = Path(temp_file.name)
        temp_file.write(payload)
    os.replace(temp_name, path)


def apply_exports(
    records: list[dict[str, Any]],
    target_dir: Path,
    expected_count: int,
    allow_new: bool,
    dry_run: bool,
) -> list[WriteResult]:
    if len(records) != expected_count:
        raise ValueError(f"Expected {expected_count} records, received {len(records)}.")
    if not target_dir.is_dir():
        raise ValueError(f"Target directory does not exist: {target_dir}")

    seen_titles: set[str] = set()
    written: list[WriteResult] = []

    for index, raw_record in enumerate(records, start=1):
        record = merged_record(raw_record)
        title = record_title(record, index)
        if title in seen_titles:
            raise ValueError(f"Duplicate export title: {title!r}.")
        seen_titles.add(title)

        validate_csv_mime(record, title)
        file_name = record_file_name(record, title)
        target_path = target_dir / file_name
        if target_path.parent.resolve() != target_dir.resolve():
            raise ValueError(f"Output path escapes target directory: {target_path}")
        if not allow_new and not target_path.exists():
            raise ValueError(f"Refusing to create missing target file: {target_path}")

        payload = record_payload(record, title)
        if target_path.exists():
            validate_payload(payload, target_path, title)
        else:
            csv_header(payload, f"Export for {title!r}")
        changed = not target_path.exists() or target_path.read_bytes() != payload
        if not dry_run and changed:
            atomic_write(target_path, payload)
        written.append(WriteResult(path=target_path, changed=changed))

    return written


def main() -> int:
    args = parse_args()
    try:
        raw_input = read_input(args.input)
        records = load_records(raw_input)
        written = apply_exports(
            records=records,
            target_dir=Path(args.target_dir),
            expected_count=args.expected_count,
            allow_new=args.allow_new,
            dry_run=args.dry_run,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    action = "Validated" if args.dry_run else "Processed"
    changed_count = sum(1 for result in written if result.changed)
    print(f"{action} {len(written)} CSV files; {changed_count} changed.")
    for result in sorted(written, key=lambda item: str(item.path)):
        status = "CHANGED" if result.changed else "UNCHANGED"
        print(f" - {status} {result.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
