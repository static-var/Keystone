# How Keystone Works

Keystone is one complete package: nine public workflow skills backed by one shared internal gate tree. Each public skill names a phase of work, carries that phase's contract, and can hand off to another skill when the evidence says the job has changed.

There is no central routing layer. Keystone relies on strong model-visible skill descriptions and direct slash commands so the host can load the right workflow from the user's intent.

## The short version

Keystone does five things:

1. **Exposes nine public skills** for the major phases of agent work.
2. **Lets the host or user choose the phase** from natural language or a matching command.
3. **Applies that skill's contract** so the agent knows its scope, boundaries, and completion criteria.
4. **Loads shared gates and standards** when mutation, proof, review, or shipping risk appears.
5. **Hands off with a packet** when another phase should continue the work.

This keeps the agent from mixing jobs. Survey stays evidence-gathering. Planning stays planning. Implementation changes files. Review stays read-only. Shipping only runs when the user explicitly asks for finalization.

## Why Keystone exists

Agent workflows often fail for predictable reasons:

- the agent starts editing before understanding the workspace
- a plan is treated as proof of completion
- review turns into implementation
- shipping happens before verification
- the agent finishes a build and forgets the review or handoff
- platform-specific packaging drifts away from source

Keystone counters those failures with public phase skills, shared gates, and explicit delivery boundaries.

## Public skill graph

The public skills are peers with their own model-visible triggers:

| Skill | Loads when the user asks to... | Usually hands off to... |
|---|---|---|
| `context-survey` | inspect, research, summarize, inventory, compare, validate claims, or answer what is true | `product-planning`, `task-creation`, `project-audit` |
| `product-planning` | brainstorm, shape product/UX/copy/technical direction, decide scope, or create an approved spec | `task-creation`, `context-survey` |
| `task-creation` | create implementation steps, tickets, phases, milestones, checks, or agent-ready work items | `implementation`, `refactoring`, `change-review` |
| `implementation` | add, change, edit, migrate, fix after diagnosis, or execute an approved task | `change-review`, `shipping`, `root-cause-analysis` |
| `refactoring` | simplify, extract, reorganize, reduce duplication, or improve maintainability without behavior change | `change-review`, `implementation`, `root-cause-analysis` |
| `root-cause-analysis` | reproduce, isolate, and explain bugs, regressions, failing tests, flaky behavior, or errors | `implementation`, `refactoring` |
| `change-review` | review a branch, diff, PR, regression risk, correctness, or readiness without mutation | `implementation`, `refactoring`, `root-cause-analysis`, `shipping` |
| `shipping` | explicitly commit, prepare PR, merge, tag, package, publish, release, deploy, finalize, or hand off completed work | none unless the user asks for follow-up |
| `project-audit` | audit repository health, tooling, packaging, architecture, maintenance, or skill drift | `context-survey`, `task-creation`, `implementation`, `refactoring` |

The graph is evidence-driven rather than fixed. A skill continues only when the user's intent and current evidence support the next phase.

## Why no router exists

Keystone's old model made one public entrypoint choose internal modules. The multi-skill model removes that middle step.

A router is unnecessary because each public skill has a strong trigger description. Hosts that support skill discovery can choose from those descriptions, and users can still invoke the desired skill directly. Removing the router also removes a failure mode: the agent no longer has to spend a turn deciding which hidden module to use before doing the actual phase work.

## Why gates stay internal

Gates are shared safety checks, not user goals. A user asks to implement, review, or ship; the skill decides whether it needs isolation, proof, review, or ship checks.

Keeping gates internal gives Keystone one source of truth for repeated contracts without adding extra public commands. It also keeps the public surface focused on outcomes rather than mechanics.

Shared gate paths:

```text
skills/_shared/gates/checkpoint.md
skills/_shared/gates/isolation.md
skills/_shared/gates/proof.md
skills/_shared/gates/red.md
skills/_shared/gates/review.md
skills/_shared/gates/ship.md
```

## Shared standards and handoff packets

Keystone also shares two non-gate references:

```text
skills/_shared/engineering-standards.md
skills/_shared/handoff-packet.md
```

`engineering-standards.md` is language-agnostic guidance for implementation, refactoring, review, and audit work. It keeps attention on ownership, state, boundaries, source of truth, abstraction quality, duplication, and maintainability.

