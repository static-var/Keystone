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
REQUIRED_ROUTING_PAIRS = {
    "public-research": {
        "none-public-search": None,
        "survey-project-external-research": "context-survey",
    },
    "explicit-context-survey": {
        "none-external-summary": None,
        "survey-explicit-external-summary": "context-survey",
    },
    "automatic-repository-reconnaissance": {
        "none-external-summary": None,
        "survey-direct": "context-survey",
    },
    "configuration-scope": {
        "none-small-config-edit": None,
        "implementation-project-config": "implementation",
        "implementation-explicit-small-config": "implementation",
    },
    "project-config-workflow-worthiness": {
        "none-project-small-config": None,
        "implementation-project-config": "implementation",
    },
    "project-bound-implementation": {
        "implementation-direct": "implementation",
    },
    "script-scope": {
        "none-one-off-script": None,
        "implementation-project-ci-script": "implementation",
    },
    "project-script-workflow-worthiness": {
        "none-project-throwaway-script": None,
        "implementation-project-ci-script": "implementation",
    },
    "project-doc-workflow-worthiness": {
        "none-mechanical-doc-edit": None,
        "none-project-doc-typo": None,
    },
    "product-copy-scope": {
        "none-generic-copy": None,
        "planning-project-copy": "product-planning",
    },
    "debugging-scope": {
        "none-unrelated-error": None,
        "rca-project-debugging": "root-cause-analysis",
    },
    "cwd-independence": {
        "none-repo-cwd-public-search": None,
        "none-repo-cwd-one-off": None,
        "survey-outside-cwd-project-research": "context-survey",
    },
    "implementation-vs-refactoring": {
        "implementation-behavior-with-cleanup": "implementation",
        "refactor-behavior-preserving": "refactoring",
    },
    "shipping-authorization": {
        "shipping-commit-only": "shipping",
        "shipping-push-only": "shipping",
        "shipping-tag-publish": "shipping",
        "none-review-awaiting-authorization": None,
    },
    "shipping-handoff-authorization": {
        "shipping-handoff-authorized": "shipping",
        "none-shipping-handoff-awaiting": None,
    },
    "shipping-merge-authorization": {
        "shipping-merge-only": "shipping",
        "none-merge-awaiting-authorization": "change-review",
    },
    "shipping-deploy-authorization": {
        "shipping-deploy-only": "shipping",
        "none-deploy-readiness-status": "change-review",
    },
    "shipping-repository-handoff": {
        "shipping-identified-repository-handoff": "shipping",
        "none-ordinary-handoff": None,
    },
    "shipping-destructive-cleanup-authorization": {
        "shipping-authorized-destructive-cleanup": "shipping",
        "none-destructive-cleanup-awaiting": "context-survey",
    },
}
READ_ONLY_SHIPPING_NEGATIVES = {
    "none-merge-awaiting-authorization": "change-review",
    "none-deploy-readiness-status": "change-review",
    "none-destructive-cleanup-awaiting": "context-survey",
}
PROJECT_BOUND_NON_WORKFLOW_IDS = {
    "none-project-small-config",
    "none-project-doc-typo",
    "none-project-throwaway-script",
}
HANDOFF_FIXTURE_IDS = {
    "shipping-handoff-authorized",
    "none-shipping-handoff-awaiting",
}
HANDOFF_PACKET_FIELDS = (
    "source skill",
    "target skill",
    "goal",
    "evidence",
    "files",
    "risks",
    "next check",
    "overrides",
)
NO_SKILL_BOUNDARY_CATEGORIES = {
    "public-search": {"none-public-search"},
    "external-summary": {"none-external-summary"},
    "generic-planning": {"none-generic-brainstorming", "none-generic-copy"},
    "mechanical-edit": {"none-mechanical-doc-edit", "none-small-config-edit"},
    "one-off-script": {"none-one-off-script", "none-data-transform"},
    "unrelated-debugging": {"none-unrelated-error"},
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

        actual_by_id = {str(case["id"]): case["expected"] for case in cases}
        kind_by_id = {str(case["id"]): case["kind"] for case in cases}
        prompt_by_id = {str(case["id"]): str(case["prompt"]).lower() for case in cases}
        for pair, expectations in REQUIRED_ROUTING_PAIRS.items():
            with self.subTest(routing_pair=pair):
                self.assertTrue(expectations.keys() <= ids)
                self.assertTrue(
                    all(actual_by_id[case_id] == expected for case_id, expected in expectations.items())
                )
        for category, case_ids in NO_SKILL_BOUNDARY_CATEGORIES.items():
            with self.subTest(no_skill_category=category):
                self.assertTrue(case_ids <= ids)
                self.assertTrue(all(actual_by_id[case_id] is None for case_id in case_ids))
        for case_id in HANDOFF_FIXTURE_IDS:
            with self.subTest(handoff_fixture=case_id):
                self.assertIn(case_id, prompt_by_id)
                self.assertTrue(
                    all(f"{field}:" in prompt_by_id[case_id] for field in HANDOFF_PACKET_FIELDS)
                )
        for case_id, expected in READ_ONLY_SHIPPING_NEGATIVES.items():
            with self.subTest(read_only_shipping_negative=case_id):
                self.assertEqual(expected, actual_by_id[case_id])
                self.assertNotEqual("shipping", actual_by_id[case_id])
                self.assertEqual("boundary", kind_by_id[case_id])
        for case_id in PROJECT_BOUND_NON_WORKFLOW_IDS:
            with self.subTest(project_bound_non_workflow=case_id):
                self.assertIn(case_id, actual_by_id)
                self.assertIsNone(actual_by_id[case_id])
                self.assertEqual("no-skill", kind_by_id[case_id])
        self.assertIn("atlas repository", prompt_by_id["implementation-direct"])
        self.assertIn("saved-search feature", prompt_by_id["implementation-direct"])

        self.assertTrue(all(count >= 2 for count in positive_coverage.values()), positive_coverage)
        self.assertGreaterEqual(no_skill_count, 20)
        self.assertGreaterEqual(adversarial_count, 30)

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
