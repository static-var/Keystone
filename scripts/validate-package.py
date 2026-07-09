#!/usr/bin/env python3
"""Validate the Keystone release archive contents."""
from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWLIST = ROOT / "packaging.allowlist"
PUBLIC_SKILLS = sorted(
    path.parent.name
    for path in (ROOT / "skills").glob("*/SKILL.md")
    if not path.parent.name.startswith("_") and path.parent.name != "keystone"
)
EXPECTED_PUBLIC_SKILLS = {
    "change-review", "context-survey", "implementation", "product-planning",
    "project-audit", "refactoring", "root-cause-analysis", "shipping", "task-creation",
}
REQUIRED = {
    "README.md", "HOW_IT_WORKS.md", "LICENSE", "package.json", "packaging.allowlist", "Makefile",
    "scripts/build-metadata.py", "scripts/export-invocation-eval.py", "scripts/validate-keystone.py", "scripts/validate-package.py", "scripts/package-keystone.sh",
    ".pi/extensions/keystone.ts", ".claude-plugin/plugin.json", ".claude-plugin/marketplace.json", ".codex-plugin/plugin.json", ".agents/plugins/marketplace.json",
    "skills/_shared/gates/checkpoint.md", "skills/_shared/gates/isolation.md", "skills/_shared/gates/proof.md", "skills/_shared/gates/red.md", "skills/_shared/gates/review.md", "skills/_shared/gates/ship.md",
    "skills/_shared/engineering-standards.md", "skills/_shared/handoff-packet.md",
} | {f"skills/{s}/SKILL.md" for s in PUBLIC_SKILLS} | {
    f".agents/skills/{s}/SKILL.md" for s in PUBLIC_SKILLS
} | {
    ".agents/skills/_shared/engineering-standards.md",
    ".agents/skills/_shared/handoff-packet.md",
    ".agents/skills/_shared/gates/checkpoint.md",
    ".agents/skills/_shared/gates/isolation.md",
    ".agents/skills/_shared/gates/proof.md",
    ".agents/skills/_shared/gates/red.md",
    ".agents/skills/_shared/gates/review.md",
    ".agents/skills/_shared/gates/ship.md",
}
FORBIDDEN_PREFIXES = ("docs/", "plans/", "maintainers/", "dist/", ".git/", "skills/keystone/", ".agents/skills/keystone/")
FORBIDDEN_NAMES = {"index.html", "styles.css", ".DS_Store"}


def fail(message: str) -> None:
    print(f"validate-package: {message}", file=sys.stderr)
    raise SystemExit(1)


def forbidden(path: str) -> bool:
    private_agent_shared = re.match(r"^\.agents/skills/[^/]+/_shared/", path)
    return bool(private_agent_shared) or path.rsplit("/", 1)[-1] in FORBIDDEN_NAMES or path.startswith(FORBIDDEN_PREFIXES) or path.endswith((".pyc", ".plan.md", "-plan.md", ".design.md", "-design.md"))


def expand_allowlist() -> set[str]:
    if not ALLOWLIST.is_file():
        fail("missing packaging.allowlist")
    expanded: set[str] = set()
    for raw in ALLOWLIST.read_text().splitlines():
        path = raw.strip()
        if not path or path.startswith("#"):
            continue
        if forbidden(path):
            fail(f"forbidden allowlist entry: {path}")
        candidate = ROOT / path
        if not candidate.exists():
            fail(f"allowlisted path missing: {path}")
        if candidate.is_dir():
            expanded.update(child.relative_to(ROOT).as_posix() for child in candidate.rglob("*") if child.is_file() and not forbidden(child.relative_to(ROOT).as_posix()))
        else:
            expanded.add(path)
    return expanded


def main(argv: list[str]) -> int:
    if set(PUBLIC_SKILLS) != EXPECTED_PUBLIC_SKILLS:
        fail(f"public skills must be exactly {sorted(EXPECTED_PUBLIC_SKILLS)}")
    archive = Path(argv[1]) if len(argv) > 1 else Path("dist/keystone.zip")
    if not archive.is_file():
        fail(f"archive not found: {archive}")
    with zipfile.ZipFile(archive) as zf:
        names = {name for name in zf.namelist() if not name.endswith("/")}
    missing = sorted(REQUIRED - names)
    if missing:
        fail("missing required files: " + ", ".join(missing))
    bad = sorted(name for name in names if forbidden(name))
    if bad:
        fail("forbidden files present: " + ", ".join(bad))
    expected = expand_allowlist()
    extra = sorted(names - expected)
    absent = sorted(expected - names)
    if extra:
        fail("archive contains files outside expanded allowlist: " + ", ".join(extra))
    if absent:
        fail("expanded allowlist files missing from archive: " + ", ".join(absent))
    print("validate-package: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
