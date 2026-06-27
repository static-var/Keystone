#!/usr/bin/env python3
"""Validate Keystone canonical source and packaging invariants."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "keystone"
SKILL = SKILL_DIR / "SKILL.md"
FORBIDDEN_TRACKED = {
    "docs",
    "plans",
    "index.html",
    "styles.css",
}


def fail(message: str) -> None:
    print(f"validate-keystone: {message}", file=sys.stderr)
    raise SystemExit(1)


def tracked_files() -> list[str]:
    try:
        result = subprocess.run(
            ["git", "ls-files"], cwd=ROOT, text=True, check=True, capture_output=True
        )
    except Exception:
        return []
    return [line for line in result.stdout.splitlines() if line]


def parse_frontmatter(text: str) -> dict[str, object]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    data: dict[str, object] = {}
    current_key = None
    for raw in text[4:end].splitlines():
        line = raw.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if line.startswith("  - ") and current_key:
            data.setdefault(current_key, []).append(line[4:].strip().strip('"\''))
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            current_key = key.strip()
            value = value.strip()
            data[current_key] = [] if value == "" else value.strip('"\'')
    return data


def check_skill() -> str:
    if not SKILL_DIR.is_dir():
        fail("missing canonical skill directory skills/keystone/")
    if not SKILL.is_file():
        fail("missing canonical skill file skills/keystone/SKILL.md")
    text = SKILL.read_text()
    metadata = parse_frontmatter(text)
    name = metadata.get("name")
    if name is None:
        heading = re.search(r"^#\s+(.+)$", text, re.M)
        name = heading.group(1).strip().lower() if heading else None
    if str(name).lower() != "keystone":
        fail("skill name must be keystone")
    return text


def check_language(text: str) -> None:
    public_plan = re.compile(r"(?<![\w/.-])/(?:plan)(?![\w/.-])|\bplanner\s+name\s+is\s+plan\b", re.I)
    if public_plan.search(text):
        fail("public /plan mention found; Keystone uses breakdown")
    if not re.search(r"\bbreakdown\b", text, re.I):
        fail("missing required breakdown terminology")


def check_references(text: str) -> None:
    refs = sorted(set(re.findall(r"\(([^)]+\.(?:md|json|yaml|yml|txt|sh|py))\)", text)))
    refs += sorted(set(re.findall(r"(?:^|\s)([A-Za-z0-9_./-]+\.(?:md|json|yaml|yml|txt|sh|py))", text)))
    missing = []
    for ref in refs:
        if ref.startswith(("http://", "https://", "mailto:")) or ref.startswith("/"):
            continue
        candidate = (SKILL_DIR / ref).resolve()
        try:
            candidate.relative_to(ROOT)
        except ValueError:
            continue
        if not candidate.exists():
            missing.append(ref)
    if missing:
        fail("missing referenced module/gate files: " + ", ".join(sorted(set(missing))))


def check_ignored_not_tracked() -> None:
    bad = []
    for path in tracked_files():
        first = path.split("/", 1)[0]
        if path in FORBIDDEN_TRACKED or first in FORBIDDEN_TRACKED:
            bad.append(path)
    if bad:
        fail("ignored artifacts are tracked: " + ", ".join(bad))


def check_package_json() -> None:
    package_path = ROOT / "package.json"
    if not package_path.is_file():
        fail("missing package.json")
    package = json.loads(package_path.read_text())
    for key in ("name", "version", "description", "license", "keywords"):
        if key not in package:
            fail(f"package.json missing {key}")
    if package.get("pi", {}).get("skills") != ["./skills"]:
        fail('package.json must set pi.skills to ["./skills"]')


def main() -> int:
    text = check_skill()
    check_language(text)
    check_references(text)
    check_ignored_not_tracked()
    check_package_json()
    print("validate-keystone: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
