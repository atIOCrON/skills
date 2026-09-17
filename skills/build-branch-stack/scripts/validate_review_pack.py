#!/usr/bin/env python3
"""Validate a pinned review pack's evidence, links, and file hashes."""

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(pack, repo):
    errors = []
    pack = pack.resolve()
    repo = repo.resolve()
    manifest = pack / "evidence-manifest.json"
    try:
        data = json.loads(manifest.read_text())
        review_sha = data["review_sha"]
        checks = data["checks"]
        if not re.fullmatch(r"[0-9a-f]{40,64}", review_sha) or not isinstance(checks, list):
            raise ValueError("invalid review SHA or checks")
        resolved = subprocess.check_output(
            ["git", "-C", str(repo), "rev-parse", "--verify", f"{review_sha}^{{commit}}"],
            text=True,
        ).strip()
        if resolved != review_sha:
            errors.append("review_sha is not the resolved full commit SHA")
    except (OSError, KeyError, ValueError, subprocess.CalledProcessError) as exc:
        errors.append(f"invalid evidence manifest: {exc}")
        checks = []
        review_sha = None

    ids = set()
    for i, check in enumerate(checks):
        label = f"check {i + 1}"
        try:
            label = check["id"]
            if not isinstance(label, str) or not label:
                raise ValueError("missing id")
            if label in ids:
                raise ValueError("duplicate id")
            ids.add(label)
            if check["kind"] not in ("agent", "external"):
                raise ValueError("invalid kind")
            if type(check["required"]) is not bool:
                raise ValueError("required must be a boolean")
            if check["result"] not in ("passed", "failed", "pending", "blocked_by_environment"):
                raise ValueError("invalid result")
            if not isinstance(check["command"], str) or not check["command"].strip():
                raise ValueError("missing command or procedure")
            if not isinstance(check["runtime"], str) or not check["runtime"].strip():
                raise ValueError("missing runtime")
            sha = check["last_run_sha"]
            if sha is not None and not (isinstance(sha, str) and re.fullmatch(r"[0-9a-f]{40,64}", sha)):
                raise ValueError("invalid last_run_sha")
            if check["required"] and check["kind"] == "agent" and check["result"] == "passed" and sha != review_sha:
                raise ValueError("passed required agent check ran on another SHA")
            path, expected = check["log_path"], check["log_sha256"]
            if (path is None) != (expected is None):
                raise ValueError("log path and hash must both be set or null")
            if check["result"] in ("passed", "failed") and (path is None or sha is None):
                raise ValueError("completed check needs a log and tested SHA")
            if path is not None:
                if not isinstance(path, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
                    raise ValueError("invalid log path or SHA-256")
                log = (pack / path).resolve()
                if not log.is_file() or digest(log) != expected:
                    raise ValueError(f"missing or changed log: {path}")
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"{label}: {exc}")

    hashes = pack / "hash-manifest.sha256"
    listed = set()
    try:
        for line in hashes.read_text().splitlines():
            match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
            if not match:
                errors.append(f"invalid hash line: {line}")
                continue
            expected, name = match.groups()
            path = (pack / name).resolve()
            if path.parent != pack or not path.is_file() or digest(path) != expected:
                errors.append(f"missing or changed pack file: {name}")
            listed.add(name)
    except OSError as exc:
        errors.append(f"cannot read hash manifest: {exc}")
    actual = {p.name for p in pack.iterdir() if p.is_file() and p.name != hashes.name}
    if listed != actual:
        errors.append(f"hash manifest coverage differs: missing {sorted(actual - listed)}, extra {sorted(listed - actual)}")
    required_files = {
        "index.md", "changed-files.txt", "diff-stat.txt", "changes.diff",
        "ownership-map.md", "verification-summary.md", "evidence-manifest.json",
        "acceptance-gates.md", "deterministic-checks.md",
    }
    if required_files - actual:
        errors.append(f"missing required pack files: {sorted(required_files - actual)}")
    if review_sha and (pack / "index.md").is_file() and review_sha not in (pack / "index.md").read_text():
        errors.append("index.md does not identify the review SHA")

    for page in pack.glob("*.md"):
        for target in re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", page.read_text()):
            target = unquote(target.split("#", 1)[0].strip("<>"))
            if not target or re.match(r"[a-z][a-z0-9+.-]*:", target, re.I):
                continue
            if not (page.parent / target).resolve().exists():
                errors.append(f"broken link in {page.name}: {target}")

    for error in errors:
        print(error, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: validate_review_pack.py <pack-dir> <repo-root>")
    sys.exit(main(Path(sys.argv[1]), Path(sys.argv[2])))
