# Keystone

<p align="center">
  <img src="assets/brand/keystone-logo.svg" alt="Keystone" width="360">
</p>

<p align="center">
  <a href="https://www.npmjs.com/package/@static-var/keystone"><img alt="npm" src="https://img.shields.io/npm/v/%40static-var%2Fkeystone"></a>
  <a href="https://github.com/static-var/Keystone/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/static-var/Keystone/actions/workflows/ci.yml/badge.svg"></a>
  <a href="https://github.com/static-var/Keystone/blob/main/LICENSE"><img alt="License: MIT" src="https://img.shields.io/npm/l/%40static-var%2Fkeystone"></a>
</p>

> Proactive workflow skills for disciplined AI work: use the right phase, keep boundaries clear, and prove the result.

Keystone is a package of model-discoverable workflow skills for coding agents. Instead of sending every request through a single router, Keystone exposes the phases agents need for project work: survey, plan, break down, implement, refactor, diagnose, review, ship, and audit.

Use Keystone when you want an agent to move deliberately: gather evidence before decisions, mutate only after isolation checks, separate review from fixing, and require proof before success claims.

## When Keystone loads

Keystone auto-loads only when the request is both **project-bound** and **workflow-worthy**:

- **Project-bound** means the request's subject is a software or product repository, initiative, feature, architecture, regression, release, or project decision.
- **Workflow-worthy** means a Keystone phase contract would materially change how the work should proceed.

The prompt's subject controls eligibility, not the current working directory. A public web search performed while the agent happens to be inside a repository remains normal agent work. Project-specific external research can qualify when its evidence informs that project's decision or change. Pure repository understanding or reconnaissance also qualifies when the repository itself is the subject, even without a downstream decision or change.

Normal agent behavior handles standalone public web search and recommendations, generic summaries and explanations, ordinary copywriting or brainstorming, mechanical single-file config or documentation edits, and one-off scripts. Keystone remains appropriate for integrated project config or scripts, product copy decisions, diagnosis, review, audit, and explicitly requested shipping.

Near-pairs make the boundary concrete:

| Normal agent behavior | Keystone project workflow |
|---|---|
| Compare current password-manager prices. | Compare authentication providers against this repository's architecture constraints. |
| Write a one-off script to rename local images. | Add a migration script integrated with this project's CI and verify it. |
| Change one value in a tool config. | Migrate the application's config schema across runtime code and tests. |
| Rewrite this standalone announcement. | Decide the in-product upgrade copy and acceptance criteria for this feature. |

## Why use Keystone?

Agents usually fail in predictable ways:

- they edit before understanding the repo
- they treat a plan as proof
- they debug by guessing
- they review while changing files
- they ship without evidence

Keystone turns those habits into explicit skills:

| You need... | Use... |
|---|---|
| understand a repository or gather project-specific evidence before a decision | `context-survey` |
| shape a product initiative's behavior, UX, copy, architecture, or scope | `product-planning` |
| turn approved project direction into implementation-ready work | `task-creation` |
| make an integrated project change with project-specific proof | `implementation` |
| improve project structure without intended behavior changes | `refactoring` |
| reproduce, isolate, and explain a project bug or regression before fixing | `root-cause-analysis` |
| review a project diff, branch, PR, or readiness decision read-only | `change-review` |
| explicitly finalize completed project work: commit, push, prepare or create a PR, merge, tag, package, publish, release, deploy, perform a repository handoff, or perform destructive cleanup | `shipping` |
| audit repository health, tooling, packaging, architecture, or maintenance risk | `project-audit` |

There is no central routing skill. The host discovers the right Keystone skill from the user's prompt or the user invokes the matching slash command directly.

## Migrate from `/keystone` to direct skills

Keystone 2.0 removes the old `/keystone` entrypoint. Use the matching public skill directly instead:

```text
/context-survey inspect or summarize existing code
/product-planning shape product, UX, scope, or technical direction
/task-creation turn approved direction into implementation-ready tasks
/implementation make scoped code, content, config, or documentation changes
/refactoring improve structure without intended behavior changes
/root-cause-analysis reproduce and explain bugs before fixing
/change-review review a diff, branch, PR, or regression risk read-only
/shipping explicitly commit, push, prepare or create a PR, merge, tag, package, publish, release, deploy, perform a repository handoff, or perform destructive cleanup
/project-audit audit repository, tooling, package health, or maintenance risk
```

