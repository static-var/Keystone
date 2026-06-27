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

Everything else is internal:

```text
skills/keystone/modules/*.md
skills/keystone/modules/gates/*.md
```

Internal modules are named in the public skill, but they are not separate slash commands.

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
| `read` | Inspect and summarize existing material | Never edits |
| `research` | Gather evidence and compare options | Does not present guesses as facts |
| `write` | Draft or improve prose | Does not change code behavior |
| `ui` | Shape screens, components, visual hierarchy, and interface states | Does not own product architecture |
| `design` | Decide product direction, architecture, and scope | Does not implement |
| `breakdown` | Convert approved direction into ordered tasks | Is not named `plan` |
| `build` | Mutate scoped files | Must pass isolation before first mutation |
| `debug` | Diagnose failures from evidence | Does not guess fixes |
| `review` | Evaluate work without changing it | Read-only: no fixes, commits, or shipping |
| `ship` | Finalize completed work | Does not start new implementation |
| `health` | Assess project/tooling condition | Does not silently fix issues |
| `skill-engineering` | Maintain Keystone itself | Maintainer-only |

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
   └─ .agents/plugins/marketplace.json
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
- `package.json` has required package and Pi metadata

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
| Pi | `package.json` with `pi.skills: ["./skills"]` |
| Claude Code | `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` |
| Codex | `.codex-plugin/plugin.json` |
| Agents/Copilot-style hosts | `.agents/plugins/marketplace.json` |

Keystone is currently a **Pi skill package**, not a Pi extension. A Pi extension would require a `.pi/extensions/*.ts` file, which this repository does not include.

## Common maintainer workflows

### Change routing language

1. Edit `skills/keystone/SKILL.md`.
2. Update `tests/routing/cases.yaml` if behavior changes.
3. Run `make test`.

### Add a module

1. Add `skills/keystone/modules/<name>.md`.
2. Add a routing row in `skills/keystone/SKILL.md`.
3. Add routing fixture coverage.
4. Ensure packaging includes the module directory through `packaging.allowlist`.
5. Run `make test`.

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
