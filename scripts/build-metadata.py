#!/usr/bin/env python3
"""Generate Keystone platform metadata for the public multi-skill package."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "package.json"
NAME = "keystone"
PACKAGE_DESCRIPTION = "Keystone proactive multi-skill AI engineering workflows for planning, implementation, review, shipping, and maintenance."


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text()
    if not text.startswith("---\n"):
        raise ValueError(f"missing frontmatter: {path.relative_to(ROOT)}")
    end = text.find("\n---", 4)
    if end == -1:
        raise ValueError(f"unclosed frontmatter: {path.relative_to(ROOT)}")
    data: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" in line and not line.startswith(" "):
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip().strip('"\'')
    return data


def public_skill_catalog() -> list[dict[str, str]]:
    catalog = []
    for path in sorted((ROOT / "skills").glob("*/SKILL.md")):
        if path.parent.name.startswith("_") or path.parent.name == "keystone":
            continue
        metadata = parse_frontmatter(path)
        name = metadata.get("name", "")
        description = metadata.get("description", "")
        if name != path.parent.name or not description:
            raise ValueError(f"invalid public skill frontmatter: {path.relative_to(ROOT)}")
        catalog.append({"name": name, "description": description})
    if not catalog:
        raise ValueError("no public skills found")
    return catalog


def read_package() -> dict:
    return json.loads(PACKAGE.read_text()) if PACKAGE.exists() else {}


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def agent_skill_text(skill: str) -> str:
    """Render one canonical skill inside the atomic Agent Skills bundle."""
    return (ROOT / "skills" / skill / "SKILL.md").read_text()


def write_agent_skills(catalog: list[dict[str, str]]) -> None:
    base = ROOT / ".agents" / "skills"
    shared = base / "_shared"
    if shared.exists():
        shutil.rmtree(shared)
    shutil.copytree(ROOT / "skills" / "_shared", shared)
    for entry in catalog:
        skill = entry["name"]
        target = base / skill
        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True)
        (target / "SKILL.md").write_text(agent_skill_text(skill))


def main() -> int:
    package = read_package()
    catalog = public_skill_catalog()
    public_skills = [entry["name"] for entry in catalog]
    version = package.get("version", "0.0.0")
    license_name = package.get("license", "UNLICENSED")

    claude_plugin = {
        "$schema": "https://json.schemastore.org/claude-code-plugin.json",
        "name": NAME,
        "version": version,
        "description": PACKAGE_DESCRIPTION,
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
        "plugins": [{"name": NAME, "source": "./", "description": PACKAGE_DESCRIPTION, "version": version, "author": {"name": "static-var"}, "category": "productivity", "tags": ["workflow", "skills", "engineering", "review", "planning"]}],
    }
    codex_plugin = {
        "name": NAME,
        "version": version,
        "description": PACKAGE_DESCRIPTION,
        "skills": "./skills/",
        "interface": {
            "displayName": "Keystone",
            "shortDescription": "Proactive AI engineering workflow skills.",
            "longDescription": f"Keystone ships {len(public_skills)} public engineering workflow skills. Skills are invoked directly by intent; there is no central command.",
            "developerName": "static-var",
            "category": "Development & Workflow",
            "capabilities": ["Read", "Write", "Review", "Workflow"],
            "brandColor": "#1F2933",
            "composerIcon": "./assets/brand/keystone-icon.png",
            "logo": "./assets/brand/keystone-icon.png",
            "defaultPrompt": ["Survey this repository before planning changes.", "Implement this approved task with proof.", "Review this branch for blockers before shipping."],
        },
    }
    codex_marketplace = {
        "name": NAME,
        "interface": {"displayName": "Keystone"},
        "plugins": [{"name": NAME, "displayName": "Keystone", "source": {"source": "local", "path": "./"}, "policy": {"installation": "AVAILABLE", "authentication": "ON_USE"}, "category": "Development & Workflow", "description": PACKAGE_DESCRIPTION}],
    }

    write_json(ROOT / ".claude-plugin" / "plugin.json", claude_plugin)
    write_json(ROOT / ".claude-plugin" / "marketplace.json", claude_marketplace)
    write_json(ROOT / ".codex-plugin" / "plugin.json", codex_plugin)
    write_json(ROOT / ".agents" / "plugins" / "marketplace.json", codex_marketplace)
    write_agent_skills(catalog)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
