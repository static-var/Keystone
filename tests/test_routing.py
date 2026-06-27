"""Lightweight validation for Keystone routing evaluation fixtures."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASES_PATH = ROOT / "tests" / "routing" / "cases.yaml"
SKILL_PATH = ROOT / "skills" / "keystone" / "SKILL.md"

PUBLIC_SKILL = "keystone"
INTERNAL_MODULES = {
    "router",
    "read",
    "research",
    "write",
    "ui",
    "design",
    "breakdown",
    "build",
    "debug",
    "review",
    "ship",
    "health",
    "skill-engineering",
}

REQUIRED_COVERAGE = {
    "router",
    "read",
    "research",
    "write",
    "ui",
    "design",
    "breakdown",
    "build",
    "debug",
    "review",
    "ship",
    "health",
    "skill-engineering",
}

STOPWORDS = {
    "a", "an", "and", "are", "as", "before", "by", "for", "from", "if", "in",
    "into", "is", "it", "of", "on", "or", "the", "this", "to", "when", "with",
    "work", "works", "user", "request", "module", "primary", "keystone", "design", "internal", "approved", "changing",
}


class RoutingFixtureError(AssertionError):
    """Raised when routing fixtures are missing or malformed."""


def load_cases() -> list[dict[str, object]]:
    if not CASES_PATH.exists():
        raise RoutingFixtureError(f"required routing fixture is missing: {CASES_PATH}")
    try:
        data = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RoutingFixtureError(
            f"{CASES_PATH} must use the JSON-compatible YAML subset: {exc}"
        ) from exc
    if not isinstance(data, list):
        raise RoutingFixtureError(f"{CASES_PATH} must contain a list of case objects")
    return data


def assert_case_shape(testcase: unittest.TestCase, case: dict[str, object], index: int) -> None:
    testcase.assertIsInstance(case, dict, f"case #{index} must be an object")
    for field in ("id", "prompt", "expected"):
        testcase.assertIn(field, case, f"case #{index} missing {field!r}")
        testcase.assertIsInstance(case[field], str, f"case #{index} {field!r} must be a string")
        testcase.assertTrue(case[field], f"case #{index} {field!r} cannot be empty")

    expected = case["expected"]
    testcase.assertIn(
        expected,
        INTERNAL_MODULES,
        f"case {case['id']!r} routes to unknown module {expected!r}",
    )
    testcase.assertNotEqual(expected, "plan", "internal planner module must be 'breakdown', not 'plan'")

    if "negative" in case:
        testcase.assertIsInstance(case["negative"], list, f"case {case['id']!r} negative must be a list")
        for denied in case["negative"]:
            testcase.assertIsInstance(denied, str, f"case {case['id']!r} negative entries must be strings")
            testcase.assertNotEqual(
                expected,
                denied,
                f"case {case['id']!r} cannot both expect and reject {expected!r}",
            )


def token_present(text: str, token: str) -> bool:
    return re.search(rf"(?<![A-Za-z0-9_-]){re.escape(token)}(?![A-Za-z0-9_-])", text) is not None


def tokens(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z][a-z0-9-]+", text.lower())
        if len(token) > 2 and token not in STOPWORDS
    }


def skill_routing_rows() -> list[tuple[str, str]]:
    if not SKILL_PATH.exists():
        return []
    rows: list[tuple[str, str]] = []
    for line in SKILL_PATH.read_text(encoding="utf-8").splitlines():
        match = re.match(r"\|\s*(.*?)\s*\|\s*`modules/([a-z-]+)\.md`\s*\|", line)
        if match:
            intent, module = match.groups()
            rows.append((module, intent))
    return rows


def route_prompt_from_skill(prompt: str) -> str | None:
    prompt_tokens = tokens(prompt)
    for module, intent in skill_routing_rows():
        if prompt_tokens & tokens(intent):
            return module
    return None


def skill_routing_modules() -> set[str]:
    return {module for module, _intent in skill_routing_rows()}


class RoutingFixturesTest(unittest.TestCase):
    def test_cases_are_valid_and_cover_all_keystone_modules(self) -> None:
        cases = load_cases()
        self.assertGreaterEqual(len(cases), len(REQUIRED_COVERAGE))
        expected_modules = set()
        negative_count = 0
        for index, case in enumerate(cases):
            assert_case_shape(self, case, index)
            expected_modules.add(case["expected"])
            negative_count += bool(case.get("negative"))

        self.assertEqual(REQUIRED_COVERAGE, expected_modules)
        self.assertGreaterEqual(negative_count, 4, "include explicit negative routing cases")

    def test_public_skill_and_breakdown_naming_cases_exist(self) -> None:
        cases = load_cases()
        prompts = "\n".join(str(case["prompt"]).lower() for case in cases)
        self.assertIn("/plan", prompts)
        self.assertTrue(
            any(case["expected"] == "breakdown" and "plan" in str(case.get("negative", [])).lower() for case in cases),
            "include a case showing /plan is not public and breakdown is expected",
        )
        self.assertNotIn('"expected": "plan"', CASES_PATH.read_text(encoding="utf-8"))

    def test_fixture_prompts_route_with_skill_routing_table(self) -> None:
        if not SKILL_PATH.exists():
            self.skipTest(f"optional Keystone skill source not present: {SKILL_PATH}")
        for case in load_cases():
            self.assertEqual(
                case["expected"],
                route_prompt_from_skill(str(case["prompt"])),
                f"routing table mismatch for {case['id']!r}",
            )

    def test_skill_routing_table_backs_expected_modules(self) -> None:
        if not SKILL_PATH.exists():
            self.skipTest(f"optional Keystone skill source not present: {SKILL_PATH}")
        self.assertEqual(REQUIRED_COVERAGE, skill_routing_modules())

    def test_skill_content_mentions_expected_modules_when_present(self) -> None:
        if not SKILL_PATH.exists():
            self.skipTest(f"optional Keystone skill source not present: {SKILL_PATH}")
        skill_text = SKILL_PATH.read_text(encoding="utf-8")
        self.assertTrue(token_present(skill_text, PUBLIC_SKILL), "public skill name 'keystone' missing")
        missing = sorted(module for module in INTERNAL_MODULES if not token_present(skill_text, module))
        self.assertFalse(missing, f"Keystone skill source missing module names: {missing}")


if __name__ == "__main__":
    unittest.main()
