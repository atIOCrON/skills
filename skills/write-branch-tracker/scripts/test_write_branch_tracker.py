#!/usr/bin/env python3
"""Exercise ordering, draft ownership, CSV round trips, and CLI validation."""

import copy
import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import write_branch_tracker as tracker


def row(sort, stack, branch, target="master"):
    return {
        "Sort": sort, "Stack": stack,
        "Target Branch": target, "Source Branch": branch, "Status": "Review",
        "To Do": "", "Plan": "", "Note": "", "Package(s)": "",
        "Operator problem": 'An export drops valid rows, including "café".',
        "Solution": "Preserve valid rows.",
        "Suggested operator test path": "Run the isolated export fixture.",
        "Pass condition": "The fixture's valid rows all appear.",
        "Type(s)": "Fix", "Change surface(s)": "First-party code; Tests",
    }


class TrackerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.input = self.root / "rows.json"
        self.rows = [
            row(1, 1, "feature/export"),
            row(2, 1, "feature/consumer", "feature/export"),
            row(3, 2, "feature/docs"),
        ]

    def load(self, rows):
        self.input.write_text(json.dumps(rows), encoding="utf-8")
        return tracker.load_rows(self.input)

    def test_csv_round_trip_and_no_overwrite(self):
        self.rows[0]["Status"] = "In Release"
        self.rows[1]["Status"] = "Merged"
        rows = self.load(self.rows)
        path = tracker.write_csv(rows, self.root, "2026-10-02T12-00-00+1000")
        data = path.read_bytes()
        self.assertTrue(data.startswith(b"\xef\xbb\xbf"))
        self.assertTrue(data.endswith(b"\r\n"))
        self.assertNotIn(b"\n", data.replace(b"\r\n", b""))
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            self.assertEqual(reader.fieldnames, list(tracker.FIELDS))
            actual = list(reader)
        self.assertEqual(actual, [{key: str(value) for key, value in r.items()} for r in rows])
        self.assertEqual(path.name, "2026-10-02T12-00-00+1000-branch-tracker.csv")
        with self.assertRaisesRegex(ValueError, "overwrite"):
            tracker.write_csv(rows, self.root, "2026-10-02T12-00-00+1000")
        self.assertEqual(path.read_bytes(), data)

    def test_invalid_schema_values(self):
        cases = [
            ("Sort", True), ("Sort", "1"), ("Sort", 2), ("Stack", 0),
            ("Stack", 2), ("Status", "Complete"), ("Status", "In Review"),
            ("To Do", "Call operator"), ("Note", " "),
            ("Operator problem", ""), ("Plan", None), ("Solution", "one\ntwo"),
            ("Type(s)", "Configuration"), ("Type(s)", "Customisation"),
            ("Type(s)", "Fix; Fix"), ("Change surface(s)", "First-party plugin"),
            ("Package(s)", "vendor/package;"),
        ]
        for field, value in cases:
            with self.subTest(field=field, value=value):
                rows = copy.deepcopy(self.rows)
                rows[0][field] = value
                with self.assertRaises(ValueError):
                    self.load(rows)
        missing = copy.deepcopy(self.rows)
        del missing[0]["Plan"]
        with self.assertRaisesRegex(ValueError, "missing"):
            self.load(missing)

    def test_bad_dependency_order_and_groups(self):
        for target in ("feature/consumer", "feature/export"):
            rows = copy.deepcopy(self.rows)
            rows[0]["Target Branch"] = target
            with self.assertRaisesRegex(ValueError, "precede"):
                self.load(rows)
        rows = copy.deepcopy(self.rows)
        rows[1]["Stack"] = 2
        with self.assertRaisesRegex(ValueError, "same stack"):
            self.load(rows)
        rows = copy.deepcopy(self.rows)
        rows[2]["Stack"] = 3
        with self.assertRaisesRegex(ValueError, "next number"):
            self.load(rows)

    def test_duplicate_branches(self):
        rows = copy.deepcopy(self.rows)
        rows[2]["Source Branch"] = rows[0]["Source Branch"]
        with self.assertRaisesRegex(ValueError, "duplicate branch"):
            self.load(rows)

    def test_allowed_statuses_and_normalised_lists(self):
        for status in tracker.STATUSES:
            rows = [row(1, 1, "feature/a")]
            rows[0].update({"Status": status, "Type(s)": "Fix; Operations",
                            "Package(s)": " vendor/a ; vendor/b "})
            loaded = self.load(rows)
            self.assertEqual(loaded[0]["Package(s)"], "vendor/a; vendor/b")

    def test_validate_only_does_not_create_csv(self):
        self.load(self.rows)
        result = subprocess.run(
            [sys.executable, str(Path(tracker.__file__)), str(self.input), "--validate-only"],
            capture_output=True, text=True, check=True,
        )
        self.assertEqual(json.loads(result.stdout), self.rows)
        self.assertEqual(list(self.root.iterdir()), [self.input])

    def test_timestamp_validation(self):
        stamp = "2026-10-02T12-00-00+1000"
        self.assertEqual(tracker.filename_timestamp(stamp), stamp)
        self.assertRegex(tracker.filename_timestamp(None, "UTC"), r"\+0000$")
        with self.assertRaisesRegex(ValueError, "unknown timezone"):
            tracker.filename_timestamp(None, "Invalid/Timezone")
        with self.assertRaisesRegex(ValueError, "--timestamp"):
            tracker.filename_timestamp("../output")


if __name__ == "__main__":
    unittest.main()
