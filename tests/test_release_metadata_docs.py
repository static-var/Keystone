import importlib.util
import json
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
RELEASE_VERSION = "2.0.0"


class ReleaseMetadataDocsTests(unittest.TestCase):
    def test_release_version_is_synchronized_to_2_0_0(self):
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
                "version": "2.0.0",
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

        self.assertIn("package.json version must be 2.0.0", errors)
        self.assertIn(".claude-plugin/plugin.json version must be 2.0.0", errors)
        self.assertIn(".claude-plugin/marketplace.json plugins[0].version must be 2.0.0", errors)
        self.assertIn(".codex-plugin/plugin.json version must be 2.0.0", errors)
        self.assertIn('.codex-plugin/plugin.json skills must be "./skills/"', errors)


if __name__ == "__main__":
    unittest.main()