`handoff-packet.md` defines what one skill passes to another:

- source skill
- target skill
- goal
- evidence
- files and mutability
- risks
- next check
- explicit user overrides or waivers

The packet prevents context drift when a workflow crosses phases.

## Artifact lifecycle

Keystone creates durable artifacts when the work has enough agreement or scope to justify them.

| Artifact | Created by | Default path | Rule |
|---|---|---|---|
| Spec | `product-planning` | `docs/keystone/specs/YYYY-MM-DD-<slug>.md` | Create only after the user approves the plan details. Before approval, work in conversation. |
| Task breakdown | `task-creation` | `docs/keystone/tasks/YYYY-MM-DD-<slug>.md` | Create from an approved spec, goal, or user request for tasks/tickets/phases. |
| Refactor doc | `refactoring` | `docs/keystone/refactors/YYYY-MM-DD-<slug>.md` | Create for large or cross-cutting refactors. Small local refactors may proceed after checks. |

Implementation proof, review findings, audit results, and shipping notes may live in conversation unless the user or repository convention asks for a file.

## Mutation and delivery boundaries

### Implementation

`implementation` changes scoped code, content, config, or docs. Before mutation it uses the isolation gate to check branch/worktree state, dirty files, protected paths, and requested scope. For code-quality-sensitive changes it consults shared engineering standards.

### Refactoring

`refactoring` changes internal structure without intended behavior changes. It preserves behavior through existing tests, characterization checks, or other proof. If intended behavior changes, the work belongs in `implementation`. If the failure cause is unknown, it belongs in `root-cause-analysis`.

### Review

`change-review` is read-only. It reports blockers, non-blocking findings, evidence, and a recommended owner skill for follow-up. It does not fix, commit, or ship.

### Shipping

`shipping` finalizes completed work only when explicitly requested. It can prepare commits, PRs, releases, package output, deployment handoffs, or delivery notes, but it must require proof and review evidence or an explicit user waiver.

Explicit-only actions include commits, PR creation, merge, tag, publish, release, deploy, destructive cleanup, and external side effects.

## Host capability notes

Keystone installs as a complete bundle and adapts to each supported surface's capabilities. Individual skills are entry points, not separately supported packages.

| Harness | Discovery and invocation | Subagents / reasoning |
|---|---|---|
| Pi | npm package plus Pi extension registers public skill commands matching skill names | Uses subagent tools only if the active schema exposes them; no assumed named roles, model selection, or thinking controls |
| Claude Code | plugin marketplace installs the Keystone skill package | Use host-supported delegation only when available; otherwise run inline |
| Codex | plugin marketplace installs bundled skills | Reasoning controls are host-dependent; do not assume per-skill controls |

Subagents are optional. A Keystone skill should delegate only when the boundary is clear, the artifact is useful, and coordination cost is lower than inline work.

## Packaging model

Keystone uses a canonical-source packaging pipeline.

```text
canonical skill source
   │
   ▼
npm run regenerate
   │
   ├─ .agents/skills/<skill-name>/SKILL.md
   ├─ .agents/skills/_shared/
   ├─ .agents/plugins/marketplace.json
   ├─ .claude-plugin/plugin.json
   ├─ .claude-plugin/marketplace.json
   └─ .codex-plugin/plugin.json
   │
   ▼
npm run pack:dry-run / package build
```

The canonical public skill directories are expected to be:

```text
skills/context-survey/
skills/product-planning/
skills/task-creation/
skills/implementation/
skills/refactoring/
skills/root-cause-analysis/
skills/change-review/
skills/shipping/
skills/project-audit/
skills/_shared/
```

Generated manifests and Agent Skills bundle files should not be hand-edited. Change the canonical source or package metadata, then regenerate. The generated `.agents/skills/` tree is one unit: all nine entry points share its single `_shared/` directory and are not independently portable.

## Default-deny packaging

The archive is built from `packaging.allowlist`. Files are not shipped unless they are explicitly allowed.

The package script rejects local or generated noise such as:

- `docs/`
- `plans/`
- preview files such as `index.html` and `styles.css`
- `dist/`
- `.git/`
- pycache and `.pyc`
- local plan or design drafts not meant to ship

This keeps the release package focused on the Keystone skill system and generated host surfaces.

## Validation model

