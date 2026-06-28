# How Keystone Works

Keystone is easiest to understand as a building with one front door and many private rooms.

The front door is `/keystone`. The private rooms are internal modules. The gates are checkpoints that stop the agent from doing risky work too early.

## The short version

Keystone does five things:

1. **Receives a request** through one public skill: `/keystone`.
2. **Routes the request** to exactly one internal module.
3. **Applies that module's contract** so the agent knows what it may and may not do.
4. **Loads gates only when needed** to protect mutation, verification, review, and shipping.
5. **Hands off cleanly** to the next module when the work changes shape.

When the host supports subagents, Keystone can delegate bounded work with the right reasoning level. When the host does not support that control, Keystone treats reasoning level as prompt guidance instead of a guaranteed setting.

This keeps the agent from mixing jobs. Planning stays planning. Building stays building. Review stays read-only. Shipping only happens after proof and review.

## Why Keystone exists

Agent workflows often fail for predictable reasons:

- the agent starts editing before understanding the workspace
- a plan is treated as proof of completion
- review turns into implementation
- shipping happens before verification
- too many public commands overlap and conflict
- platform-specific packaging drifts away from the real source

Keystone counters those failures with a small public surface and explicit internal contracts.

## The public surface

There is one public skill:

```text
skills/keystone/SKILL.md
```

That file is the only public entrypoint. Users invoke Keystone with `/keystone` or by asking Keystone to route work.

Everything else in the shipped skill is internal:

```text
skills/keystone/modules/*.md
skills/keystone/modules/gates/*.md
```

Internal modules are named in the public skill, but they are not separate slash commands.

Maintainer-only notes may live elsewhere in the repository, such as `maintainers/skill-engineering.md`. Those files are not part of the shipped product.

## Request lifecycle

```text
1. User asks for work
       │
       ▼
2. Keystone public skill loads
       │
       ▼
3. Router selects one primary module
       │
       ▼
4. The module contract controls the work
       │
       ▼
5. Gates run only if the module needs them
       │
       ▼
6. Keystone reports result or hands off to the next module
```

The important phrase is **one primary module**. Keystone avoids blending roles unless a module explicitly hands off.

## Modules

Each module has the same shape:

- **Intent:** what the module is for
- **Load when:** when Keystone should choose it
- **Allowed mutation:** what files or artifacts it may change
- **Must not:** hard boundaries
- **May call:** allowed handoffs or gates
- **Handoff:** what it should report when done
- **Exit gate:** what must be true before leaving the module

### Module catalogue

| Module | Job | Hard boundary |
|---|---|---|
| `router` | Choose the right module | Does not do the work itself |
| `research` | Inspect, summarize, gather evidence, and compare options | Does not edit or present guesses as facts |
| `shape` | Draft prose, shape product direction, UI/UX, visual direction, and scope | Does not implement or treat a spec as proof |
| `breakdown` | Convert approved direction into ordered tasks | Is not named `plan` |
| `build` | Mutate scoped files | Must pass isolation before first mutation |
| `debug` | Diagnose failures from evidence | Does not guess fixes |
| `review` | Evaluate work without changing it | Read-only: no fixes, commits, or shipping |
| `ship` | Finalize completed work | Does not start new implementation |
| `health` | Assess project/tooling condition | Does not silently fix issues |

## Subagents and reasoning

Keystone keeps subagent guidance inline in `skills/keystone/SKILL.md`, the Pi extension bootstrap, and each module's `Subagents and reasoning` section. There is no separate helper file to load.

Use subagents only when the active host exposes them and delegation has a clear boundary, useful artifact, and lower coordination cost than inline work.

