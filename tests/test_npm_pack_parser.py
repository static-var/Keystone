import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PARSER = ROOT / "scripts" / "npm-pack-filename.mjs"


class NpmPackFilenameParserTests(unittest.TestCase):
    def parse_pack_output(self, payload):
        return subprocess.run(
            ["node", str(PARSER)],
            input=json.dumps(payload),
            text=True,
            capture_output=True,
        )

    def test_reads_filename_from_legacy_array_shape(self):
        result = self.parse_pack_output([
            {"filename": "static-var-keystone-2.0.0.tgz"}
        ])

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "static-var-keystone-2.0.0.tgz\n")

    def test_reads_filename_from_npm_12_object_shape(self):
        result = self.parse_pack_output({
            "@static-var/keystone": {"filename": "static-var-keystone-2.0.0.tgz"}
        })

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "static-var-keystone-2.0.0.tgz\n")

    def test_rejects_empty_pack_output(self):
        for payload in ([], {}):
            with self.subTest(payload=payload):
                result = self.parse_pack_output(payload)

                self.assertNotEqual(result.returncode, 0)
                self.assertIn("npm pack output did not include a package entry", result.stderr)
                self.assertEqual(result.stdout, "")

    def test_rejects_malformed_filename(self):
        for filename in ("", "../keystone.tgz", "nested/keystone.tgz", "keystone.zip"):
            with self.subTest(filename=filename):
                result = self.parse_pack_output([{"filename": filename}])

                self.assertNotEqual(result.returncode, 0)
                self.assertIn("npm pack filename must be a local .tgz filename", result.stderr)
                self.assertEqual(result.stdout, "")

    def test_rejects_invalid_json(self):
        result = subprocess.run(
            ["node", str(PARSER)],
            input="not json",
            text=True,
            capture_output=True,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unable to parse npm pack JSON", result.stderr)
        self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
