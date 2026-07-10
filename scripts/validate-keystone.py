#!/usr/bin/env python3
"""Validate Keystone multi-skill metadata and public packaging surfaces."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_RELEASE_VERSION = "2.0.1"
EXPECTED_PUBLIC_SKILLS = {
    "change-review", "context-survey", "implementation", "product-planning",
    "project-audit", "refactoring", "root-cause-analysis", "shipping", "task-creation",
}
SHARED = [
    "skills/_shared/gates/checkpoint.md",
    "skills/_shared/gates/isolation.md",
    "skills/_shared/gates/proof.md",
    "skills/_shared/gates/red.md",
    "skills/_shared/gates/review.md",
    "skills/_shared/gates/ship.md",
    "skills/_shared/engineering-standards.md",
    "skills/_shared/handoff-packet.md",
]
ALLOWLIST = ROOT / "packaging.allowlist"
PI_EXTENSION = ROOT / ".pi" / "extensions" / "keystone.ts"
SHIPPED_SURFACES = [
    "README.md",
    "HOW_IT_WORKS.md",
    "package.json",
    "packaging.allowlist",
    "scripts/build-metadata.py",
    "scripts/validate-package.py",
    ".pi/extensions/keystone.ts",
    ".agents/plugins/marketplace.json",
    ".claude-plugin/plugin.json",
    ".claude-plugin/marketplace.json",
    ".codex-plugin/plugin.json",
]


def fail(message: str) -> None:
    print(f"validate-keystone: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_frontmatter(text: str) -> dict[str, object]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    data: dict[str, object] = {}
    for raw in text[4:end].splitlines():
        if ":" not in raw or raw.startswith("  "):
            continue
        key, value = raw.split(":", 1)
        data[key.strip()] = value.strip().strip('"\'')
    return data


def public_skills() -> list[str]:
    return sorted(
        path.parent.name
        for path in (ROOT / "skills").glob("*/SKILL.md")
        if not path.parent.name.startswith("_") and path.parent.name != "keystone"
    )


def allowlist_entries_for(root: Path) -> set[str]:
    allowlist = root / "packaging.allowlist"
    if not allowlist.is_file():
        fail("missing packaging.allowlist")
    return {line.strip() for line in allowlist.read_text().splitlines() if line.strip() and not line.lstrip().startswith("#")}


def allowlist_entries() -> set[str]:
    return allowlist_entries_for(ROOT)


def check_public_skills() -> None:
    actual = set(public_skills())
    if actual != EXPECTED_PUBLIC_SKILLS:
        fail(f"public skills must be exactly {sorted(EXPECTED_PUBLIC_SKILLS)}; got {sorted(actual)}")
    for skill in public_skills():
        path = ROOT / "skills" / skill / "SKILL.md"
        if not path.is_file():
            fail(f"missing public skill: skills/{skill}/SKILL.md")
        fm = parse_frontmatter(path.read_text())
        if fm.get("name") != skill:
            fail(f"skills/{skill}/SKILL.md frontmatter name must be {skill}")
        if not fm.get("description"):
            fail(f"skills/{skill}/SKILL.md missing model-visible description")
    entries = allowlist_entries()
    if "skills/keystone/SKILL.md" in entries:
        fail("public skills/keystone/SKILL.md entrypoint must not be shipped")
    if "assets/readme/keystone-routing-kami.png" in entries:
        fail("stale routing diagram asset must not be shipped")
    for rel in SHARED:
        if not (ROOT / rel).is_file():
            fail(f"missing shared Keystone file: {rel}")


def metadata_errors(root: Path) -> list[str]:
    errors: list[str] = []
    package = json.loads((root / "package.json").read_text())
    if package.get("name") != "@static-var/keystone":
        errors.append('package.json name must be "@static-var/keystone"')
    if package.get("version") != EXPECTED_RELEASE_VERSION:
        errors.append(f"package.json version must be {EXPECTED_RELEASE_VERSION}")
    if set(package.get("files", [])) != allowlist_entries_for(root):
        errors.append("package.json files must exactly match packaging.allowlist entries")
    if package.get("pi", {}).get("skills") != ["./skills"]:
        errors.append('package.json must set pi.skills to ["./skills"]')

    extension = (root / ".pi" / "extensions" / "keystone.ts").read_text()
    if 'registerCommand("keystone"' in extension or "`/keystone" in extension:
        errors.append("Pi extension must not register or advertise /keystone")
    if "readdirSync(skillsDir" not in extension or "skillDescription(skill)" not in extension:
        errors.append("Pi extension must discover public skills and descriptions from canonical frontmatter")
    if "registerCommand(skill" not in extension:
        errors.append("Pi extension must register commands for discovered public skills")

    for rel in (".claude-plugin/plugin.json", ".claude-plugin/marketplace.json", ".codex-plugin/plugin.json", ".agents/plugins/marketplace.json"):
        data = json.loads((root / rel).read_text())
        if data.get("name") != "keystone":
            errors.append(f"{rel} name must be keystone")
        if rel in (".claude-plugin/plugin.json", ".claude-plugin/marketplace.json", ".codex-plugin/plugin.json") and data.get("version") != EXPECTED_RELEASE_VERSION:
            errors.append(f"{rel} version must be {EXPECTED_RELEASE_VERSION}")
        if rel == ".claude-plugin/marketplace.json":
            plugins = data.get("plugins", [])
            if not plugins or plugins[0].get("version") != EXPECTED_RELEASE_VERSION:
                errors.append(f"{rel} plugins[0].version must be {EXPECTED_RELEASE_VERSION}")
        if rel == ".codex-plugin/plugin.json" and data.get("skills") != "./skills/":
            errors.append(f'{rel} skills must be "./skills/"')
        if rel == ".codex-plugin/plugin.json":
            interface = data.get("interface", {})
            expected_urls = {
                "homepage": "https://keystone.staticvar.dev/",
                "repository": "https://github.com/static-var/Keystone",
            }
            for field, expected in expected_urls.items():
                if data.get(field) != expected:
                    errors.append(f"{rel} {field} must be {expected}")
            interface_urls = {
                "websiteURL": "https://keystone.staticvar.dev/",
                "privacyPolicyURL": "https://keystone.staticvar.dev/privacy/",
                "termsOfServiceURL": "https://keystone.staticvar.dev/terms/",
            }
            for field, expected in interface_urls.items():
                if interface.get(field) != expected:
                    errors.append(f"{rel} interface.{field} must be {expected}")
    return errors


def check_metadata() -> None:
    for error in metadata_errors(ROOT):
        fail(error)


def check_stale_public_language() -> None:
    stale_patterns = [r"one doorway", r"one-router", r"workflow router", r"public router"]
    command_patterns = [r"`/keystone", r"\s/keystone\b"]
    migration_docs = {ROOT / "README.md", ROOT / "HOW_IT_WORKS.md"}
    paths = [ROOT / rel for rel in SHIPPED_SURFACES]
    paths += [ROOT / ".agents" / "skills" / skill / "SKILL.md" for skill in public_skills()]
    paths += [ROOT / "skills" / skill / "SKILL.md" for skill in public_skills()]
    for path in paths:
        if not path.is_file():
            continue
        text = path.read_text().lower()
        patterns = stale_patterns if path in migration_docs else stale_patterns + command_patterns
        for pattern in patterns:
            if re.search(pattern, text):
                fail(f"stale public router language found in {path.relative_to(ROOT)}: {pattern}")


def check_migration_corruption() -> None:
    patterns = {
        r"\.\./_shared/\.\./_shared/": "duplicated shared path",
        r"\bpchange-review\b": "corrupted change-review name",
        r"\b(?:Root-Cause Analysisging|Shippingping|Product Planningd|project-audity)\b": "corrupted skill word",
    }
    paths = [ROOT / "skills" / skill / "SKILL.md" for skill in public_skills()]
    paths += [ROOT / rel for rel in SHARED]
    for path in paths:
        text = path.read_text()
        for pattern, label in patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                fail(f"{label} in {path.relative_to(ROOT)}")


def check_shared_references() -> None:
    paths = [ROOT / "skills" / skill / "SKILL.md" for skill in public_skills()]
    paths += [ROOT / rel for rel in SHARED]
    paths += [ROOT / "README.md", ROOT / "HOW_IT_WORKS.md"]
    gate_names = {Path(rel).name for rel in SHARED if "/gates/" in rel}
    for path in paths:
        text = path.read_text()
        for match in re.finditer(r"`([^`]*?(?:_shared/gates/|gates/)?([a-z-]+\.md))`", text):
            raw, filename = match.groups()
            if filename in gate_names:
                target = ROOT / "skills" / "_shared" / "gates" / filename
                if not target.is_file():
                    fail(f"missing referenced gate from {path.relative_to(ROOT)}: {raw}")
            elif "gate" in raw or "gates/" in raw or "_shared/gates/" in raw:
                fail(f"unknown gate reference from {path.relative_to(ROOT)}: {raw}")
    for rel in SHARED:
        if "/gates/" not in rel:
            continue
        text = (ROOT / rel).read_text()
        stale_names = ["`build`", "`debug`", "`health`", "`research`", "`shape`", "`breakdown`", "Review module"]
        for name in stale_names:
            if name in text:
                fail(f"shared gate contains stale skill/module name in {rel}: {name}")


def orphaned_shared_references(root: Path, shared: list[str]) -> list[str]:
    """Return canonical shared references with no incoming context pointer."""
    shared_paths = {Path(rel) for rel in shared}
    incoming: set[Path] = set()
    sources = list((root / "skills").glob("*/SKILL.md"))
    sources += [root / rel for rel in shared]
    markdown_link = re.compile(r"\]\((?!https?://|/)([^)#]+\.md)(?:#[^)]*)?\)")
    code_pointer = re.compile(r"`([^`]+\.md)`")
    for source in sources:
        if not source.is_file():
            continue
        text = source.read_text()
        pointers = markdown_link.findall(text) + [
            path for path in code_pointer.findall(text) if "<" not in path
        ]
        for relative in pointers:
            target = (source.parent / relative).resolve()
            try:
                target_rel = target.relative_to(root.resolve())
            except ValueError:
                continue
            if target_rel in shared_paths:
                incoming.add(target_rel)
    return sorted(rel.as_posix() for rel in shared_paths - incoming)


def check_shared_reachability() -> None:
    orphaned = orphaned_shared_references(ROOT, SHARED)
    if orphaned:
        fail("shared references require an incoming context pointer: " + ", ".join(orphaned))


def main() -> int:
    check_public_skills()
    check_metadata()
    check_stale_public_language()
    check_migration_corruption()
    check_shared_references()
    check_shared_reachability()
    print("validate-keystone: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
