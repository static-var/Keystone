#!/usr/bin/env python3
"""Export full-catalog invocation cases for a supported host/model runner."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def frontmatter_description(path: Path) -> str:
    match = re.search(r"^description:\s*(.+)$", path.read_text(encoding="utf-8"), re.MULTILINE)
    if not match:
        raise ValueError(f"missing description: {path}")
    return match.group(1).strip().strip('"\'')


def build_records(root: Path) -> list[dict[str, object]]:
    skills = sorted(
        path.parent.name
        for path in (root / "skills").glob("*/SKILL.md")
        if not path.parent.name.startswith("_") and path.parent.name != "keystone"
    )
    descriptions = {skill: frontmatter_description(root / "skills" / skill / "SKILL.md") for skill in skills}
    cases = json.loads((root / "tests" / "routing" / "cases.yaml").read_text(encoding="utf-8"))
    return [
        {
            **case,
            "decision": "single-label-or-none",
            "candidates": skills,
            "descriptions": descriptions,
        }
        for case in cases
    ]


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    for record in build_records(root):
        print(json.dumps(record, separators=(",", ":")))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"export-invocation-eval: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
