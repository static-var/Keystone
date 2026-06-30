#!/usr/bin/env python3
"""Validate Keystone canonical source and packaging invariants."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "keystone"
SKILL = SKILL_DIR / "SKILL.md"
MODULE_DIR = SKILL_DIR / "modules"
PI_EXTENSION = ROOT / ".pi" / "extensions" / "keystone.ts"
CLAUDE_PLUGIN = ROOT / ".claude-plugin" / "plugin.json"
CLAUDE_MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
CODEX_PLUGIN = ROOT / ".codex-plugin" / "plugin.json"
CODEX_MARKETPLACE = ROOT / ".agents" / "plugins" / "marketplace.json"
AGENTS_SKILL_ADAPTER = ROOT / ".agents" / "skills" / "keystone" / "SKILL.md"
ALLOWLIST = ROOT / "packaging.allowlist"
SUBAGENT_HELPER = MODULE_DIR / "helpers" / "subagents.md"
COMMON_PLAYBOOK_HEADINGS = (
    "## Core principle",
    "## Load when",
    "## Not for",
    "## Outcome contract",
    "## Subagents and reasoning",
    "## Hard rules",
    "## Failure modes",
    "## Output format",
)
MODULE_PLAYBOOK_HEADINGS = {
    "build": ("## Modes", "## Process", "Architecture pressure-test:"),
    "review": ("## Review passes", "## Severity rubric", "## Impact tracing", "## Security and regression checklist"),
    "breakdown": ("## Modes", "## Process", "## Requirements inventory", "## Iteration layering", "## Task quality bar"),
}
DEFAULT_PLAYBOOK_HEADINGS = ("## Modes", "## Process")
FORBIDDEN_TRACKED = {
    "docs",
    "plans",
    "index.html",
    "styles.css",
}


def fail(message: str) -> None:
    print(f"validate-keystone: {message}", file=sys.stderr)
    raise SystemExit(1)


def tracked_files() -> list[str]:
    try:
        result = subprocess.run(
            ["git", "ls-files"], cwd=ROOT, text=True, check=True, capture_output=True
        )
    except Exception:
        return []
    return [line for line in result.stdout.splitlines() if line]


def parse_frontmatter(text: str) -> dict[str, object]:
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
            data[current_key] = [] if value == "" else value.strip('"\'')
    return data


def check_skill() -> str:
    if not SKILL_DIR.is_dir():
        fail("missing canonical skill directory skills/keystone/")
    if not SKILL.is_file():
        fail("missing canonical skill file skills/keystone/SKILL.md")
    text = SKILL.read_text()
    metadata = parse_frontmatter(text)
    name = metadata.get("name")
    if name is None:
        heading = re.search(r"^#\s+(.+)$", text, re.M)
        name = heading.group(1).strip().lower() if heading else None
    if str(name).lower() != "keystone":
        fail("skill name must be keystone")
    return text


def check_language(text: str) -> None:
    public_plan = re.compile(r"(?<![\w/.-])/(?:plan)(?![\w/.-])|\bplanner\s+name\s+is\s+plan\b", re.I)
    if public_plan.search(text):
        fail("public /plan mention found; Keystone uses breakdown")
    if not re.search(r"\bbreakdown\b", text, re.I):
        fail("missing required breakdown terminology")


def check_references(text: str) -> None:
    refs = sorted(set(re.findall(r"\(([^)]+\.(?:md|json|yaml|yml|txt|sh|py))\)", text)))
    refs += sorted(set(re.findall(r"(?:^|\s)([A-Za-z0-9_./-]+\.(?:md|json|yaml|yml|txt|sh|py))", text)))
    missing = []
    for ref in refs:
        if ref.startswith(("http://", "https://", "mailto:")) or ref.startswith("/"):
            continue
        candidate = (SKILL_DIR / ref).resolve()
        try:
            candidate.relative_to(ROOT)
        except ValueError:
            continue
        if not candidate.exists():
            missing.append(ref)
    if missing:
        fail("missing referenced module/gate files: " + ", ".join(sorted(set(missing))))


def routing_modules(text: str) -> set[str]:
    return {
        match.group(1)
        for match in re.finditer(r"`modules/([a-z-]+)\.md`", text)
    }


def check_product_modules(skill_text: str) -> None:
    primary_modules = routing_modules(skill_text)
    root_modules = {path.stem for path in MODULE_DIR.glob("*.md")}
    extra = sorted(root_modules - primary_modules)
    missing = sorted(primary_modules - root_modules)
    if extra:
        fail("module files not present in routing table: " + ", ".join(extra))
    if missing:
        fail("routing table modules missing files: " + ", ".join(missing))


def check_module_playbooks(skill_text: str) -> None:
    primary_modules = routing_modules(skill_text)
    pseudo_modules = {"tests", "package", "plan"}
    allowed_terms = {"plan"}  # allowed only as a concept; public /plan remains forbidden elsewhere.
    for path in MODULE_DIR.glob("*.md"):
        text = path.read_text()
        invalid = sorted(
            token for token in re.findall(r"`([a-z][a-z-]+)`", text)
            if token in pseudo_modules and token not in primary_modules and token not in allowed_terms
        )
        if invalid:
            fail(f"module {path.stem} references non-shipped pseudo-modules: " + ", ".join(invalid))
    for name in sorted(primary_modules - {"router"}):
        module = MODULE_DIR / f"{name}.md"
        text = module.read_text()
        required = COMMON_PLAYBOOK_HEADINGS + MODULE_PLAYBOOK_HEADINGS.get(
            name,
            DEFAULT_PLAYBOOK_HEADINGS,
        )
        missing = [
            heading for heading in required
            if re.search(rf"^{re.escape(heading)}\s*$", text, re.M) is None
        ]
        if missing:
            fail(f"module {name} missing playbook headings: " + ", ".join(missing))


def check_skill_quality_regressions(skill_text: str) -> None:
    metadata = parse_frontmatter(skill_text)
    expected_description = "Use when the user invokes /keystone or explicitly asks Keystone to route work."
    if metadata.get("description") != expected_description:
        fail("canonical Keystone description must use the narrow /keystone or explicit routing trigger")
    if AGENTS_SKILL_ADAPTER.is_file():
        adapter_metadata = parse_frontmatter(AGENTS_SKILL_ADAPTER.read_text())
        adapter_description = str(adapter_metadata.get("description", ""))
        if "Use when the user invokes /keystone or explicitly asks Keystone to route work." not in adapter_description:
            fail(".agents adapter description must use the narrow /keystone or explicit routing trigger")
    module_paths = list(MODULE_DIR.glob("*.md")) + list((MODULE_DIR / "gates").glob("*.md"))
    for path in module_paths:
        text = path.read_text()
        rel = path.relative_to(ROOT).as_posix()
        for phrase in ("Default reasoning:", "`xhigh`", "desired reasoning intensity"):
            if phrase in text:
                fail(f"{rel} uses non-portable reasoning-control language: {phrase}")
    health = MODULE_DIR / "health.md"
    if "`no-op`" in health.read_text():
        fail("health module must use `none`, not a non-existent `no-op` module")
    if "Pending human review" in (MODULE_DIR / "gates" / "ship.md").read_text():
        fail("ship gate must not present pending review as passing evidence")
    if "Use a human reviewer, automated reviewer, domain owner, security review, design review, or read-only review pointer" in (MODULE_DIR / "gates" / "review.md").read_text():
        fail("review gate must not list a review pointer as passing review evidence")
    extension = PI_EXTENSION.read_text() if PI_EXTENSION.is_file() else ""
    if "workflow routing" in extension:
        fail("Pi extension must not broaden Keystone invocation to generic workflow routing")
    if "says \\`keystone\\`" in extension or "says `keystone`" in extension:
        fail("Pi bootstrap must not trigger on merely saying keystone")
    if "${piToolMapping()}\n</EXTREMELY_IMPORTANT>`;" in extension:
        fail("Pi bootstrap must stay minimal; inject full host mapping only through /keystone command")


def check_checkpoint_guidance(skill_text: str) -> None:
    checkpoint = MODULE_DIR / "gates" / "checkpoint.md"
    if not checkpoint.is_file():
        fail("missing checkpoint gate: modules/gates/checkpoint.md")
    required_skill_phrases = (
        "modules/gates/checkpoint.md",
        "single source of truth",
        "continue now",
        "pending pointer",
        "Never end a build/change with only",
    )
    for phrase in required_skill_phrases:
        if phrase not in skill_text:
            fail(f"Keystone skill missing checkpoint guidance phrase: {phrase}")
    gate_text = checkpoint.read_text()
    for phrase in ("Auto-advance rule", "Prompt rule", "build` with mutations -> `review"):
        if phrase not in gate_text:
            fail(f"checkpoint gate missing required phrase: {phrase}")
    primary_modules = routing_modules(skill_text)
    for name in sorted(primary_modules):
        module_text = (MODULE_DIR / f"{name}.md").read_text()
        if "Checkpoint" not in module_text:
            fail(f"module {name} must include checkpoint guidance")
    build_text = (MODULE_DIR / "build.md").read_text()
    for phrase in ("After mutation, Build must not stop", "continue to `review` when safe"):
        if phrase not in build_text:
            fail(f"build module missing checkpoint hard rule: {phrase}")


def check_inline_subagent_guidance(skill_text: str) -> None:
    if SUBAGENT_HELPER.exists():
        fail("subagent helper file must not be shipped; keep subagent guidance inline")
    forbidden = "modules/helpers/subagents.md"
    if forbidden in skill_text:
        fail("Keystone skill must not reference the removed subagent helper file")
    required_skill_phrases = (
        "Use subagents when the active host exposes them",
        "@tintinweb/pi-subagents",
        "Agent",
        "get_subagent_result",
        "steer_subagent",
        "Do not assume named roles, model selection, or thinking controls",
    )
    for phrase in required_skill_phrases:
        if phrase not in skill_text:
            fail(f"Keystone skill missing inline subagent guidance phrase: {phrase}")
    for phrase in forbidden_pi_subagent_claims():
        if phrase in skill_text:
            fail(f"Keystone skill advertises non-portable pi-subagents capability: {phrase}")

    primary_modules = routing_modules(skill_text)
    if not primary_modules:
        fail("no primary modules found in Keystone routing table")
    for name in sorted(primary_modules):
        module = MODULE_DIR / f"{name}.md"
        if not module.is_file():
            fail(f"missing primary module file: modules/{name}.md")
        module_text = module.read_text()
        if "## Subagents and reasoning" not in module_text:
            fail(f"module missing subagent reasoning section: modules/{name}.md")
        if forbidden in module_text or "helpers/subagents.md" in module_text:
            fail(f"module references removed subagent helper file: modules/{name}.md")
        for phrase in forbidden_module_subagent_role_claims():
            if phrase in module_text:
                fail(f"module advertises named/non-portable subagent role language: modules/{name}.md: {phrase}")


def forbidden_module_subagent_role_claims() -> tuple[str, ...]:
    return (
        "subagent roles",
        "researcher subagents",
        "architecture reviewer subagents",
        "risk reviewer subagents",
        "worker subagents",
        "subagents/workers",
        "oracle/debug subagents",
        "oracle subagents",
        "debug subagents",
        "scout subagents",
        "reviewer subagents",
        "writer subagents",
        "writer, UI, design, or architecture subagents",
        "specify role,",
        "<role, reasoning, context packet, expected artifact>",
    )


def forbidden_pi_subagent_claims(markdown_escaped: bool = False) -> tuple[str, ...]:
    tick = "\\`" if markdown_escaped else "`"
    return (
        "Prefer narrow roles",
        "narrowest subagent role",
        f"{tick}scout{tick}",
        f"{tick}worker{tick}",
        f"{tick}reviewer{tick}",
        f"{tick}oracle{tick}",
        f"{tick}writer{tick}",
        f"{tick}thinking{tick} or {tick}model{tick}",
        f"{tick}model{tick} or {tick}thinking{tick}",
        f"{tick}thinking{tick} and {tick}model{tick}",
        f"{tick}model{tick} and {tick}thinking{tick}",
        f"{tick}thinking{tick}, {tick}model{tick}",
        f"{tick}model{tick}, {tick}thinking{tick}",
        f"{tick}profile{tick}",
    )


def check_pi_subagent_docs() -> None:
    for path in (ROOT / "README.md", ROOT / "HOW_IT_WORKS.md"):
        if not path.is_file():
            fail(f"missing {path.name}")
        text = path.read_text()
        if "@tintinweb/pi-subagents" not in text:
            fail(f"{path.name} missing @tintinweb/pi-subagents install guidance")
        if "Do not assume named roles" not in text and "does not assume named roles" not in text:
            fail(f"{path.name} must say not to assume named roles or Pi subagent controls")
        for phrase in forbidden_pi_subagent_claims():
            if phrase in text:
                fail(f"{path.name} advertises non-portable pi-subagents capability: {phrase}")


def check_pi_subagents_extension_guidance() -> None:
    if not PI_EXTENSION.is_file():
        fail("missing Pi extension .pi/extensions/keystone.ts")
    extension = PI_EXTENSION.read_text()
    required_phrases = (
        "@tintinweb/pi-subagents",
        "Agent",
        "get_subagent_result",
        "steer_subagent",
        "Follow the canonical Keystone subagent guidance for behavior",
    )
    for phrase in required_phrases:
        if phrase not in extension:
            fail(f"Pi extension missing pi-subagents host mapping phrase: {phrase}")
    behavioral_phrases = (
        "Do not assume named roles, model selection, or thinking controls",
        "Do not invent unsupported subagent tools",
        "Keep read-only work read-only",
    )
    for phrase in behavioral_phrases:
        if phrase in extension:
            fail(f"Pi extension duplicates canonical subagent behavior: {phrase}")
    for phrase in forbidden_pi_subagent_claims(markdown_escaped=True) + ("`profile`",):
        if phrase in extension:
            fail(f"Pi extension advertises non-portable pi-subagents capability: {phrase}")
    if "modules/helpers/subagents.md" in extension or "helpers/subagents.md" in extension:
        fail("Pi extension must not reference removed subagent helper file")


def check_ignored_not_tracked() -> None:
    bad = []
    for path in tracked_files():
        first = path.split("/", 1)[0]
        if path in FORBIDDEN_TRACKED or first in FORBIDDEN_TRACKED:
            bad.append(path)
    if bad:
        fail("ignored artifacts are tracked: " + ", ".join(bad))


def allowlist_entries() -> set[str]:
    if not ALLOWLIST.is_file():
        fail("missing packaging.allowlist")
    return {
        line.strip()
        for line in ALLOWLIST.read_text().splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }


def check_github_actions_node24_compatible() -> None:
    workflows = sorted((ROOT / ".github" / "workflows").glob("*.yml"))
    if not workflows:
        fail("missing GitHub Actions workflows")
    deprecated_refs = (
        "actions/checkout@v4",
        "actions/setup-node@v4",
        "actions/setup-python@v5",
        "actions/upload-artifact@v4",
    )
    for path in workflows:
        text = path.read_text()
        for ref in deprecated_refs:
            if ref in text:
                fail(f"{path.relative_to(ROOT)} uses deprecated Node 20 action {ref}")
    combined = "\n".join(path.read_text() for path in workflows)
    required_refs = (
        "actions/checkout@v6",
        "actions/setup-node@v6",
        "actions/setup-python@v6",
        "actions/upload-artifact@v6",
    )
    for ref in required_refs:
        if ref not in combined:
            fail(f"GitHub Actions workflows missing Node 24-compatible action {ref}")


def check_skills_sh_docs() -> None:
    readme = ROOT / "README.md"
    if not readme.is_file():
        fail("missing README.md")
    text = readme.read_text()
    required = (
        "https://skills.sh/static-var/keystone",
        "npx skills add static-var/keystone --skill keystone",
        "npx skills add static-var/keystone --list",
    )
    for phrase in required:
        if phrase not in text:
            fail(f"README.md missing skills.sh guidance: {phrase}")


def check_agents_skill_adapter() -> None:
    if not AGENTS_SKILL_ADAPTER.is_file():
        fail("missing .agents/skills/keystone/SKILL.md adapter for OpenCode/Copilot-compatible hosts")
    text = AGENTS_SKILL_ADAPTER.read_text()
    if "../../../skills/keystone/SKILL.md" not in text:
        fail(".agents skill adapter must point to canonical skills/keystone/SKILL.md")
    if "Do not expose internal modules" not in text:
        fail(".agents skill adapter must preserve one public Keystone surface")


def check_claude_metadata() -> None:
    if not CLAUDE_PLUGIN.is_file():
        fail("missing Claude plugin manifest .claude-plugin/plugin.json")
    plugin = json.loads(CLAUDE_PLUGIN.read_text())
    if plugin.get("name") != "keystone":
        fail("Claude plugin name must be keystone")
    if "skills" in plugin:
        fail("Claude plugin manifest should rely on the bundled skills/ directory, not legacy skills entries")
    if not CLAUDE_MARKETPLACE.is_file():
        fail("missing Claude marketplace .claude-plugin/marketplace.json")
    marketplace = json.loads(CLAUDE_MARKETPLACE.read_text())
    if marketplace.get("name") != "keystone":
        fail("Claude marketplace name must be keystone")
    if not isinstance(marketplace.get("owner"), dict) or not marketplace["owner"].get("name"):
        fail("Claude marketplace must include owner.name")
    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list) or len(plugins) != 1:
        fail("Claude marketplace must expose exactly one Keystone plugin entry")
    entry = plugins[0]
    if entry.get("name") != "keystone" or entry.get("source") != "./":
        fail('Claude marketplace plugin entry must be keystone with source "./"')


def check_codex_metadata() -> None:
    if not CODEX_PLUGIN.is_file():
        fail("missing Codex plugin manifest .codex-plugin/plugin.json")
    plugin = json.loads(CODEX_PLUGIN.read_text())
    if plugin.get("name") != "keystone":
        fail("Codex plugin name must be keystone")
    if plugin.get("skills") != "./skills/":
        fail('Codex plugin must expose bundled skills with skills: "./skills/"')
    interface = plugin.get("interface")
    if not isinstance(interface, dict):
        fail("Codex plugin must include interface metadata for directory presentation")
    expected_interface = {
        "displayName": "Keystone",
        "brandColor": "#1F2933",
        "composerIcon": "./assets/brand/keystone-icon.png",
        "logo": "./assets/brand/keystone-icon.png",
    }
    for key, value in expected_interface.items():
        if interface.get(key) != value:
            fail(f"Codex plugin interface.{key} must be {value}")
    for asset in (ROOT / "assets/brand/keystone-icon.png", ROOT / "assets/brand/keystone-logo.png"):
        if not asset.is_file():
            fail(f"missing Codex plugin logo asset: {asset.relative_to(ROOT).as_posix()}")
    if not CODEX_MARKETPLACE.is_file():
        fail("missing Codex marketplace .agents/plugins/marketplace.json")
    marketplace = json.loads(CODEX_MARKETPLACE.read_text())
    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list) or len(plugins) != 1:
        fail("Codex marketplace must expose exactly one Keystone plugin entry")
    entry = plugins[0]
    if entry.get("name") != "keystone":
        fail("Codex marketplace plugin entry must be named keystone")
    if entry.get("source") != {"source": "local", "path": "./"}:
        fail('Codex marketplace plugin source must be {"source": "local", "path": "./"}')
    policy = entry.get("policy", {})
    if policy.get("installation") != "AVAILABLE":
        fail("Codex marketplace plugin must be installable")
    if policy.get("authentication") not in {"ON_USE", "ON_INSTALL"}:
        fail("Codex marketplace plugin authentication policy must be ON_USE or ON_INSTALL")


def check_package_json() -> None:
    package_path = ROOT / "package.json"
    if not package_path.is_file():
        fail("missing package.json")
    package = json.loads(package_path.read_text())
    for key in ("name", "version", "description", "license", "keywords"):
        if key not in package:
            fail(f"package.json missing {key}")
    if package.get("name") != "@static-var/keystone":
        fail('package.json name must be "@static-var/keystone" for npm/pi.dev publishing')
    keywords = package.get("keywords", [])
    if not isinstance(keywords, list) or "pi-package" not in keywords:
        fail('package.json keywords must include "pi-package"')
    files = package.get("files")
    expected_files = allowlist_entries()
    if set(files or []) != expected_files:
        fail("package.json files must exactly match packaging.allowlist entries")
    pi = package.get("pi", {})
    if pi.get("skills") != ["./skills"]:
        fail('package.json must set pi.skills to ["./skills"]')
    if pi.get("extensions") != ["./.pi/extensions/keystone.ts"]:
        fail('package.json must set pi.extensions to ["./.pi/extensions/keystone.ts"]')
    if not PI_EXTENSION.is_file():
        fail("missing Pi extension .pi/extensions/keystone.ts")
    extension = PI_EXTENSION.read_text()
    if 'registerCommand("keystone"' not in extension:
        fail("Pi extension must register public /keystone command")
    leaked = sorted(
        name for name in routing_modules(check_skill())
        if name != "keystone" and f'registerCommand("{name}"' in extension
    )
    if leaked:
        fail("Pi extension exposes internal modules as slash commands: " + ", ".join(leaked))


def main() -> int:
    text = check_skill()
    check_language(text)
    check_references(text)
    check_product_modules(text)
    check_module_playbooks(text)
    check_skill_quality_regressions(text)
    check_checkpoint_guidance(text)
    check_inline_subagent_guidance(text)
    check_pi_subagent_docs()
    check_pi_subagents_extension_guidance()
    check_ignored_not_tracked()
    check_github_actions_node24_compatible()
    check_skills_sh_docs()
    check_agents_skill_adapter()
    check_claude_metadata()
    check_codex_metadata()
    check_package_json()
    print("validate-keystone: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