Natural-language requests still work when the host supports skill discovery; the slash commands are the explicit migration path from `/keystone`.

## Install

### Pi

```bash
pi install npm:@static-var/keystone
```

Then invoke a public skill by name, or ask naturally and let Pi's skill discovery choose:

```text
/context-survey summarize the current package layout and risks
/implementation update the docs to match the approved spec
/change-review review the current branch for regressions
```

Optional Pi subagents:

```bash
pi install npm:@tintinweb/pi-subagents
```

Keystone may use subagent tools only when the active Pi tool schema exposes them. It does not assume named roles, model selection, thinking controls, or profile support.

### Claude Code

```text
/plugin marketplace add static-var/Keystone
/plugin install keystone@keystone
```

Invoke the installed public skills from Claude Code's plugin surface, for example `context-survey`, `implementation`, or `shipping`.

### Codex

```bash
codex plugin marketplace add static-var/Keystone --ref main
codex plugin add keystone --marketplace keystone
```

Then ask Codex for the workflow phase you need or invoke the installed Keystone skill from your Codex surface.

## How to use it

Ask for the phase you want in normal language:

```text
Survey the repository and explain what has to change before the package can ship.
```

```text
Turn this approved product spec into implementation-ready tasks with checks.
```

```text
Refactor the duplicated parsing logic without changing behavior.
```

```text
Diagnose why the release workflow fails and identify the smallest supported fix path.
```

```text
Review the current branch for blockers, regressions, and packaging leaks.
```

```text
Ship this completed change: verify evidence, prepare the commit summary, and hand off the PR notes.
```

Keystone skills can hand off when the work changes shape. For example, `root-cause-analysis` may hand off to `implementation` after evidence supports a fix path, and `change-review` may hand off findings to `refactoring` or `implementation`. Handoffs use a shared packet so the next skill receives the goal, evidence, files, risks, and next check. A handoff to `shipping` carries authorization in the canonical packet's `evidence` field as the user's explicit delivery request and action set.

## Artifact defaults

Keystone writes durable planning artifacts only when the workflow calls for them:

```text
docs/keystone/specs/YYYY-MM-DD-<slug>.md      # product-planning, after user approval
docs/keystone/tasks/YYYY-MM-DD-<slug>.md      # task-creation
docs/keystone/refactors/YYYY-MM-DD-<slug>.md  # large or cross-cutting refactoring
```

Before a plan is approved, `product-planning` works in conversation and asks focused questions instead of creating a spec file. `task-creation` keeps 1–5 top-level slices in conversation and writes 6 or more to its default artifact path; explicit chat-only or save requests override that threshold.

## Explicit-only shipping

`shipping` is explicit-only. Keystone does not commit, push, prepare or create a PR, merge, tag, package, publish, release, deploy, perform a repository handoff, or perform destructive cleanup just because implementation or review finished.

Ask for those actions directly, and Keystone will require proof and review evidence unless you explicitly waive them.

## Shared gates and standards

Keystone's public skills share internal gates and doctrine:

- **checkpoint** — make the next action or stopping point explicit
- **isolation** — check branch, worktree, scope, and dirty state before mutation
- **red** — establish a failing check or reproduction when practical
- **proof** — verify claims with evidence before success reports
- **review** — keep critique separate from fixing
- **ship** — confirm completed work is ready for handoff or delivery
- **engineering standards** — language-agnostic guidance for ownership, boundaries, state, abstractions, duplication, and maintainability

Gates are internal shared contracts, not public skills or commands.

## Project status

- npm package: `@static-var/keystone`
- public skills: `context-survey`, `product-planning`, `task-creation`, `implementation`, `refactoring`, `root-cause-analysis`, `change-review`, `shipping`, `project-audit`
- distribution: one complete Keystone package containing all nine skills and one shared gate tree
- license: MIT
- supported surfaces: Pi, Claude Code, Codex

For architecture, packaging, validation, and maintainer commands, read [`HOW_IT_WORKS.md`](HOW_IT_WORKS.md).

Invocation fixtures exercise all nine descriptions, ambiguous boundaries, and prompts that should select no Keystone skill. They validate the evaluation corpus, not model behavior. Before release, run the exported corpus against every supported host being claimed and record its selections:

```bash
python3 scripts/export-invocation-eval.py
```
