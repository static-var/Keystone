#!/usr/bin/env python3
"""Validate Keystone multi-skill metadata, adapters, and public packaging surfaces."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
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


def allowlist_entries() -> set[str]:
    if not ALLOWLIST.is_file():
        fail("missing packaging.allowlist")
    return {line.strip() for line in ALLOWLIST.read_text().splitlines() if line.strip() and not line.lstrip().startswith("#")}


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


def check_agents_adapters() -> None:
    base = ROOT / ".agents" / "skills"
    generated_public = {
        path.parent.name for path in base.glob("*/SKILL.md")
        if path.parent.name != "writing-great-skills" and not path.parent.name.startswith("_")
    }
    if generated_public != EXPECTED_PUBLIC_SKILLS:
        fail(f"generated public skills must be exactly {sorted(EXPECTED_PUBLIC_SKILLS)}; got {sorted(generated_public)}")
    if (base / "_shared" / "SKILL.md").exists():
        fail(".agents/skills/_shared must be reference only, not a public skill")
    for rel in SHARED:
        shared_rel = Path(rel).relative_to("skills/_shared")
        generated = base / "_shared" / shared_rel
        canonical_shared = ROOT / rel
        if not generated.is_file():
            fail(f"generated Agent Skills bundle is missing _shared/{shared_rel}")
        if generated.read_bytes() != canonical_shared.read_bytes():
            fail(f"generated shared reference is stale: _shared/{shared_rel}")
    for skill in public_skills():
        path = ROOT / ".agents" / "skills" / skill / "SKILL.md"
        if not path.is_file():
            fail(f"missing Agent Skills adapter: .agents/skills/{skill}/SKILL.md")
        text = path.read_text()
        canonical = ROOT / "skills" / skill / "SKILL.md"
        adapter_fm = parse_frontmatter(text)
        canonical_fm = parse_frontmatter(canonical.read_text())
        if adapter_fm != canonical_fm:
            fail(f"adapter metadata for {skill} must match canonical frontmatter")
        expected = canonical.read_text()
        if text != expected:
            fail(f"generated Agent Skill for {skill} is stale")
        if (path.parent / "_shared").exists():
            fail(f"generated Agent Skill for {skill} must use the bundle-level _shared tree")

    markdown_link = re.compile(r"\]\((?!https?://|/)([^)#]+\.md)(?:#[^)]*)?\)")
    code_pointer = re.compile(r"`([^`]+\.md)`")
    markdown_files = [base / skill / "SKILL.md" for skill in public_skills()]
    markdown_files += list((base / "_shared").rglob("*.md"))
    for markdown in markdown_files:
        text = markdown.read_text()
        pointers = markdown_link.findall(text) + [
            path for path in code_pointer.findall(text) if "<" not in path
        ]
        for relative in pointers:
            if not (markdown.parent / relative).resolve().is_file():
                fail(f"unresolved Agent Skills bundle pointer: {markdown.relative_to(base)} -> {relative}")


def check_metadata() -> None:
    package = json.loads((ROOT / "package.json").read_text())
    if package.get("name") != "@static-var/keystone":
        fail('package.json name must be "@static-var/keystone"')
    if set(package.get("files", [])) != allowlist_entries():
        fail("package.json files must exactly match packaging.allowlist entries")
    if package.get("pi", {}).get("skills") != ["./skills"]:
        fail('package.json must set pi.skills to ["./skills"]')
    extension = PI_EXTENSION.read_text()
    if 'registerCommand("keystone"' in extension or "`/keystone" in extension:
        fail("Pi extension must not register or advertise /keystone")
    if "readdirSync(skillsDir" not in extension or "skillDescription(skill)" not in extension:
        fail("Pi extension must discover public skills and descriptions from canonical frontmatter")
    if "registerCommand(skill" not in extension:
        fail("Pi extension must register commands for discovered public skills")
    for rel in (".claude-plugin/plugin.json", ".claude-plugin/marketplace.json", ".codex-plugin/plugin.json", ".agents/plugins/marketplace.json"):
        data = json.loads((ROOT / rel).read_text())
        if data.get("name") != "keystone":
            fail(f"{rel} name must be keystone")


def check_stale_public_language() -> None:
    patterns = [r"`/keystone", r"\s/keystone\b", r"one doorway", r"one-router", r"workflow router", r"public router"]
    paths = [ROOT / rel for rel in SHIPPED_SURFACES]
    paths += [ROOT / ".agents" / "skills" / skill / "SKILL.md" for skill in public_skills()]
    paths += [ROOT / "skills" / skill / "SKILL.md" for skill in public_skills()]
    for path in paths:
        if not path.is_file():
            continue
        text = path.read_text().lower()
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
    check_agents_adapters()
    check_metadata()
    check_stale_public_language()
    check_migration_corruption()
    check_shared_references()
    check_shared_reachability()
    print("validate-keystone: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
