#!/usr/bin/env python3
"""Exercise accepted-stack and parallel-candidate manifest boundaries."""

import copy
import importlib.util
import pathlib
import unittest


MODULE_PATH = pathlib.Path(__file__).with_name("validate_release_manifest.py")
SPEC = importlib.util.spec_from_file_location("manifest_validator", MODULE_PATH)
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


def work(slug, spec):
    return {
        "slice_slug": slug, "spec_slug": spec,
        "plan": f"plans/slices/to_do/{slug}/{slug}.md",
        "source": f"feature/{slug}", "status": "queued",
        "worker_ref": None, "worktree": None,
        "authoring_base": None, "prepared_sha": None, "waiting_on": [],
    }


def manifest():
    base = {"branch": "master", "sha": "a" * 40}
    return {
        "schema_version": 1, "release_id": "test-build", "state": "building",
        "base": base, "branches": [], "exclusions": [], "accepted_gaps": [],
        "integration": None,
        "freeze": {"frozen_at": None, "authorized_by": None, "scope_digest": None},
        "schedule": {
            "selection": "queue", "layout": "linear",
            "coordinator": {"session_id": None, "worker_ref": "/root", "workspace": "/tmp/build"},
            "spec_order": ["spec_a", "spec_b"], "current_spec": "spec_a",
            "ordering_reason": "Prerequisites then simple specs",
            "tail": copy.deepcopy(base),
            "work": [work("a1", "spec_a"), work("a2", "spec_a"), work("b1", "spec_b")],
        },
    }


def accept(data, index, sha):
    item = data["schedule"]["work"][index]
    item["status"] = "stacked"
    parent = copy.deepcopy(data["schedule"]["tail"])
    branch = {
        **{field: item[field] for field in ("source", "plan", "spec_slug", "slice_slug")},
        "target": parent["branch"], "parent": parent,
        "stacking_reason": "Linear build placement", "dependency_reason": "none",
        "code_prerequisites": [], "tip_sha": sha, "tree_sha": "d" * 40,
        "surfaces": ["test"], "checks": [],
        "reviews": [
            {"reviewer": reviewer, "status": "pending", "sha": None,
             "method": None, "origin_sha": None, "evidence": None}
            for reviewer in ("claude", "codex", "cursor")
        ],
        "change_request": {"url": None, "state": "none"},
    }
    data["branches"].append(branch)
    data["schedule"]["tail"] = {"branch": item["source"], "sha": sha}
    return branch


class BuildScheduleTests(unittest.TestCase):
    def test_initial_selection_requires_no_placeholder_commits(self):
        data = manifest()
        self.assertEqual(validator.validate(data), [])
        data["schedule"]["selection"] = "explicit"
        self.assertEqual(validator.validate(data), [])

    def test_later_spec_can_prepare_without_becoming_the_tail(self):
        data = manifest()
        later = data["schedule"]["work"][2]
        later.update(status="prepared", authoring_base=data["base"], prepared_sha="b" * 40)
        self.assertEqual(validator.validate(data), [])
        data["schedule"]["tail"] = {"branch": later["source"], "sha": later["prepared_sha"]}
        self.assertTrue(any("schedule.tail" in error for error in validator.validate(data)))

    def test_prepared_candidate_cannot_masquerade_as_accepted(self):
        data = manifest()
        accept(data, 0, "b" * 40)
        item = data["schedule"]["work"][0]
        item.update(status="prepared", authoring_base=data["base"], prepared_sha="b" * 40)
        self.assertTrue(any("cannot accept" in error for error in validator.validate(data)))

    def test_independent_slices_can_form_an_explicit_linear_stack(self):
        data = manifest()
        accept(data, 0, "b" * 40)
        accept(data, 1, "c" * 40)
        self.assertEqual(validator.validate(data), [])
        data["branches"][1]["parent"] = data["base"]
        data["branches"][1]["target"] = "master"
        self.assertTrue(any("linear parent" in error for error in validator.validate(data)))

    def test_later_spec_cannot_skip_unaccepted_slices(self):
        data = manifest()
        accept(data, 0, "b" * 40)
        accept(data, 2, "c" * 40)
        self.assertTrue(any("work prefix" in error for error in validator.validate(data)))

    def test_work_order_cannot_interleave_spec_blocks(self):
        data = manifest()
        data["schedule"]["work"] = [
            data["schedule"]["work"][0], data["schedule"]["work"][2], data["schedule"]["work"][1],
        ]
        self.assertTrue(any("spec block" in error for error in validator.validate(data)))

    def test_duplicate_assignments_and_unexplained_blockers_are_rejected(self):
        data = manifest()
        data["schedule"]["work"].append(copy.deepcopy(data["schedule"]["work"][2]))
        data["schedule"]["work"][0]["status"] = "blocked"
        errors = validator.validate(data)
        self.assertTrue(any("duplicates" in error for error in errors))
        self.assertTrue(any("waiting reason" in error for error in errors))

    def test_unfinished_queue_cannot_be_frozen_as_a_prefix_release(self):
        data = manifest()
        accept(data, 0, "b" * 40)
        data["state"] = "frozen"
        self.assertTrue(any("unfinished scheduled work" in error for error in validator.validate(data)))

    def test_explicit_dependency_layout_preserves_independent_roots(self):
        data = manifest()
        data["schedule"]["layout"] = "dependency"
        accept(data, 0, "b" * 40)
        second = accept(data, 2, "c" * 40)
        second["parent"] = copy.deepcopy(data["base"])
        second["target"] = "master"
        self.assertEqual(validator.validate(data), [])

    def test_legacy_contract_and_digest_remain_unchanged(self):
        data = manifest()
        accept(data, 0, "b" * 40)
        del data["schedule"]
        for field in ("slice_slug", "spec_slug", "stacking_reason", "code_prerequisites"):
            del data["branches"][0][field]
        self.assertEqual(validator.validate(data), [])
        expected = {
            "base": data["base"], "exclusions": [],
            "branches": [{key: data["branches"][0][key] for key in (
                "source", "plan", "target", "parent", "dependency_reason", "tip_sha", "tree_sha", "surfaces", "checks"
            )}],
        }
        self.assertEqual(validator.scope_payload(data), expected)
        data["branches"] = []
        self.assertTrue(validator.validate(data))

    def test_runtime_schedule_does_not_change_the_candidate_digest(self):
        data = manifest()
        accept(data, 0, "b" * 40)
        original = validator.scope_digest(data)
        data["schedule"]["current_spec"] = None
        data["schedule"]["work"][2]["worker_ref"] = "/root/later"
        self.assertEqual(validator.scope_digest(data), original)
        data["branches"][0]["code_prerequisites"] = ["landed_prerequisite"]
        self.assertNotEqual(validator.scope_digest(data), original)


if __name__ == "__main__":
    unittest.main()
