# Keystone

> One public `/keystone` doorway for disciplined AI workflows.

Keystone is a hybrid workflow/skill system for coding agents. It keeps the public surface small, routes each request to one internal module, and uses gates to prevent the common failure modes: editing too early, planning without proof, reviewing while mutating, or shipping unverified work.

Keystone borrows the best parts of Waza-style routing/review/release discipline and Superpowers-style planning, TDD, debugging, and verification habits.

## What Keystone gives you

- **One public entrypoint:** `/keystone`
- **Private internal modules:** router, research, shape, breakdown, build, debug, review, ship, and health
- **A renamed planner:** `breakdown`, not `plan`, to avoid `/plan` collisions
- **Safety gates:** isolation, red, proof, review, and ship
- **Subagent guidance:** host capability matrix plus recommended reasoning level per module
- **Package tooling:** generated platform manifests, allowlisted archive builds, validators, and routing tests
- **Multi-host packaging:** Pi extension + skill package metadata plus Claude/Codex/agents plugin manifests

## Quick start

```bash
# Validate source, package, routing fixtures, and Python scripts
make test

# Regenerate host metadata
make regenerate

# Build the distributable archive
make package
```

The package archive is written to:

```text
dist/keystone.zip
```

`dist/` is generated and ignored by git.

Install in Pi from npm after release:

```bash
pi install npm:@static-var/keystone
```

Or install directly from GitHub:

```bash
pi install git:github.com/static-var/Keystone
```

Then invoke:

```text
/keystone <task>
```

Pi package gallery listing: once `@static-var/keystone` is published to npm with the `pi-package` keyword, it appears on `https://pi.dev/packages`.

## How it works in one picture

```text
User request
   │
   ▼
/keystone public skill
   │
   ▼
Router chooses exactly one primary module
   │
   ├─ router / research / shape / breakdown
   └─ build / debug / review / ship / health
   │
   ▼
Module contract decides what is allowed
   │
   ▼
Gate checks when required
   │
   ├─ isolation: safe before mutation
   ├─ red: failing check before implementation when practical
   ├─ proof: evidence before success claims
   ├─ review: no blocking review findings
   └─ ship: verified, reviewed, ready to hand off
```

## Core rule

Keystone exposes **one public skill**:

```text
skills/keystone/SKILL.md
```

Everything else under `skills/keystone/modules/` is internal. Internal modules are not public slash commands.

## Routing map

| User wants to... | Keystone routes to... |
|---|---|
| classify an ambiguous request | `router` |
| inspect, summarize, research, or compare sources | `research` |
| draft prose, shape product direction, design UI, or make architecture/scope tradeoffs | `shape` |
| turn approved direction into tasks | `breakdown` |
| edit files or implement work | `build` |
| diagnose bugs or failures | `debug` |
| review work without changing it | `review` |
| finalize completed work | `ship` |
| assess project/tooling health | `health` |

## Repository-only maintainer notes

Keystone maintainer guidance can live in the repository without shipping as product. Current maintainer-only notes are in:

```text
maintainers/skill-engineering.md
```

This file is not included in `dist/keystone.zip` and is not part of `/keystone` routing.

## Repository layout

```text
.
├── skills/keystone/              # canonical skill source
│   ├── SKILL.md                  # public /keystone entrypoint
│   └── modules/                  # internal modules and gates
├── scripts/                      # metadata, validation, packaging
├── tests/routing/cases.yaml      # routing fixture cases
├── tests/test_routing.py         # stdlib routing test runner
├── tests/test_package_validator.py # package validator unit coverage
├── maintainers/                  # repo-only, not shipped in package
├── .claude-plugin/               # generated Claude plugin metadata
├── .codex-plugin/                # generated Codex plugin metadata
├── .agents/plugins/              # generated Codex repo marketplace
├── .agents/skills/               # generated Agent Skills adapter for OpenCode/Copilot-compatible hosts
├── packaging.allowlist           # default-deny package contents
├── Makefile                      # test/package/regenerate targets
└── HOW_IT_WORKS.md               # human-readable architecture guide
```

## Subagent and reasoning support

Keystone keeps subagent guidance inline in the root skill and each module. Use subagents only when the active host exposes them and delegation is cheaper than doing the work inline.

For Pi, install the supported subagent extension:

```bash
pi install npm:@tintinweb/pi-subagents
```

Then Keystone can use `Agent`, `get_subagent_result`, and `steer_subagent` when the active tool schema exposes them. Keystone does not assume named roles, model selection, or thinking controls from Pi; if those controls are unavailable, it works inline or encodes intent in the prompt instead of inventing unsupported fields.

Each Keystone module includes a `Subagents and reasoning` section with its default reasoning level.

## Platform support

Keystone currently ships as:

- **Pi extension + skill package** via `package.json`:
  ```json
  {
    "pi": {
      "extensions": ["./.pi/extensions/keystone.ts"],
      "skills": ["./skills"]
    }
  }
  ```
- **Pi extension source** in `.pi/extensions/keystone.ts`, which registers `/keystone`, discovers the bundled skill, and adds a small Pi-specific bootstrap.
- **Claude Code plugin manifest + marketplace** in `.claude-plugin/`
- **Codex plugin manifest** in `.codex-plugin/plugin.json`
- **Codex repo marketplace** in `.agents/plugins/marketplace.json`
- **Agent Skills adapter** in `.agents/skills/keystone/SKILL.md` for OpenCode, GitHub Copilot, VS Code, and other Agent Skills hosts
- **skills.sh listing** at `https://skills.sh/static-var/keystone`

