import importlib.util
import re
import shutil
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate-package.py"


def load_validate_package():
    spec = importlib.util.spec_from_file_location("validate_package", VALIDATOR)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class PackageValidatorTests(unittest.TestCase):
    def test_all_shared_gates_are_required(self):
        validator = load_validate_package()
        for gate in ("checkpoint", "isolation", "proof", "red", "review", "ship"):
            with self.subTest(gate=gate):
                self.assertIn(f"skills/_shared/gates/{gate}.md", validator.REQUIRED)

    def test_all_public_skills_are_required(self):
        validator = load_validate_package()
        for skill in validator.PUBLIC_SKILLS:
            with self.subTest(skill=skill):
                self.assertIn(f"skills/{skill}/SKILL.md", validator.REQUIRED)
                self.assertIn(f".agents/skills/{skill}/SKILL.md", validator.REQUIRED)

    def test_agent_skills_ship_as_self_contained_directories(self):
        validator = load_validate_package()
        expanded = validator.expand_allowlist()
        for skill in validator.PUBLIC_SKILLS:
            with self.subTest(skill=skill):
                self.assertIn(f".agents/skills/{skill}/SKILL.md", expanded)
                self.assertIn(f".agents/skills/{skill}/_shared/gates/checkpoint.md", expanded)

    def test_each_agent_skill_resolves_local_markdown_pointers_when_copied_alone(self):
        markdown_link = re.compile(r"\]\((?!https?://|/)([^)#]+\.md)(?:#[^)]*)?\)")
        code_pointer = re.compile(r"`([^`]+\.md)`")
        validator = load_validate_package()
        with tempfile.TemporaryDirectory() as temporary:
            consumer = Path(temporary)
            for skill in validator.PUBLIC_SKILLS:
                source = ROOT / ".agents" / "skills" / skill
                target = consumer / source.name
                shutil.copytree(source, target)
                for markdown in target.rglob("*.md"):
                    text = markdown.read_text()
                    pointers = markdown_link.findall(text) + [
                        path for path in code_pointer.findall(text) if "<" not in path
                    ]
                    for relative in pointers:
                        with self.subTest(skill=source.name, file=markdown.name, pointer=relative):
                            self.assertTrue(
                                (markdown.parent / relative).resolve().is_file(),
                                f"{markdown.relative_to(target)} -> {relative}",
                            )

    def test_license_file_is_required(self):
        validator = load_validate_package()
        self.assertIn("LICENSE", validator.REQUIRED)

    def test_brand_assets_are_allowlisted(self):
        validator = load_validate_package()
        expanded = validator.expand_allowlist()
        for asset in (
            "assets/brand/keystone-icon.png",
            "assets/brand/keystone-icon.svg",
            "assets/brand/keystone-logo.png",
        ):
            with self.subTest(asset=asset):
                self.assertIn(asset, expanded)


if __name__ == "__main__":
    unittest.main()
