import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate-package.py"
KEYSTONE_VALIDATOR = ROOT / "scripts" / "validate-keystone.py"


def load_validate_package():
    spec = importlib.util.spec_from_file_location("validate_package", VALIDATOR)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_validate_keystone():
    spec = importlib.util.spec_from_file_location("validate_keystone", KEYSTONE_VALIDATOR)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class PackageValidatorTests(unittest.TestCase):
    def test_orphaned_shared_reference_is_rejected(self):
        validator = load_validate_keystone()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            skill = root / "skills" / "example" / "SKILL.md"
            used = root / "skills" / "_shared" / "used.md"
            orphaned = root / "skills" / "_shared" / "orphaned.md"
            skill.parent.mkdir(parents=True)
            used.parent.mkdir(parents=True)
            skill.write_text("Load `../_shared/used.md`.\n")
            used.write_text("Used.\n")
            orphaned.write_text("Orphaned.\n")
            shared = ["skills/_shared/used.md", "skills/_shared/orphaned.md"]
            self.assertEqual(
                validator.orphaned_shared_references(root, shared),
                ["skills/_shared/orphaned.md"],
            )

    def test_all_shared_gates_are_required(self):
        validator = load_validate_package()
        for gate in ("checkpoint", "isolation", "proof", "red", "review", "ship"):
            with self.subTest(gate=gate):
                self.assertIn(f"skills/_shared/gates/{gate}.md", validator.REQUIRED)

    def test_all_public_skills_are_required(self):
        validator = load_validate_package()
        self.assertEqual(set(validator.PUBLIC_SKILLS), validator.EXPECTED_PUBLIC_SKILLS)
        for skill in validator.PUBLIC_SKILLS:
            with self.subTest(skill=skill):
                self.assertIn(f"skills/{skill}/SKILL.md", validator.REQUIRED)

    def test_agent_skills_are_not_packaged_as_a_duplicate_tree(self):
        validator = load_validate_package()
        self.assertFalse(any(path.startswith(".agents/skills/") for path in validator.expand_allowlist()))

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