## skills.sh install

Keystone is available on skills.sh as a standard Agent Skill:

```bash
npx skills add static-var/keystone --skill keystone
```

To inspect without installing:

```bash
npx skills add static-var/keystone --list
```

skills.sh page:

```text
https://skills.sh/static-var/keystone
```

## Claude Code plugin install

Keystone is installable as a Claude Code plugin marketplace from this GitHub repo.

In Claude Code:

```text
/plugin marketplace add static-var/Keystone
/plugin install keystone@keystone
```

Then invoke the namespaced Keystone skill:

```text
/keystone:keystone <task>
```

## Codex plugin install

Keystone is also installable as a Codex plugin from this GitHub repo marketplace.

```bash
codex plugin marketplace add static-var/Keystone --ref main
```

Then open the plugin browser and install Keystone:

```bash
codex /plugins
```

CLI install equivalent:

```bash
codex plugin add keystone --marketplace keystone
# or: codex plugin add keystone@keystone
```

After installation, invoke Keystone explicitly with `@keystone` / `$keystone` depending on your Codex surface, or ask Codex to use Keystone for workflow routing.

## OpenCode / Copilot / VS Code skills

Keystone ships a `.agents/skills/keystone` adapter because OpenCode and GitHub Copilot-compatible hosts discover Agent Skills from `.agents/skills`.

Project-local use: clone or vendor this repo into a project and those hosts can discover `.agents/skills/keystone/SKILL.md`.

Personal/global use is best done by linking the canonical skill directory, so module references stay intact:

```bash
# From a repo checkout
KS=/path/to/Keystone

# Or from global npm install
npm install -g @static-var/keystone
KS="$(npm root -g)/@static-var/keystone"

# OpenCode
mkdir -p ~/.config/opencode/skills
ln -s "$KS/skills/keystone" ~/.config/opencode/skills/keystone

# GitHub Copilot / VS Code
mkdir -p ~/.copilot/skills
ln -s "$KS/skills/keystone" ~/.copilot/skills/keystone

# Shared Agent Skills path for compatible hosts
mkdir -p ~/.agents/skills
ln -s "$KS/skills/keystone" ~/.agents/skills/keystone
```

T3 Code currently rides on underlying agents. Use the matching Codex, Claude Code, or OpenCode install path for the provider you run inside T3 Code.

## Release automation

Pi package discovery is npm-based. The package name is `@static-var/keystone`; the unscoped `keystone` name is already taken on npm.

CI/CD:

- `.github/workflows/ci.yml` runs on PRs and `main`: `npm ci`, Pi extension typecheck, `make test`, npm pack dry-run, and uploads `dist/keystone.zip`.
- `.github/workflows/release.yml` runs on `v*.*.*` tags or manual dispatch: verifies the tag matches `package.json` version, validates, publishes to npm through Trusted Publishing/OIDC with provenance, and creates a GitHub Release with both `dist/keystone.zip` and the npm tarball.

Trusted Publishing setup on npm:

1. Confirm you own the npm scope in `package.json`. Keystone currently publishes as `@static-var/keystone`; if your npm username/org is different, rename the package before publishing.
2. Bootstrap the package once, because npm only shows the package access / Trusted Publisher UI after the package exists:
   ```bash
   npm login
   npm run typecheck
   make test
   npm publish --access public --provenance=false
   ```
   If npm requires 2FA, append `--otp <code>`. Local bootstrap disables provenance because provenance is provided by future OIDC releases.
3. Open `https://www.npmjs.com/package/@static-var/keystone/access`.
4. In **Trusted Publisher**, choose **GitHub Actions**.
5. Configure:
   - Organization or user: `static-var`
   - Repository: `Keystone`
   - Workflow filename: `release.yml`
   - Environment name: leave blank unless you add a GitHub deployment environment
   - Allowed actions: `npm publish`
6. Save. Future releases use OIDC; no `NPM_TOKEN` secret is needed.

Release:

```bash
npm version patch --no-git-tag-version  # or minor/major; edit changelog if added later
make test
VERSION=$(node -p "require('./package.json').version")
git add package.json package-lock.json
git commit -m "chore: release v${VERSION}"
git tag "v${VERSION}"
git push origin main --tags
```

## Maintainer commands

```bash
make regenerate      # rebuild generated plugin/marketplace metadata
make validate        # build package, validate source, validate archive
make routing         # run routing fixture tests
make package         # write dist/keystone.zip from packaging.allowlist
make test            # run the full local check suite
npm run typecheck    # typecheck the Pi extension
npm run pack:dry-run # preview npm package contents
```

## Guardrails

- Do not add public slash commands for internal modules.
- Do not rename `breakdown` to `plan`.
- Do not let `build` edit before the isolation gate.
- Do not let `review` fix, commit, or ship.
- Do not let `ship` start new implementation.
- Do not hand-edit generated manifests; update source and run `make regenerate`.
- Do not package ignored local artifacts such as `index.html`, `styles.css`, `plans/`, `docs/`, `dist/`, or pycache files.

## Read next

For the full mental model, routing lifecycle, packaging flow, and maintainer workflow, read:

```text
HOW_IT_WORKS.md
```

## License

MIT
