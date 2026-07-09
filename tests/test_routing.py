"""Validate the invocation evaluation corpus and full-catalog export."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASES_PATH = ROOT / "tests" / "routing" / "cases.yaml"
PUBLIC_SKILLS = {
    "context-survey",
    "product-planning",
    "task-creation",
    "implementation",
    "refactoring",
    "root-cause-analysis",
    "change-review",
    "shipping",
    "project-audit",
}


def load_cases() -> list[dict[str, object]]:
    data = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise AssertionError(f"{CASES_PATH} must contain a list")
    return data


def load_exporter():
    path = ROOT / "scripts" / "export-invocation-eval.py"
    spec = importlib.util.spec_from_file_location("export_invocation_eval", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class InvocationFixturesTest(unittest.TestCase):
    def test_exact_public_catalog(self) -> None:
        actual = {
            path.parent.name
            for path in (ROOT / "skills").glob("*/SKILL.md")
            if not path.parent.name.startswith("_") and path.parent.name != "keystone"
        }
        self.assertEqual(PUBLIC_SKILLS, actual)

    def test_cases_are_well_formed_and_cover_boundaries(self) -> None:
        cases = load_cases()
        ids: set[str] = set()
        positive_coverage: dict[str, int] = {skill: 0 for skill in PUBLIC_SKILLS}
        no_skill_count = 0
        adversarial_count = 0

        for index, case in enumerate(cases):
            self.assertIsInstance(case, dict, f"case #{index} must be an object")
            self.assertEqual({"id", "prompt", "expected", "kind"}, set(case), f"case #{index} fields drifted")
            self.assertIsInstance(case["id"], str)
            self.assertIsInstance(case["prompt"], str)
            self.assertTrue(case["id"] and case["prompt"])
            self.assertNotIn(case["id"], ids, f"duplicate case id: {case['id']}")
            ids.add(str(case["id"]))
            self.assertIn(case["kind"], {"direct", "boundary", "no-skill"})

            expected = case["expected"]
            if expected is None:
                self.assertEqual("no-skill", case["kind"])
                no_skill_count += 1
            else:
                self.assertIn(expected, PUBLIC_SKILLS)
                positive_coverage[str(expected)] += 1
            adversarial_count += case["kind"] == "boundary"

        self.assertTrue(all(count >= 2 for count in positive_coverage.values()), positive_coverage)
        self.assertGreaterEqual(no_skill_count, 3)
        self.assertGreaterEqual(adversarial_count, 9)

    def test_export_compares_every_case_against_full_catalog(self) -> None:
        exporter = load_exporter()
        records = exporter.build_records(ROOT)
        self.assertEqual(len(load_cases()), len(records))
        for record in records:
            self.assertEqual(PUBLIC_SKILLS, set(record["candidates"]))
            self.assertEqual(PUBLIC_SKILLS, set(record["descriptions"]))
            self.assertEqual("single-label-or-none", record["decision"])

    def test_no_legacy_router_expectations(self) -> None:
        raw = CASES_PATH.read_text(encoding="utf-8").lower()
        self.assertNotIn('"expected": "router"', raw)
        self.assertNotIn('"expected": "plan"', raw)


if __name__ == "__main__":
    unittest.main()
