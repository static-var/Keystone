import json
import posixpath
import re
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUBMISSION = ROOT / "marketplace" / "openai" / "submission.json"


class OpenAIMarketplaceTests(unittest.TestCase):
    def test_publication_metadata_has_public_listing_urls(self) -> None:
        manifest = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text())

        self.assertEqual("https://keystone.staticvar.dev/", manifest["homepage"])
        self.assertEqual("https://github.com/static-var/Keystone", manifest["repository"])
        self.assertEqual("MIT", manifest["license"])
        self.assertEqual("static-var", manifest["author"]["name"])

        interface = manifest["interface"]
        self.assertEqual("Developer Tools", interface["category"])
        self.assertLessEqual(len(interface["shortDescription"]), 30)
        self.assertLessEqual(len(interface["defaultPrompt"]), 3)
        self.assertEqual("https://keystone.staticvar.dev/", interface["websiteURL"])
        self.assertEqual("https://keystone.staticvar.dev/support/", interface["supportURL"])
        self.assertEqual("https://keystone.staticvar.dev/privacy/", interface["privacyPolicyURL"])
        self.assertEqual("https://keystone.staticvar.dev/terms/", interface["termsOfServiceURL"])

    def test_submission_materials_match_portal_requirements(self) -> None:
        submission = json.loads(SUBMISSION.read_text())

        self.assertEqual("Skills only", submission["submissionType"])
        self.assertEqual("Developer Tools", submission["listing"]["category"])
        icons = submission["listing"]["icons"]
        self.assertEqual(
            "assets/brand/keystone-icon.png",
            icons["directory"]["lightMode"],
        )
        self.assertEqual(
            "assets/brand/keystone-icon-dark.png",
            icons["directory"]["darkMode"],
        )
        self.assertEqual(icons["directory"], icons["composer"])
        self.assertEqual(5, len(submission["tests"]["positive"]))
        self.assertEqual(3, len(submission["tests"]["negative"]))
        self.assertGreaterEqual(len(submission["starterPrompts"]), 3)
        for case in submission["tests"]["positive"]:
            self.assertTrue(case["prompt"])
            self.assertTrue(case["expectedBehavior"])
            self.assertTrue(case["expectedResultShape"])
            self.assertIn("fixtureData", case)
        for case in submission["tests"]["negative"]:
            self.assertTrue(case["scenario"])
            self.assertTrue(case["expectedFallback"])
            self.assertTrue(case["reason"])

    def test_openai_bundle_contains_only_the_public_plugin_surface(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            archive = Path(temporary) / "keystone-openai.zip"
            result = subprocess.run(
                ["sh", "scripts/package-openai-plugin.sh", str(archive)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            with zipfile.ZipFile(archive) as bundle:
                names = {name for name in bundle.namelist() if not name.endswith("/")}
                skill_sources = {
                    name: bundle.read(name).decode()
                    for name in names
                    if name.startswith("skills/") and name.endswith("/SKILL.md")
                }

        self.assertIn(".codex-plugin/plugin.json", names)
        self.assertIn("LICENSE", names)
        self.assertIn("assets/brand/keystone-icon.png", names)
        self.assertIn("assets/brand/keystone-icon-dark.png", names)
        self.assertIn("references/gates/checkpoint.md", names)
        self.assertIn("references/engineering-standards.md", names)
        self.assertFalse(any(name.startswith("skills/_shared/") for name in names))
        for skill in (
            "change-review",
            "context-survey",
            "implementation",
            "product-planning",
            "project-audit",
            "refactoring",
            "root-cause-analysis",
            "shipping",
            "task-creation",
        ):
            self.assertIn(f"skills/{skill}/SKILL.md", names)
            self.assertNotIn("../_shared/", skill_sources[f"skills/{skill}/SKILL.md"])
        self.assertFalse(any(name.startswith(".claude-plugin/") for name in names))
        self.assertFalse(any(name.startswith(".pi/") for name in names))
        self.assertFalse(any(name.startswith("scripts/") for name in names))
        for name, source in skill_sources.items():
            for pointer in re.findall(r"`([^`]+\.md)`", source):
                if pointer.startswith(("http://", "https://")) or "<" in pointer:
                    continue
                target = posixpath.normpath(posixpath.join(posixpath.dirname(name), pointer))
                with self.subTest(skill=name, pointer=pointer):
                    self.assertIn(target, names)

    def test_legal_and_support_pages_are_public_site_artifacts(self) -> None:
        expected = {
            "privacy": "Privacy Policy",
            "terms": "Terms of Use",
            "support": "Support",
        }
        for slug, heading in expected.items():
            with self.subTest(slug=slug):
                page = ROOT / "site" / slug / "index.html"
                text = page.read_text()
                self.assertIn(f"<h1>{heading}</h1>", text)
                self.assertIn('href="/"', text)

        privacy = (ROOT / "site" / "privacy" / "index.html").read_text()
        self.assertIn("Google Fonts", privacy)
        self.assertIn("https://policies.google.com/privacy", privacy)

        support = (ROOT / "site" / "support" / "index.html").read_text()
        self.assertIn("https://github.com/static-var/Keystone/security/advisories/new", support)


if __name__ == "__main__":
    unittest.main()
