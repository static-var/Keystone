#!/usr/bin/env python3
"""Validate the Keystone release archive contents."""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

REQUIRED = {
    "package.json",
    "packaging.allowlist",
    "Makefile",
    "scripts/build-metadata.py",
    "scripts/validate-keystone.py",
    "scripts/validate-package.py",
    "scripts/package-keystone.sh",
    "skills/keystone/SKILL.md",
    ".claude-plugin/plugin.json",
    ".claude-plugin/marketplace.json",
    ".codex-plugin/plugin.json",
    ".agents/plugins/marketplace.json",
}
FORBIDDEN_NAMES = {
    "index.html",
    "styles.css",
    ".DS_Store",
}
FORBIDDEN_PREFIXES = (
    "docs/",
    "plans/",
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


def main(argv: list[str]) -> int:
    archive = Path(argv[1]) if len(argv) > 1 else Path("dist/keystone.zip")
    if not archive.is_file():
        fail(f"archive not found: {archive}")
    with zipfile.ZipFile(archive) as zf:
        names = {name for name in zf.namelist() if not name.endswith("/")}
    missing = sorted(REQUIRED - names)
    if missing:
        fail("missing required files: " + ", ".join(missing))
    forbidden = []
    for name in sorted(names):
        base = name.rsplit("/", 1)[-1]
        if base in FORBIDDEN_NAMES or name.startswith(FORBIDDEN_PREFIXES) or name.endswith(FORBIDDEN_SUFFIXES):
            forbidden.append(name)
    if forbidden:
        fail("forbidden files present: " + ", ".join(forbidden))
    print("validate-package: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
