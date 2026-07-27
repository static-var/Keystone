import importlib.util
import json
import re
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "scripts" / "validate-keystone.py"
spec = importlib.util.spec_from_file_location("validate_keystone", VALIDATOR_PATH)
validate_keystone = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(validate_keystone)
PUBLIC_SKILLS = [
    "context-survey",
    "product-planning",
    "task-creation",
    "implementation",
    "refactoring",
    "root-cause-analysis",
    "change-review",
    "shipping",
    "project-audit",
]
RELEASE_VERSION = "2.0.3"


class ReleaseMetadataDocsTests(unittest.TestCase):
    def test_release_version_is_synchronized_to_2_0_2(self):
        package = json.loads((ROOT / "package.json").read_text())
        self.assertEqual(RELEASE_VERSION, package["version"])
        lockfile = json.loads((ROOT / "package-lock.json").read_text())
        self.assertEqual(RELEASE_VERSION, lockfile["version"])
        self.assertEqual(RELEASE_VERSION, lockfile["packages"][""]["version"])

        metadata_versions = {
            ".claude-plugin/plugin.json": lambda data: [data["version"]],
            ".claude-plugin/marketplace.json": lambda data: [data["version"], data["plugins"][0]["version"]],
            ".codex-plugin/plugin.json": lambda data: [data["version"]],
        }
        for rel, versions in metadata_versions.items():
            with self.subTest(rel=rel):
                data = json.loads((ROOT / rel).read_text())
                self.assertEqual([RELEASE_VERSION] * len(versions(data)), versions(data))

    def test_docs_describe_migration_to_nine_direct_skills(self):
        readme = (ROOT / "README.md").read_text()
        how = (ROOT / "HOW_IT_WORKS.md").read_text()
        combined = f"{readme}\n{how}"

        self.assertIn("Migrate from `/keystone` to direct skills", combined)
        self.assertIn("Use the matching public skill directly", combined)
        for skill in PUBLIC_SKILLS:
            with self.subTest(skill=skill):
                self.assertIn(f"/{skill}", combined)
        self.assertNotIn("standalone Agent Skills", combined)

    def test_shipping_explicit_only_sections_cover_canonical_actions(self):
        action_patterns = {
            "commit": r"\bcommits?\b",
            "push": r"\bpush(?:es)?\b",
            "PR": r"\bPRs?\b",
            "merge": r"\bmerge\b",
            "tag": r"\btag\b",
            "package": r"\bpackage\b",
            "publish": r"\bpublish\b",
            "release": r"\brelease\b",
            "deploy": r"\bdeploy\b",
            "repository handoff": r"\brepository handoff\b",
            "destructive cleanup": r"\bdestructive cleanup\b",
        }
        shipping = (ROOT / "skills" / "shipping" / "SKILL.md").read_text()
        readme = (ROOT / "README.md").read_text()
        how = (ROOT / "HOW_IT_WORKS.md").read_text()

        def section(text, heading):
            depth = len(heading.split(" ", 1)[0])
            return re.search(
                rf"^{re.escape(heading)}\n(?P<body>.*?)(?=^#{{1,{depth}}} |\Z)",
                text,
                re.MULTILINE | re.DOTALL,
            )

        def line(text, marker):
            return re.search(
                rf"^(?P<body>.*{re.escape(marker)}.*)$",
                text,
                re.MULTILINE,
            )

        sections = {
            "Shipping description": re.search(
                r"^description: (?P<body>.*)$",
                shipping,
                re.MULTILINE,
            ),
            "Shipping Load when": section(shipping, "## Load when"),
            "Shipping Hard rules": section(shipping, "## Hard rules"),
            "Shipping Explicit-only finalization": section(
                shipping, "## Explicit-only finalization"
            ),
            "README Shipping trigger": line(readme, "| `shipping` |"),
            "README /shipping trigger": line(readme, "/shipping explicitly"),
            "README Explicit-only shipping": section(
                readme, "## Explicit-only shipping"
            ),
            "HOW Shipping trigger": line(how, "| `shipping` |"),
            "HOW /shipping trigger": line(how, "| `/keystone ship"),
            "HOW Shipping boundary": section(how, "### Shipping"),
            "HOW maintainer Shipping reminder": line(
                how, "Use `shipping` only when"
            ),
        }

        for source, match in sections.items():
            with self.subTest(source=source, section="present"):
                self.assertIsNotNone(match)
            assert match is not None
            body = match.group("body")
            for action, pattern in action_patterns.items():
                with self.subTest(source=source, action=action):
                    self.assertIsNotNone(re.search(pattern, body, re.IGNORECASE))

    def test_shipping_process_executes_authorized_actions_safely(self):
        shipping = (ROOT / "skills" / "shipping" / "SKILL.md").read_text()
        process = re.search(
            r"^## Process\n(?P<body>.*?)(?=^## |\Z)",
            shipping,
            re.MULTILINE | re.DOTALL,
        )
        self.assertIsNotNone(process)
        assert process is not None

        contracts = {
            "perform authorized action set": (
                r"\bperform\b.*\bauthorized action set\b"
            ),
            "resolve exact targets": r"\bresolve\b.*\bexact targets?\b",
            "record results": r"\brecord\b.*\bresults?\b",
            "stop on failure": r"\bstop\b.*\bfail(?:s|ure|ed)?\b",
            "destructive cleanup recoverability": (
                r"\bdestructive cleanup\b.*\brecoverab"
            ),
            "destructive cleanup target confirmation": (
                r"\bdestructive cleanup\b.*\btarget confirmation\b"
            ),
        }
        for contract, pattern in contracts.items():
            with self.subTest(contract=contract):
                self.assertIsNotNone(
                    re.search(pattern, process.group("body"), re.IGNORECASE | re.DOTALL)
                )

    def test_shipping_handoff_authorization_is_canonical(self):
        handoff = (ROOT / "skills" / "_shared" / "handoff-packet.md").read_text()
        rules = re.search(
            r"^## Rules\n(?P<body>.*?)(?=^## |\Z)",
            handoff,
            re.MULTILINE | re.DOTALL,
        )
        self.assertIsNotNone(rules)
        assert rules is not None
        body = rules.group("body")

        contracts = {
            "shipping target condition": r"\btarget skill\b.*\bshipping\b",
            "evidence authorization field": (
                r"\bevidence\b.*\b(?:carries|contains)\b"
            ),
            "verbatim explicit delivery request": (
                r"\bverbatim\b.*\bexplicit delivery request\b"
            ),
            "exact authorized action set": r"\bexact authorized action set\b",
        }
        for contract, pattern in contracts.items():
            with self.subTest(contract=contract):
                self.assertIsNotNone(
                    re.search(pattern, body, re.IGNORECASE | re.DOTALL)
                )

    def test_shipping_packet_reports_action_execution_state(self):
        shipping = (ROOT / "skills" / "shipping" / "SKILL.md").read_text()

        def section(heading):
            return re.search(
                rf"^{re.escape(heading)}\n(?P<body>.*?)(?=^## |\Z)",
                shipping,
                re.MULTILINE | re.DOTALL,
            )

        sections = {
            "Outcome contract": section("## Outcome contract"),
            "Output format": section("## Output format"),
        }
        contracts = {
            "authorized action set": r"\bauthorized action set\b",
            "attempted action exact target result": (
                r"\battempted actions?\b.*\bexact targets?\b.*\b(?:result|status)\b"
            ),
            "partial completion": r"\bpartial completion\b",
            "remaining or unattempted actions": (
                r"\b(?:remaining|unattempted) actions?\b"
            ),
            "recovery": r"\brecovery\b",
            "next step": r"\bnext step\b",
        }
        for source, match in sections.items():
            with self.subTest(source=source, section="present"):
                self.assertIsNotNone(match)
            assert match is not None
            body = match.group("body")
            for contract, pattern in contracts.items():
                with self.subTest(source=source, contract=contract):
                    self.assertIsNotNone(
                        re.search(pattern, body, re.IGNORECASE | re.DOTALL)
                    )

    def test_context_survey_step_one_supports_pure_reconnaissance(self):
        survey = (ROOT / "skills" / "context-survey" / "SKILL.md").read_text()
        process = re.search(
            r"^## Process\n(?P<body>.*?)(?=^## |\Z)",
            survey,
            re.MULTILINE | re.DOTALL,
        )
        self.assertIsNotNone(process)
        assert process is not None
        step_one = re.search(r"^1\. (?P<body>.*)$", process.group("body"), re.MULTILINE)
        self.assertIsNotNone(step_one)
        assert step_one is not None
        body = step_one.group("body")

        contracts = {
            "requested understanding outcome": (
                r"\b(?:requested understanding outcome|repository reconnaissance)\b"
            ),
            "conditional downstream decision": (
                r"\b(?:downstream )?decision\b.*\b(?:when|if|where) applicable\b"
            ),
        }
        for contract, pattern in contracts.items():
            with self.subTest(contract=contract):
                self.assertIsNotNone(re.search(pattern, body, re.IGNORECASE))

    def test_validator_reports_release_metadata_version_mismatches(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "package.json").write_text(json.dumps({
                "name": "@static-var/keystone",
                "version": "1.9.9",
                "files": [],
                "pi": {"skills": ["./skills"]},
            }))
            (root / "packaging.allowlist").write_text("")
            (root / ".pi" / "extensions").mkdir(parents=True)
            (root / ".pi" / "extensions" / "keystone.ts").write_text(
                'readdirSync(skillsDir); skillDescription(skill); registerCommand(skill);'
            )
            (root / ".claude-plugin").mkdir()
            (root / ".claude-plugin" / "plugin.json").write_text(json.dumps({
                "name": "keystone",
                "version": "1.9.9",
            }))
            (root / ".claude-plugin" / "marketplace.json").write_text(json.dumps({
                "name": "keystone",
                "version": "2.0.3",
                "plugins": [{"name": "keystone", "version": "1.9.9"}],
            }))
            (root / ".codex-plugin").mkdir()
            (root / ".codex-plugin" / "plugin.json").write_text(json.dumps({
                "name": "keystone",
                "version": "1.9.9",
                "skills": "skills/",
            }))
            (root / ".agents" / "plugins").mkdir(parents=True)
            (root / ".agents" / "plugins" / "marketplace.json").write_text(json.dumps({
                "name": "keystone",
            }))

            errors = validate_keystone.metadata_errors(root)

        self.assertIn("package.json version must be 2.0.3", errors)
        self.assertIn(".claude-plugin/plugin.json version must be 2.0.3", errors)
        self.assertIn(".claude-plugin/marketplace.json plugins[0].version must be 2.0.3", errors)
        self.assertIn(".codex-plugin/plugin.json version must be 2.0.3", errors)
        self.assertIn('.codex-plugin/plugin.json skills must be "./skills/"', errors)


if __name__ == "__main__":
    unittest.main()