Keystone validation should cover three layers.

### Source validation

```bash
python3 scripts/validate-keystone.py
```

This focused validator checks:

- discovered public skill directories have matching frontmatter names and model-visible descriptions
- shared gates and shared references exist under `skills/_shared/`
- stale central-router and one-entrypoint claims are absent from shipped surfaces
- generated bundle skills match canonical content and resolve references through one shared tree
- package and plugin metadata satisfy their structural contracts

### Package validation

```bash
python3 scripts/validate-package.py dist/keystone.zip
```

Expected checks include:

- required package files exist in the archive
- forbidden files are absent
- archive contents match the expanded allowlist
- Claude, Codex, Pi, and the generated bundle expose the same public skill set

### Full verification

`make test` adds the exact nine-skill catalog invariant, invocation-corpus coverage,
complete-bundle reference checks, package validation, and Python compilation.

Known project commands:

```bash
npm run regenerate
npm run validate
npm run typecheck
npm run pack:dry-run
```

If packaging scripts change, update this document and the implementation task with the actual commands.

### Invocation evaluation

`tests/routing/cases.yaml` covers each public skill, ambiguous neighboring phases, and explicit no-skill prompts. Automated tests verify corpus shape, exact nine-skill coverage, and that every case is exported with the full catalog of candidate descriptions. They do not prove which skill a model will select.

Export JSONL for a supported host/model runner:

```bash
python3 scripts/export-invocation-eval.py
```

Before release, run every exported prompt against each host listed as supported, expose all nine descriptions at once, allow either one skill or no skill, and compare the observed selection with `expected`. Record host version, model, case ID, observed selection, and result. Treat unexpected selections as release evidence to fix or explicitly waive; a passing unit test alone is not invocation proof.

## Platform outputs

Keystone provides:

| Host | Output |
|---|---|
| Pi | `.pi/extensions/keystone.ts` plus `package.json` `pi.extensions` and `pi.skills` entries for public skill commands |
| Claude Code | `.claude-plugin/plugin.json` plus `.claude-plugin/marketplace.json` |
| Codex | `.codex-plugin/plugin.json` plus `.agents/plugins/marketplace.json` repo marketplace |
| Complete Agent Skills bundle | `.agents/skills/` with nine skill directories and one sibling `_shared/` tree |

The Pi extension should discover bundled skills and register commands matching the skill names. It should not inject a single-command bootstrap.

The Agent Skills tree is generated from canonical `skills/` sources as one complete bundle. Canonical sources remain the single source of truth; regenerate rather than editing generated files. Copying or installing one skill directory without its sibling skills and `_shared/` tree is unsupported.

## Common maintainer workflows

### Change a public skill

1. Edit `skills/<skill-name>/SKILL.md` or disclosed reference files.
2. Keep shared rules in `skills/_shared/` when more than one skill needs them.
3. Run `npm run regenerate`.
4. Run `npm run validate` and any targeted tests.

### Add or change a shared gate

1. Edit the gate under `skills/_shared/gates/`.
2. Update only the public skills that need to point at it.
3. Regenerate the complete bundle and manifests.
4. Validate source and package contents.

### Change packaging metadata

1. Edit `package.json`, `packaging.allowlist`, or canonical skill frontmatter.
2. Run `npm run regenerate`.
3. Inspect generated manifests.
4. Run `npm run validate` and `npm run pack:dry-run`.

### Prepare a release package

1. Run `npm run typecheck`.
2. Run `npm run validate`.
3. Run `npm run pack:dry-run` and inspect the included files.
4. Use `shipping` only when the user explicitly asks to commit, tag, publish, release, or deploy.

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

1. Are exactly nine public skills exposed?
2. Do public skill names match the agreed names?
3. Are gates internal shared docs rather than commands?
4. Does mutation pass isolation before file changes?
5. Does RCA establish evidence before a fix path?
6. Is review read-only?
7. Is shipping explicit-only?
8. Are specs, tasks, and refactor docs written to documented default paths when needed?
9. Are generated manifests regenerated from canonical source?
10. Do validation and package dry-run pass, or are blockers documented with exact evidence?

## Design principle

Keystone is not trying to make agents more autonomous by removing structure.

It makes agents safer by giving each phase a clear name, a boundary, shared gates, and a proof requirement.
