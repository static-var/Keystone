# Keystone

<p align="center">
  <img src="assets/brand/keystone-logo.svg" alt="Keystone" width="360">
</p>

<p align="center">
  <a href="https://www.npmjs.com/package/@static-var/keystone"><img alt="npm" src="https://img.shields.io/npm/v/%40static-var%2Fkeystone"></a>
  <a href="https://github.com/static-var/Keystone/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/static-var/Keystone/actions/workflows/ci.yml/badge.svg"></a>
  <a href="https://github.com/static-var/Keystone/blob/main/LICENSE"><img alt="License: MIT" src="https://img.shields.io/npm/l/%40static-var%2Fkeystone"></a>
  <a href="https://skills.sh/static-var/keystone"><img alt="skills.sh" src="https://img.shields.io/badge/skills.sh-keystone-0f766e"></a>
</p>

> Proactive workflow skills for disciplined AI work: use the right phase, keep boundaries clear, and prove the result.

Keystone is a package of model-discoverable workflow skills for coding agents. Instead of sending every request through a single router, Keystone exposes the phases agents need for real work: survey, plan, break down, implement, refactor, diagnose, review, ship, and audit.

Use Keystone when you want an agent to move deliberately: gather evidence before decisions, mutate only after isolation checks, separate review from fixing, and require proof before success claims.

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
| inspect, research, inventory, compare, or answer “what is true here?” | `context-survey` |
| shape product behavior, UX, copy, technical direction, architecture, or scope | `product-planning` |
| turn approved direction into tasks, tickets, milestones, or handoffs | `task-creation` |
| make scoped code, content, config, or documentation changes | `implementation` |
| improve structure without intended behavior changes | `refactoring` |
| reproduce, isolate, and explain a bug or failure before fixing | `root-cause-analysis` |
| review a diff, branch, PR, or change read-only | `change-review` |
| explicitly finalize completed work: commit, PR, release, publish, package, or hand off | `shipping` |
| audit repository, tooling, package health, architecture, or maintenance risk | `project-audit` |

There is no central routing skill. The host discovers the right Keystone skill from the user's prompt or the user invokes the matching slash command directly.

## Install

### skills.sh / Agent Skills hosts

```bash
npx skills add static-var/keystone --list
npx skills add static-var/keystone
```

Keystone generates nine self-contained Agent Skills under:

```text
.agents/skills/<skill-name>/
```

Each generated directory includes the skill and its local `_shared/` references, so it can be installed or copied individually. Agent Skills-compatible hosts include OpenCode, GitHub Copilot, and VS Code skill directories. Install all skills or select individual skills through skills.sh.

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

Keystone skills can hand off when the work changes shape. For example, `root-cause-analysis` may hand off to `implementation` after evidence supports a fix path, and `change-review` may hand off findings to `refactoring` or `implementation`. Handoffs use a shared packet so the next skill receives the goal, evidence, files, risks, and next check.

## Artifact defaults

Keystone writes durable planning artifacts only when the workflow calls for them:

```text
docs/keystone/specs/YYYY-MM-DD-<slug>.md      # product-planning, after user approval
docs/keystone/tasks/YYYY-MM-DD-<slug>.md      # task-creation
docs/keystone/refactors/YYYY-MM-DD-<slug>.md  # large or cross-cutting refactoring
```

Before a plan is approved, `product-planning` works in conversation and asks focused questions instead of creating a spec file.

## Explicit-only shipping

`shipping` is explicit-only. Keystone does not commit, open PRs, merge, tag, publish, release, deploy, perform destructive cleanup, or create external side effects just because implementation or review finished.

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
- license: MIT
- supported surfaces: Pi, skills.sh Agent Skills, Claude Code, Codex, OpenCode, GitHub Copilot / VS Code-compatible hosts

For architecture, packaging, validation, and maintainer commands, read [`HOW_IT_WORKS.md`](HOW_IT_WORKS.md).

Invocation fixtures exercise all nine descriptions, ambiguous boundaries, and prompts that should select no Keystone skill. They validate the evaluation corpus, not model behavior. Before release, run the exported corpus against every supported host being claimed and record its selections:

```bash
python3 scripts/export-invocation-eval.py
```
