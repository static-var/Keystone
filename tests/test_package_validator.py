import importlib.util
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
    def test_all_shipped_gates_are_required(self):
        validator = load_validate_package()
        for gate in ("isolation", "proof", "red", "review", "ship"):
            with self.subTest(gate=gate):
                self.assertIn(f"skills/keystone/modules/gates/{gate}.md", validator.REQUIRED)

    def test_license_file_is_required(self):
        validator = load_validate_package()
        self.assertIn("LICENSE", validator.REQUIRED)

    def test_brand_assets_are_required(self):
        validator = load_validate_package()
        for asset in (
            "assets/brand/keystone-icon.png",
            "assets/brand/keystone-icon.svg",
            "assets/brand/keystone-logo.png",
            "assets/brand/keystone-logo.svg",
            "assets/readme/keystone-routing-kami.png",
        ):
            with self.subTest(asset=asset):
                self.assertIn(asset, validator.REQUIRED)


if __name__ == "__main__":
    unittest.main()
