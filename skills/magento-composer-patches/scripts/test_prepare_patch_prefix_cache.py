#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("prepare_patch_prefix_cache.py")
STRICT_SCRIPT = Path(__file__).with_name("strict_patch_replay.sh")


def has_gnu_patch() -> bool:
    if shutil.which("gpatch"):
        return True
    patch = shutil.which("patch")
    if not patch:
        return False
    result = subprocess.run([patch, "--version"], text=True, capture_output=True)
    return "GNU patch" in result.stdout


@unittest.skipUnless(has_gnu_patch(), "GNU patch is required")
class PrefixCacheTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.pristine = self.root / "pristine"
        self.cache = self.root / "cache"
        self.patch = self.root / "change.patch"
        self.pristine.mkdir()
        (self.pristine / "example.txt").write_text("old\n")
        self.write_patch("new")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_patch(self, replacement: str) -> None:
        self.patch.write_text(
            "--- a/example.txt\n"
            "+++ b/example.txt\n"
            "@@ -1 +1 @@\n"
            "-old\n"
            f"+{replacement}\n"
        )

    def run_cache(self, *, check: bool = True) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--pristine-tree",
                str(self.pristine),
                "--cache-root",
                str(self.cache),
                "--strip-level",
                "1",
                "--patch",
                str(self.patch),
            ],
            text=True,
            capture_output=True,
            check=check,
        )

    def test_cache_hit_and_input_invalidation(self) -> None:
        first = json.loads(self.run_cache().stdout)
        self.assertFalse(first["cache_hit"])
        self.assertEqual(Path(first["tree"], "example.txt").read_text(), "new\n")
        self.assertEqual((self.pristine / "example.txt").read_text(), "old\n")

        second = json.loads(self.run_cache().stdout)
        self.assertTrue(second["cache_hit"])
        self.assertEqual(first["cache_key"], second["cache_key"])

        self.write_patch("newer")
        third = json.loads(self.run_cache().stdout)
        self.assertFalse(third["cache_hit"])
        self.assertNotEqual(first["cache_key"], third["cache_key"])
        self.assertEqual(Path(third["tree"], "example.txt").read_text(), "newer\n")

    def test_corrupt_entry_is_rejected(self) -> None:
        first = json.loads(self.run_cache().stdout)
        Path(first["tree"], "example.txt").write_text("tampered\n")
        result = self.run_cache(check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("corrupt cache entry", result.stderr)

    def test_cache_root_inside_pristine_is_rejected(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--pristine-tree",
                str(self.pristine),
                "--cache-root",
                str(self.pristine / "cache"),
                "--strip-level",
                "1",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must not be inside", result.stderr)

    def test_strict_replay_rejects_offset(self) -> None:
        shifted_tree = self.root / "shifted"
        shifted_tree.mkdir()
        (shifted_tree / "example.txt").write_text("extra\nold\n")
        log = self.root / "offset.log"
        result = subprocess.run(
            [
                "bash",
                str(STRICT_SCRIPT),
                str(shifted_tree),
                str(self.patch),
                str(log),
                "1",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("offset", log.read_text().lower())


if __name__ == "__main__":
    unittest.main()
