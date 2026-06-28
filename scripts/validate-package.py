#!/usr/bin/env python3
"""Validate the Keystone release archive contents."""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWLIST = ROOT / "packaging.allowlist"

REQUIRED = {
    "README.md",
    "HOW_IT_WORKS.md",
    "package.json",
    "packaging.allowlist",
    "Makefile",
    "scripts/build-metadata.py",
    "scripts/validate-keystone.py",
    "scripts/validate-package.py",
    "scripts/package-keystone.sh",
    ".pi/extensions/keystone.ts",
    "skills/keystone/SKILL.md",
    "skills/keystone/modules/router.md",
    "skills/keystone/modules/research.md",
    "skills/keystone/modules/shape.md",
    "skills/keystone/modules/breakdown.md",
    "skills/keystone/modules/build.md",
    "skills/keystone/modules/debug.md",
    "skills/keystone/modules/review.md",
    "skills/keystone/modules/ship.md",
    "skills/keystone/modules/health.md",
    "skills/keystone/modules/gates/isolation.md",
    "skills/keystone/modules/gates/proof.md",
    "skills/keystone/modules/gates/red.md",
    "skills/keystone/modules/gates/review.md",
    "skills/keystone/modules/gates/ship.md",
    ".claude-plugin/plugin.json",
    ".claude-plugin/marketplace.json",
    ".codex-plugin/plugin.json",
    ".agents/plugins/marketplace.json",
    ".agents/skills/keystone/SKILL.md",
}
FORBIDDEN_NAMES = {
    "index.html",
    "styles.css",
    "skill-engineering.md",
    ".DS_Store",
}
FORBIDDEN_PREFIXES = (
    "docs/",
    "plans/",
    "maintainers/",
    "dist/",
    ".git/",
    ".keystone/plans/",
    ".keystone/specs/",
    ".keystone/tmp/",
    "__pycache__/",
)
FORBIDDEN_SUFFIXES = (
    ".pyc",
    ".plan.md",
    "-plan.md",
    ".design.md",
    "-design.md",
)


def fail(message: str) -> None:
    print(f"validate-package: {message}", file=sys.stderr)
    raise SystemExit(1)


def forbidden(path: str) -> bool:
    base = path.rsplit("/", 1)[-1]
    return (
        base in FORBIDDEN_NAMES
        or path.startswith(FORBIDDEN_PREFIXES)
        or path.endswith(FORBIDDEN_SUFFIXES)
    )


def expand_allowlist() -> set[str] | None:
    if not ALLOWLIST.is_file():
        return None
    expanded: set[str] = set()
    for raw in ALLOWLIST.read_text().splitlines():
        path = raw.strip()
        if not path or path.startswith("#"):
            continue
        if forbidden(path) or path in {"dist", "docs", "plans", "maintainers", ".git"}:
            fail(f"forbidden allowlist entry: {path}")
        candidate = ROOT / path
        if not candidate.exists():
            fail(f"allowlisted path missing: {path}")
        if candidate.is_dir():
            for child in candidate.rglob("*"):
                if child.is_file():
                    rel = child.relative_to(ROOT).as_posix()
                    if not forbidden(rel):
                        expanded.add(rel)
        else:
            expanded.add(path)
    return expanded


def main(argv: list[str]) -> int:
    archive = Path(argv[1]) if len(argv) > 1 else Path("dist/keystone.zip")
    if not archive.is_file():
        fail(f"archive not found: {archive}")
    with zipfile.ZipFile(archive) as zf:
        names = {name for name in zf.namelist() if not name.endswith("/")}
    missing = sorted(REQUIRED - names)
    if missing:
        fail("missing required files: " + ", ".join(missing))
    forbidden_names = sorted(name for name in names if forbidden(name))
    if forbidden_names:
        fail("forbidden files present: " + ", ".join(forbidden_names))

    expected = expand_allowlist()
    if expected is None:
        expected_list = archive.parent / "keystone.files"
        if expected_list.is_file():
            expected = {
                line.strip()
                for line in expected_list.read_text().splitlines()
                if line.strip()
            }
    if expected is not None:
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
