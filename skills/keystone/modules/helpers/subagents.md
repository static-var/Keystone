# Keystone Subagents and Reasoning Helper

## Purpose
Teach Keystone when subagents can be used, which hosts support them, and what reasoning level each Keystone module should prefer.

This helper is advisory. Host capability wins over Keystone preference. If the current harness cannot set reasoning per subagent, encode the desired reasoning in the subagent prompt or do the work inline.

## Delegation rule
Use subagents only when the task has a clear boundary and a useful handoff artifact.

Good delegation targets:
- read-only reconnaissance
- independent implementation slices
- focused debugging/root-cause analysis
- read-only review
- documentation/copy drafting

Do not delegate when:
- the task needs tight conversational clarification
- one agent must continuously coordinate shared mutable state
- the host cannot preserve enough context for safe handoff
- the subagent would need secrets or permissions the parent should not share

## Host capability matrix

| Harness | Subagents | Per-subagent reasoning/effort | How to configure | Keystone policy |
|---|---:|---:|---|---|
| Pi coding agent with `pi-subagents` | yes | yes | `.pi/agents/<name>.md` frontmatter `model`, `thinking`, `profile`, or `Agent({ subagent_type, thinking, model, profile })` | Use native roles; prefer role defaults unless Keystone needs a one-off override. |
| Claude Code | yes | partial | `.claude/agents/<name>.md` supports subagent config and `model`; built-in Explore accepts quick/medium/very-thorough style detail, but custom agents do not expose a general reasoning knob | Use `model` plus explicit prompt instructions; use built-in Explore detail when applicable. |
| Codex CLI/app | unclear/host-dependent | partial/global | known global config includes `model_reasoning_effort`; no stable per-subagent effort schema confirmed | Treat Keystone reasoning as advisory text unless the active Codex host exposes a per-agent effort control. |
| T3 Code | not confirmed | not confirmed | no confirmed public/local schema | Treat as unsupported; run inline or through the underlying Claude/Codex/OpenCode provider if available. |
| OpenCode | yes | partial/provider-dependent | agent config supports `mode: "subagent"`, `model`, and provider-specific `variant`; no universal reasoning field is confirmed | Use subagent mode; map Keystone reasoning to model/variant only where the provider exposes effort variants, otherwise write the desired reasoning in the prompt. |
| GitHub Copilot / VS Code | yes | partial | `.github/agents/*.agent.md` supports `model`, `agents`, `user-invocable`, `disable-model-invocation`; no general reasoning knob found | Use custom agents and model choice; put reasoning expectation in the agent prompt. |

## Canonical reasoning scale

Keystone uses this host-neutral scale:

| Level | Use for |
|---|---|
| `off` | deterministic formatting, mechanical edits, no reasoning needed |
| `minimal` | tiny lookups, simple classification, trivial copy changes |
| `low` | ordinary reading, straightforward writing, small scoped tasks |
| `medium` | normal implementation, UI decisions, moderate research |
| `high` | architecture, debugging, review, planning, ambiguous tradeoffs |
| `xhigh` | hard root-cause analysis, security-sensitive review, major design decisions |

If a host uses another vocabulary, map to the nearest equivalent. If no setting exists, write the desired level into the prompt, for example: "Use high reasoning; explore alternatives before deciding."

## Keystone module defaults

| Keystone file | Preferred role | Default reasoning | Escalate when |
|---|---|---:|---|
| `modules/router.md` | none or lightweight classifier | `low` | request is ambiguous across several irreversible actions |
| `modules/read.md` | scout/read-only explorer | `low` | repository is large or source relationships are unclear (`medium`) |
| `modules/research.md` | scout or oracle | `medium` | claims affect architecture, market, safety, or release decisions (`high`) |
| `modules/write.md` | writer | `low` | copy depends on complex positioning, legal, or technical accuracy (`medium`) |
| `modules/ui.md` | UI/design reviewer or worker | `medium` | visual system, accessibility, or multi-screen flows are involved (`high`) |
| `modules/design.md` | oracle for second opinion | `high` | large architecture/product bets or irreversible scope decisions (`xhigh`) |
| `modules/breakdown.md` | planner plus reviewer | `high` | plan spans multiple independent agents or risky sequencing (`xhigh`) |
| `modules/build.md` | worker | `medium` | concurrency, migrations, broad refactors, or unfamiliar stack (`high`) |
| `modules/debug.md` | oracle/root-cause investigator | `high` | intermittent, cross-system, performance, or data-loss failures (`xhigh`) |
| `modules/review.md` | reviewer/read-only | `high` | security, release, data migration, or public API review (`xhigh`) |
| `modules/ship.md` | ship coordinator | `medium` | release has unresolved risk or multi-host packaging (`high`) |
| `modules/health.md` | scout plus reviewer | `medium` | broad repository/tooling drift or release readiness audit (`high`) |
| `modules/skill-engineering.md` | worker plus reviewer | `high` | changing routing contracts, public entrypoint, or package semantics (`xhigh`) |
| `modules/gates/*.md` | none | `low` | evidence is contradictory or safety-critical (`medium`) |

## Pi role mapping

When Pi subagents are available, use the narrowest role and usually keep its configured defaults:

| Need | Pi role | Typical thinking |
|---|---|---:|
| codebase exploration | `scout` | `low` |
| implementation | `worker` | `medium` |
| code/spec review | `reviewer` | `high` |
| architecture/root-cause second opinion | `oracle` | `high` or `xhigh` |
| docs/copy | `writer` | `low` |

Only override `thinking` when the module table says to escalate or de-escalate.

## Safe parallel work pattern

1. `breakdown` identifies independent tasks and their verification commands.
2. `build` passes `gates/isolation.md` before any mutation.
3. If the host supports isolated worktrees, each worker gets a separate worktree or host-isolated workspace.
4. Each worker reports files changed, tests run, and concerns.
5. `review` runs as read-only, preferably in a separate reviewer subagent.
6. `ship` finalizes only after proof and review gates pass.

## Prompt contract for delegated work

Every subagent prompt should include:

- exact task scope
- files or areas allowed to change/read
- protected files
- expected output artifact or report
- reasoning level requested if the host cannot enforce it
- verification command expected
- instruction not to broaden scope

For read-only subagents, explicitly say: "Do not edit files." For review subagents, explicitly say: "Return findings only; do not fix." 