For Pi, Keystone is configured for `@tintinweb/pi-subagents` (https://github.com/tintinweb/pi-subagents):

```bash
pi install npm:@tintinweb/pi-subagents
```

When installed, Keystone may use `Agent`, `get_subagent_result`, and `steer_subagent` if the active tool schema exposes them. It does not assume named roles, model selection, or thinking controls from Pi; otherwise it works inline.

### Host capability summary

| Harness | Subagents | Reasoning control |
|---|---:|---|
| Pi coding agent with `@tintinweb/pi-subagents` | yes | use only controls exposed by the active tool schema; do not assume named roles, `model`, or `thinking` |
| Claude Code | yes | model selection and built-in Explore detail; no general custom-agent reasoning field confirmed |
| Codex CLI/app | host-dependent | global `model_reasoning_effort`; per-subagent effort not confirmed |
| T3 Code | not confirmed | not confirmed |
| OpenCode | yes | partial/provider-dependent: `model` plus provider-specific `variant`; no universal reasoning knob confirmed; discovers Keystone through `.agents/skills` or symlinked canonical skill |
| GitHub Copilot / VS Code | yes | custom agent `model`; no general reasoning field confirmed; discovers Keystone through `.agents/skills`, `.github/skills`, or personal skill dirs |

### Module reasoning defaults

| Module group | Default reasoning |
|---|---|
| router, simple reading, simple writing | `low` to `medium` |
| research, shape, build, health, ship | `medium`, escalating to `high` for risk |
| breakdown, debug, review, high-stakes shape decisions | `high`, escalating to `xhigh` for hard or irreversible work |
| gates | `low`, escalating only when evidence is safety-critical |

The rule is simple: delegate the narrowest bounded task and request the lowest reasoning intensity that can safely complete it. Only use role names, model selection, or thinking controls when the active host schema exposes them. Escalate for ambiguity, irreversible decisions, security, data loss, release risk, or root-cause uncertainty.

## Gates

Gates are small checks loaded by modules when needed.

| Gate | Purpose | Usually used by |
|---|---|---|
| `isolation` | Confirm mutation is safe before editing | `build` |
| `red` | Establish a failing check or reproduction when practical | `build`, `debug` |
| `proof` | Verify claims with evidence before success reports | `debug`, `ship`, `health` |
| `review` | Confirm required review has no blockers | `ship` |
| `ship` | Confirm verified, reviewed work is ready for handoff | `ship` |

The gates are deliberately boring. Their job is to stop common mistakes, not to be clever.

## Why `breakdown`, not `plan`

Many tools already use `/plan`. Keystone keeps `/keystone` as the only public entrypoint and uses `breakdown` internally for task decomposition.

So this is correct:

```text
/keystone → breakdown
```

This is not:

```text
/plan
```

The name also clarifies the job: `breakdown` turns an approved direction into verifiable work items. It does not mean the work is done.

## Build vs. ship

Keystone separates implementation from finalization.

### Build

`build` is for changing files. Before the first mutation it must check isolation:

- What branch/worktree are we in?
- What files are protected?
- Are there unrelated dirty changes?
- Is the requested scope clear?

`build` may implement, refactor, edit, or create files. It does not merge, publish, or call the work shippable by itself.

### Ship

`ship` is for finalizing completed work. It can prepare delivery notes, package output, PR/merge handoff, or release readiness.

It should only run after proof and review are satisfied or explicitly waived.

## Review is read-only

The `review` module never fixes. This is intentional.

A reviewer that edits while reviewing blurs evidence. Keystone keeps review as a report:

- blockers
- non-blocking findings
- evidence
- recommended owner module for follow-up

If something must be fixed, Keystone routes back to `build` or `debug`.

## Packaging model

Keystone uses a canonical-source packaging pipeline.

```text
canonical skill source
   │
   ▼
make regenerate
   │
   ├─ .claude-plugin/plugin.json
   ├─ .claude-plugin/marketplace.json
   ├─ .codex-plugin/plugin.json
   ├─ .agents/plugins/marketplace.json
   └─ .agents/skills/keystone/SKILL.md
   │
   ▼
make package
   │
   ▼
dist/keystone.zip
```

The canonical source is:

```text
skills/keystone/
```

Generated manifests should not be hand-edited. Change the canonical source or package metadata, then run:

```bash
make regenerate
```

## Default-deny packaging

The archive is built from `packaging.allowlist`.

That means files are not shipped unless they are explicitly allowed.

The package script rejects known local or generated noise:

- `docs/`
- `plans/`
- `index.html`
- `styles.css`
- `dist/`
- `.git/`
- pycache and `.pyc`
- `*.plan.md`, `*-plan.md`
- `*.design.md`, `*-design.md`

This keeps the release package focused on the Keystone skill system, not local planning or preview artifacts.

## Validators

Keystone has three validation layers.

### Source validation

```bash
python3 scripts/validate-keystone.py
```

Checks include:

- canonical skill exists
- skill name is `keystone`
- `breakdown` terminology is present
- public `/plan` is not introduced
- referenced modules/gates exist
- ignored artifacts are not tracked
- `package.json` has required package and Pi extension/skill metadata

### Package validation

```bash
python3 scripts/validate-package.py dist/keystone.zip
```

Checks include:

- required package files exist in the archive
- forbidden files are absent
- archive contents match the expanded allowlist

### Routing validation

```bash
python3 -m unittest tests/test_routing.py
```

Checks include:

- routing fixtures are valid
- every Keystone module has coverage
- `/plan` routes to `breakdown`, not a public planner
- fixture prompts match the routing table in `skills/keystone/SKILL.md`

## Full verification

Run everything with:

```bash
make test
```

This runs metadata generation, packaging, source validation, package validation, routing tests, and Python compile checks.

## Platform outputs

Keystone currently provides:

| Host | Output |
|---|---|
| Pi | `.pi/extensions/keystone.ts` plus `package.json` with `pi.extensions` and `pi.skills` |
| Claude Code | `.claude-plugin/plugin.json` plus `.claude-plugin/marketplace.json` marketplace |
| Codex | `.codex-plugin/plugin.json` plus `.agents/plugins/marketplace.json` repo marketplace |
| OpenCode / GitHub Copilot / VS Code | `.agents/skills/keystone/SKILL.md` adapter plus canonical `skills/keystone/` |
| T3 Code | use the underlying Codex, Claude Code, or OpenCode install path |

The Claude Code plugin path uses Claude's marketplace pattern: `.claude-plugin/plugin.json` identifies the repository root as a plugin, and `.claude-plugin/marketplace.json` exposes a single installable `keystone` entry with source `./`. Users add it with `/plugin marketplace add static-var/Keystone`, install with `/plugin install keystone@keystone`, then invoke `/keystone:keystone`.

The Pi extension mirrors the Superpowers packaging pattern: it discovers bundled skills, registers `/keystone` as the public command, and injects a compact Pi-specific bootstrap while keeping internal modules private.

The Codex plugin path uses the Codex plugin marketplace pattern: `.codex-plugin/plugin.json` declares the bundled skill directory, while `.agents/plugins/marketplace.json` exposes a single installable Keystone entry whose local source is the repository root. Users can add it with `codex plugin marketplace add static-var/Keystone --ref main`, then install Keystone from `codex /plugins` or `codex plugin add keystone --marketplace keystone`.

OpenCode, GitHub Copilot, and VS Code support the Agent Skills standard directly. Keystone ships `.agents/skills/keystone/SKILL.md` as a thin adapter that points those hosts back to the canonical `skills/keystone/SKILL.md`, preserving one source of truth and one public Keystone skill.

The Pi package gallery at `https://pi.dev/packages` indexes npm packages. Keystone publishes as `@static-var/keystone` with the `pi-package` keyword, so installs use:

```bash
pi install npm:@static-var/keystone
```

## Common maintainer workflows

### Change routing language

1. Edit `skills/keystone/SKILL.md`.
2. Update `tests/routing/cases.yaml` if behavior changes.
3. Run `make test`.

### Release Keystone

1. Confirm the npm scope in `package.json` is owned by the publisher. Keystone currently uses `@static-var/keystone`.
2. If the npm package does not exist yet, bootstrap it once with `npm login`, `npm run typecheck`, `make test`, and `npm publish --access public --provenance=false`; append `--otp <code>` if npm requires 2FA. npm only exposes Trusted Publisher settings after the package exists.
3. In npm package access settings for `@static-var/keystone`, configure Trusted Publisher → GitHub Actions with user `static-var`, repository `Keystone`, workflow filename `release.yml`, no environment, and allowed action `npm publish`.
4. Bump `package.json` with `npm version <patch|minor|major> --no-git-tag-version`.
5. Run `npm run typecheck` and `make test`.
6. Commit `package.json` and `package-lock.json`.
7. Tag the commit as `v<package.json version>` and push `main` plus tags.
8. The release workflow publishes npm via Trusted Publishing/OIDC with provenance and creates a GitHub Release containing the npm tarball plus `dist/keystone.zip`.

### Add a shipped module

1. Add `skills/keystone/modules/<name>.md`.
2. Add a routing row in `skills/keystone/SKILL.md`.
3. Add routing fixture coverage.
4. Add a `Subagents and reasoning` section to the module.
5. Ensure packaging includes the module directory through `packaging.allowlist`.
7. Run `make test`.

### Add maintainer-only guidance

1. Put it outside `skills/keystone/`, for example under `maintainers/`.
2. Do not add it to `skills/keystone/SKILL.md` routing.
3. Do not add it to `packaging.allowlist` unless it is meant to ship.
4. Run `make test` and inspect `dist/keystone.zip` if packaging changed.

### Change packaging metadata

1. Edit `package.json` or canonical skill frontmatter.
2. Run `make regenerate`.
3. Inspect generated manifests if needed.
4. Run `make test`.

### Prepare a release package

```bash
make package
```

Then inspect:

```text
dist/keystone.zip
```

## What should stay out of git

These are local or generated artifacts:

```text
dist/
index.html
styles.css
plans/
scripts/__pycache__/
tests/__pycache__/
```

They may exist locally, but they should remain ignored.

## Mental checklist for Keystone behavior

Before changing Keystone, ask:

1. Is `/keystone` still the only public entrypoint?
2. Did we avoid creating `/plan`?
3. Does each request still route to one primary module?
4. Does `build` still check isolation before mutation?
5. Is `review` still read-only?
6. Does `ship` only finalize already-completed work?
7. Are generated manifests regenerated from source?
8. Does `make test` pass?

If the answer to any question is no, Keystone's contract has drifted.

## Design principle

Keystone is not trying to make agents more autonomous by removing structure.

It makes agents safer by giving each phase a name, a boundary, and a proof requirement.
