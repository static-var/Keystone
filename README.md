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
│   └── modules/                  # internal modules, helpers, and gates
├── scripts/                      # metadata, validation, packaging
├── tests/routing/cases.yaml      # routing fixture cases
├── tests/test_routing.py         # stdlib routing test runner
├── maintainers/                  # repo-only, not shipped in package
├── .claude-plugin/               # generated Claude plugin metadata
├── .codex-plugin/                # generated Codex plugin metadata
├── .agents/plugins/              # generated agents marketplace metadata
├── packaging.allowlist           # default-deny package contents
├── Makefile                      # test/package/regenerate targets
└── HOW_IT_WORKS.md               # human-readable architecture guide
```

## Subagent and reasoning support

Keystone documents host-specific subagent support in:

```text
skills/keystone/modules/helpers/subagents.md
```

Current summary:

| Harness | Subagents | Per-subagent reasoning |
|---|---:|---:|
| Pi with `pi-subagents` | yes | yes: `thinking`, `model`, `profile` |
| Claude Code | yes | partial: model/detail controls, no general custom-agent reasoning knob |
| Codex CLI/app | host-dependent | partial/global: use prompt advisory unless host exposes per-agent effort |
| T3 Code | unconfirmed | unconfirmed |
| OpenCode | yes | partial/provider-dependent: `model` and provider `variant`; no universal reasoning knob confirmed |
| GitHub Copilot | yes | partial: custom agent `model`, no general reasoning knob |

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
- **Claude plugin metadata** in `.claude-plugin/`
- **Codex plugin metadata** in `.codex-plugin/`
- **Agents marketplace metadata** in `.agents/plugins/`

## Release automation

Pi package discovery is npm-based. The package name is `@static-var/keystone`; the unscoped `keystone` name is already taken on npm.

CI/CD:

- `.github/workflows/ci.yml` runs on PRs and `main`: `npm ci`, Pi extension typecheck, `make test`, npm pack dry-run, and uploads `dist/keystone.zip`.
- `.github/workflows/release.yml` runs on `v*.*.*` tags or manual dispatch: verifies the tag matches `package.json` version, validates, publishes to npm through Trusted Publishing/OIDC with provenance, and creates a GitHub Release with both `dist/keystone.zip` and the npm tarball.

Trusted Publishing setup on npm:

1. Publish/create the package once if npm has no package settings page yet.
2. Open `https://www.npmjs.com/package/@static-var/keystone/access`.
3. In **Trusted Publisher**, choose **GitHub Actions**.
4. Configure:
   - Organization or user: `static-var`
   - Repository: `Keystone`
   - Workflow filename: `release.yml`
   - Environment name: leave blank unless you add a GitHub deployment environment
   - Allowed actions: `npm publish`
5. Save. No `NPM_TOKEN` secret is needed.

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
