import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RELEASE_WORKFLOW = ROOT / ".github" / "workflows" / "release.yml"


def workflow_step_block(text, step_name):
    match = re.search(
        rf"^      - name: {re.escape(step_name)}\n(?P<body>.*?)(?=^      - name: |\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    if match is None:
        raise AssertionError(f"release workflow is missing step: {step_name}")
    return match.group("body")


class ReleaseWorkflowTests(unittest.TestCase):
    def test_trusted_publishing_uses_exact_stable_npm_pin(self):
        workflow = RELEASE_WORKFLOW.read_text()

        global_npm_installs = re.findall(r"npm install -g (npm@[^\s]+)", workflow)
        self.assertEqual(["npm@11.6.2"], global_npm_installs)
        self.assertRegex(
            workflow,
            r"(?m)^      - name: .+\n        run: npm install -g npm@11\.6\.2$",
        )
        self.assertNotIn("npm@latest", workflow)

    def test_pack_step_uses_json_parser_compatible_with_npm_12_output(self):
        workflow = RELEASE_WORKFLOW.read_text()
        pack_block = workflow_step_block(workflow, "Create npm tarball")

        self.assertIn("npm pack --json > npm-pack.json", pack_block)
        self.assertIn("node scripts/npm-pack-filename.mjs npm-pack.json", pack_block)
        self.assertNotIn("jq", pack_block)
        self.assertNotRegex(pack_block, r"\[0\]\.filename")


if __name__ == "__main__":
    unittest.main()
