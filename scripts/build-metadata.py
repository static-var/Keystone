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


AGENT_SKILL_DESCRIPTION = (
    "Keystone adapter for Agent Skills hosts such as OpenCode, GitHub Copilot, and VS Code. "
    "Use when the user invokes /keystone or explicitly asks Keystone to route work."
)


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


def write_agent_skill_adapter() -> None:
    path = ROOT / ".agents" / "skills" / "keystone" / "SKILL.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"""---
name: keystone
description: {AGENT_SKILL_DESCRIPTION}
---

# Keystone Agent Skills Adapter

This is a thin adapter for hosts that discover skills from `.agents/skills/<name>/SKILL.md`.

The canonical Keystone skill lives at:

```text
../../../skills/keystone/SKILL.md
```

When this adapter is loaded:

1. Read `../../../skills/keystone/SKILL.md`, resolved relative to this adapter file's directory.
2. Follow the canonical Keystone entrypoint exactly.
3. Resolve Keystone module, gate, and helper paths relative to `skills/keystone/`, not relative to this adapter directory.
4. Keep the public surface as one Keystone skill. Do not expose internal modules as separate public commands.
"""
    )


def main() -> int:
    package = read_package()
    skill_text = SKILL.read_text() if SKILL.exists() else ""
    description = skill_summary(skill_text) if skill_text else package.get("description", "Keystone skill.")
    version = package.get("version", "0.0.0")
    license_name = package.get("license", "UNLICENSED")

    claude_plugin = {
        "$schema": "https://json.schemastore.org/claude-code-plugin.json",
        "name": NAME,
        "version": version,
        "description": description,
        "author": {"name": "static-var"},
        "repository": "https://github.com/static-var/Keystone",
        "license": license_name,
    }
    claude_marketplace = {
        "$schema": "https://json.schemastore.org/claude-code-marketplace.json",
        "name": NAME,
        "version": version,
        "description": "Keystone plugin marketplace for Claude Code.",
        "owner": {"name": "static-var"},
        "plugins": [
            {
                "name": NAME,
                "source": "./",
                "description": description,
                "version": version,
                "author": {"name": "static-var"},
                "category": "productivity",
                "tags": ["workflow", "skills", "engineering", "review", "planning"],
            }
        ],
    }

    codex_plugin = {
        "name": NAME,
        "version": version,
        "description": description,
        "skills": "./skills/",
        "interface": {
            "displayName": "Keystone",
            "shortDescription": "One doorway for disciplined AI workflows.",
            "longDescription": "Keystone routes AI coding work through one public entrypoint, with internal modules and gates for research, shaping, implementation, debugging, review, and shipping.",
            "developerName": "static-var",
            "category": "Development & Workflow",
            "capabilities": ["Read", "Write", "Review", "Workflow"],
            "brandColor": "#1F2933",
            "composerIcon": "./assets/brand/keystone-icon.png",
            "logo": "./assets/brand/keystone-icon.png",
            "defaultPrompt": [
                "Use Keystone to route this task before editing.",
                "Use Keystone to review this branch for blockers.",
                "Use Keystone to ship this change with proof.",
            ],
        },
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

    write_json(ROOT / ".claude-plugin" / "plugin.json", claude_plugin)
    write_json(ROOT / ".claude-plugin" / "marketplace.json", claude_marketplace)
    write_json(ROOT / ".codex-plugin" / "plugin.json", codex_plugin)
    write_json(ROOT / ".agents" / "plugins" / "marketplace.json", codex_marketplace)
    write_agent_skill_adapter()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
