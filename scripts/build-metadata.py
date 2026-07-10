#!/usr/bin/env python3
"""Generate Keystone platform metadata for the public multi-skill package."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "package.json"
NAME = "keystone"
PACKAGE_DESCRIPTION = "Keystone proactive multi-skill AI engineering workflows for planning, implementation, review, shipping, and maintenance."
HOMEPAGE = "https://keystone.staticvar.dev/"
REPOSITORY = "https://github.com/static-var/Keystone"
PRIVACY_POLICY = f"{HOMEPAGE}privacy/"
TERMS_OF_SERVICE = f"{HOMEPAGE}terms/"
SUPPORT = f"{HOMEPAGE}support/"


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
        "author": {"name": "static-var", "url": HOMEPAGE},
        "homepage": HOMEPAGE,
        "repository": REPOSITORY,
        "license": license_name,
        "keywords": ["agent-skills", "engineering", "workflow", "review", "planning"],
        "skills": "./skills/",
        "interface": {
            "displayName": "Keystone",
            "shortDescription": "Plan, build, review, and ship",
            "longDescription": f"Keystone helps developers move from ambiguity to verified delivery with {len(public_skills)} focused skills for understanding codebases, planning changes, implementing and refactoring safely, diagnosing failures, reviewing work, and shipping with evidence. Each skill keeps the current phase explicit, protects user-owned work, and requires proof before completion claims.",
            "developerName": "static-var",
            "category": "Developer Tools",
            "capabilities": ["Read", "Write", "Review", "Workflow"],
            "brandColor": "#1F2933",
            "composerIcon": "./assets/brand/keystone-icon.png",
            "logo": "./assets/brand/keystone-icon.png",
            "websiteURL": HOMEPAGE,
            "supportURL": SUPPORT,
            "privacyPolicyURL": PRIVACY_POLICY,
            "termsOfServiceURL": TERMS_OF_SERVICE,
            "defaultPrompt": [
                "Survey this repository before planning changes.",
                "Diagnose this failure and prove the root cause before fixing it.",
                "Review this branch for blockers before shipping.",
            ],
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
