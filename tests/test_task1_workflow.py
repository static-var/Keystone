import json
import re
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TASK_CREATION = ROOT / "skills" / "task-creation" / "SKILL.md"
README = ROOT / "README.md"
HOW_IT_WORKS = ROOT / "HOW_IT_WORKS.md"
PI_EXTENSION = ROOT / ".pi" / "extensions" / "keystone.ts"
PACKAGE_JSON = ROOT / "package.json"
REQUIRED_SHARED_FILES = {
    "skills/_shared/gates/checkpoint.md",
    "skills/_shared/gates/isolation.md",
    "skills/_shared/gates/proof.md",
    "skills/_shared/gates/red.md",
    "skills/_shared/gates/review.md",
    "skills/_shared/gates/ship.md",
    "skills/_shared/engineering-standards.md",
    "skills/_shared/handoff-packet.md",
}


def strip_frontmatter(content: str) -> str:
    return re.sub(r"^---\r?\n[\s\S]*?\r?\n---\r?\n?", "", content).strip()


def build_payload_from_outside_repo(skill: str, args: str) -> str:
    script = textwrap.dedent(
        f"""
        import {{ buildCommandPayload }} from {json.dumps(PI_EXTENSION.as_uri())};
        const payload = buildCommandPayload({json.dumps(skill)}, {json.dumps(args)});
        if (payload === null) {{
          throw new Error("payload was null");
        }}
        console.log(JSON.stringify({{ payload }}));
        """
    )
    with tempfile.TemporaryDirectory() as outside_repo:
        result = subprocess.run(
            ["node", "--experimental-strip-types", "-e", script],
            cwd=outside_repo,
            text=True,
            capture_output=True,
            check=True,
        )
    return json.loads(result.stdout)["payload"]


def payload_path(payload: str, label: str) -> Path:
    match = re.search(rf"{re.escape(label)}: `([^`]+)`", payload)
    if not match:
        raise AssertionError(f"missing payload path for {label!r}: {payload[:500]}")
    return Path(match.group(1))


class TaskCreationWorkflowTests(unittest.TestCase):
    def test_risky_task_sets_require_verification_and_change_review(self) -> None:
        content = TASK_CREATION.read_text(encoding="utf-8")
        risky_rules = [line for line in content.splitlines() if "risky task sets" in line.lower()]

        self.assertEqual(1, len(risky_rules), risky_rules)
        rule = risky_rules[0].lower()
        self.assertIn("verification gates", rule)
        self.assertIn("change-review points", rule)
        self.assertNotIn("without verification gates", rule)
        self.assertRegex(rule, r"through|with|include|require")

    def test_task_artifact_threshold_is_explicit_and_overrideable(self) -> None:
        content = TASK_CREATION.read_text(encoding="utf-8")
        normalized = content.lower()

        self.assertIn("1–5 top-level vertical slices", normalized)
        self.assertIn("6 or more top-level vertical slices", normalized)
        self.assertIn("chat only", normalized)
        self.assertIn("write or save", normalized)
        self.assertIn("slice the work naturally before counting", normalized)
        self.assertIn("do not duplicate the full task creation", normalized)
        self.assertNotIn(
            "no file mutation unless the user explicitly requested a task-creation artifact",
            normalized,
        )

        for doc in (README, HOW_IT_WORKS):
            with self.subTest(doc=doc.name):
                documented = doc.read_text(encoding="utf-8").lower()
                self.assertIn("1–5 top-level slices", documented)
                self.assertIn("6 or more", documented)
                self.assertIn("chat", documented)
                self.assertIn("save", documented)
                self.assertIn("override", documented)

    def test_pi_command_payload_embeds_resolvable_packaged_skill_content(self) -> None:
        payload = build_payload_from_outside_repo("task-creation", "Plan a risky migration")
        canonical_body = strip_frontmatter(TASK_CREATION.read_text(encoding="utf-8"))

        self.assertIn(canonical_body, payload)
        self.assertIn("Plan a risky migration", payload)
        self.assertNotIn("Load and follow `skills/task-creation/SKILL.md` exactly", payload)
        self.assertNotIn("Resolve shared gates, handoff packet, and engineering standards relative to `skills/`", payload)

        package_root = payload_path(payload, "Canonical Keystone package root")
        skill_source = payload_path(payload, "Embedded skill source")
        shared_root = payload_path(payload, "Shared gates, handoff packet, and engineering standards live under")

        self.assertTrue(package_root.is_absolute(), package_root)
        self.assertTrue(skill_source.is_absolute(), skill_source)
        self.assertTrue(shared_root.is_absolute(), shared_root)
        self.assertEqual(ROOT.resolve(), package_root.resolve())
        self.assertEqual(TASK_CREATION.resolve(), skill_source.resolve())
        self.assertEqual((ROOT / "skills" / "_shared").resolve(), shared_root.resolve())
        self.assertTrue(skill_source.is_file(), skill_source)
        self.assertTrue(shared_root.is_dir(), shared_root)

        packaged_files = set(json.loads(PACKAGE_JSON.read_text(encoding="utf-8"))["files"])
        for shared_file in REQUIRED_SHARED_FILES:
            with self.subTest(shared_file=shared_file):
                self.assertIn(shared_file, packaged_files)
                self.assertTrue((ROOT / shared_file).is_file(), shared_file)


if __name__ == "__main__":
    unittest.main()
