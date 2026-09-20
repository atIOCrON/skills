#!/usr/bin/env python3
"""Build or reuse an identity-validated Composer patch-prefix tree."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
from datetime import datetime, timezone


SCHEMA_VERSION = 1


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def add_field(digest: "hashlib._Hash", value: bytes) -> None:
    digest.update(len(value).to_bytes(8, "big"))
    digest.update(value)


def hash_tree(root: Path) -> str:
    digest = hashlib.sha256()
    entries = sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix())
    for path in entries:
        relative = path.relative_to(root).as_posix().encode()
        mode = stat.S_IMODE(path.lstat().st_mode)
        if path.is_symlink():
            kind = b"symlink"
            content = os.readlink(path).encode()
        elif path.is_dir():
            kind = b"directory"
            content = b""
        elif path.is_file():
            kind = b"file"
            content = bytes.fromhex(hash_file(path))
        else:
            raise ValueError(f"unsupported filesystem entry: {path}")
        for field in (relative, kind, str(mode).encode(), content):
            add_field(digest, field)
    return digest.hexdigest()


def find_gnu_patch() -> dict[str, str]:
    for name in ("gpatch", "patch"):
        executable = shutil.which(name)
        if not executable:
            continue
        result = subprocess.run(
            [executable, "--version"],
            text=True,
            capture_output=True,
            check=False,
        )
        first_line = (result.stdout or result.stderr).splitlines()[0] if (
            result.stdout or result.stderr
        ) else ""
        if name == "gpatch" or "GNU patch" in first_line:
            return {"command": name, "version": first_line}
    raise RuntimeError("GNU patch is required; install gpatch on macOS")


def canonical_json(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def validate_entry(entry: Path, expected_inputs: dict[str, object]) -> dict[str, object]:
    manifest_path = entry / "manifest.json"
    tree_path = entry / "tree"
    try:
        manifest = json.loads(manifest_path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(f"corrupt cache entry {entry}: invalid manifest: {error}") from error
    if manifest.get("schema_version") != SCHEMA_VERSION:
        raise RuntimeError(f"corrupt cache entry {entry}: unexpected schema version")
    if manifest.get("inputs") != expected_inputs:
        raise RuntimeError(f"corrupt cache entry {entry}: input identity mismatch")
    if not tree_path.is_dir():
        raise RuntimeError(f"corrupt cache entry {entry}: cached tree is missing")
    actual_tree_hash = hash_tree(tree_path)
    expected_tree_hash = manifest.get("output_tree_sha256")
    if actual_tree_hash != expected_tree_hash:
        raise RuntimeError(
            f"corrupt cache entry {entry}: output tree identity mismatch "
            f"({actual_tree_hash} != {expected_tree_hash})"
        )
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build or reuse a strictly replayed Composer patch prefix."
    )
    parser.add_argument("--pristine-tree", required=True, type=Path)
    parser.add_argument("--cache-root", required=True, type=Path)
    parser.add_argument("--strip-level", required=True, type=int)
    parser.add_argument("--patch", action="append", default=[], type=Path)
    return parser.parse_args()


def emit_result(
    *, entry: Path, cache_key: str, cache_hit: bool, patch_sources: list[Path]
) -> None:
    print(
        json.dumps(
            {
                "cache_hit": cache_hit,
                "cache_key": cache_key,
                "tree": str(entry / "tree"),
                "manifest": str(entry / "manifest.json"),
                "logs": str(entry / "logs"),
                "patch_sources": [str(path) for path in patch_sources],
            },
            indent=2,
            sort_keys=True,
        )
    )


def main() -> int:
    args = parse_args()
    if args.strip_level < 0:
        raise ValueError("--strip-level must be non-negative")

    pristine = args.pristine_tree.resolve()
    patches = [path.resolve() for path in args.patch]
    cache_root = args.cache_root.resolve()
    strict_script = Path(__file__).with_name("strict_patch_replay.sh").resolve()

    if not pristine.is_dir():
        raise ValueError(f"pristine tree does not exist: {pristine}")
    try:
        cache_root.relative_to(pristine)
    except ValueError:
        pass
    else:
        raise ValueError("--cache-root must not be inside --pristine-tree")
    if not strict_script.is_file():
        raise ValueError(f"strict replay script does not exist: {strict_script}")
    for patch in patches:
        if not patch.is_file():
            raise ValueError(f"patch does not exist: {patch}")

    inputs: dict[str, object] = {
        "pristine_tree_sha256": hash_tree(pristine),
        "patches": [{"sha256": hash_file(path)} for path in patches],
        "strip_level": args.strip_level,
        "strict_replay_sha256": hash_file(strict_script),
        "patch_tool": find_gnu_patch(),
    }
    cache_key = hashlib.sha256(canonical_json(inputs)).hexdigest()
    cache_root.mkdir(parents=True, exist_ok=True)
    entry = cache_root / cache_key

    if entry.exists():
        validate_entry(entry, inputs)
        emit_result(
            entry=entry,
            cache_key=cache_key,
            cache_hit=True,
            patch_sources=patches,
        )
        return 0

    temporary = Path(tempfile.mkdtemp(prefix=f".building-{cache_key[:12]}-", dir=cache_root))
    tree = temporary / "tree"
    logs = temporary / "logs"
    try:
        shutil.copytree(pristine, tree, symlinks=True)
        logs.mkdir()
        for index, patch in enumerate(patches, start=1):
            log = logs / f"{index:03d}.log"
            subprocess.run(
                [
                    "bash",
                    str(strict_script),
                    str(tree),
                    str(patch),
                    str(log),
                    str(args.strip_level),
                ],
                check=True,
            )
        manifest = {
            "schema_version": SCHEMA_VERSION,
            "cache_key": cache_key,
            "inputs": inputs,
            "output_tree_sha256": hash_tree(tree),
        }
        (temporary / "manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n"
        )
        try:
            temporary.rename(entry)
        except OSError:
            if not entry.exists():
                raise
            shutil.rmtree(temporary)
            validate_entry(entry, inputs)
            emit_result(
                entry=entry,
                cache_key=cache_key,
                cache_hit=True,
                patch_sources=patches,
            )
            return 0
    except Exception:
        if temporary.exists():
            failure_root = cache_root / "failures"
            failure_root.mkdir(exist_ok=True)
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            failure = failure_root / f"{cache_key[:16]}-{stamp}-{os.getpid()}"
            temporary.rename(failure)
            print(f"failed replay retained at {failure}", file=sys.stderr)
        raise

    emit_result(
        entry=entry,
        cache_key=cache_key,
        cache_hit=False,
        patch_sources=patches,
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, ValueError, subprocess.CalledProcessError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
