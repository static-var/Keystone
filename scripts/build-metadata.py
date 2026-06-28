#!/usr/bin/env python3
"""Generate Keystone platform metadata from the canonical skill source."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "keystone" / "SKILL.md"
PACKAGE = ROOT / "package.json"
NAME = "keystone"


def read_package() -> dict:
    if PACKAGE.exists():
        return json.loads(PACKAGE.read_text())
    return {}


def parse_frontmatter(text: str) -> dict:
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
            if value == "":
                data[current_key] = []
            else:
                data[current_key] = value.strip('"\'')
    return data


def skill_summary(text: str) -> str:
    fm = parse_frontmatter(text)
    for key in ("description", "summary"):
        if isinstance(fm.get(key), str) and fm[key]:
            return str(fm[key])
    match = re.search(r"^#\s+(.+)$", text, re.M)
    if match:
        return match.group(1).strip()
    return "Keystone skill."


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def main() -> int:
    package = read_package()
    skill_text = SKILL.read_text() if SKILL.exists() else ""
    fm = parse_frontmatter(skill_text)
    description = skill_summary(skill_text) if skill_text else package.get("description", "Keystone skill.")
    version = package.get("version", "0.0.0")
    license_name = package.get("license", "UNLICENSED")
    keywords = package.get("keywords", ["keystone", "skill"])

    plugin = {
        "name": NAME,
        "version": version,
        "description": description,
        "license": license_name,
        "skills": [{"name": NAME, "path": "../skills/keystone/SKILL.md"}],
    }
    claude_marketplace = {
        "name": NAME,
        "displayName": "Keystone",
        "version": version,
        "description": description,
        "license": license_name,
        "keywords": keywords,
        "skills": [NAME],
    }
    if isinstance(fm.get("author"), str):
        claude_marketplace["author"] = fm["author"]

    codex_plugin = {
        "name": NAME,
        "version": version,
        "description": description,
        "skills": "./skills/",
    }
    codex_marketplace = {
        "name": NAME,
        "interface": {"displayName": "Keystone"},
        "plugins": [
            {
                "name": NAME,
                "displayName": "Keystone",
                "source": {"source": "local", "path": "./"},
                "policy": {"installation": "AVAILABLE", "authentication": "ON_USE"},
                "category": "Development & Workflow",
                "description": description,
            }
        ],
    }

    write_json(ROOT / ".claude-plugin" / "plugin.json", plugin)
    write_json(ROOT / ".claude-plugin" / "marketplace.json", claude_marketplace)
    write_json(ROOT / ".codex-plugin" / "plugin.json", codex_plugin)
    write_json(ROOT / ".agents" / "plugins" / "marketplace.json", codex_marketplace)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
