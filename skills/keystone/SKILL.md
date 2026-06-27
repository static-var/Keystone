---
name: keystone
description: Use when the user invokes /keystone or asks Keystone to route product, research, writing, UI, design, planning, implementation, debugging, review, shipping, or health work through its canonical orchestrator.
---

# Keystone

Keystone is a router/orchestrator skill. It selects the right internal module for the user's current request, carries handoffs between modules, and keeps only one public entrypoint: `/keystone`.

## Routing rule

Load exactly one primary module for the current task. Load gates or helper modules only when the primary module explicitly needs them. Do not expose internal modules as public slash commands. Actively route the work: name the selected module, preserve the current handoff packet, and state the next gate or check before taking irreversible action.

## Orchestration sequences

Use these common paths unless the user's immediate next action clearly points elsewhere:

- Product or feature work: `research -> shape -> breakdown -> build -> review -> ship`.
- Existing plan or approved design: `breakdown -> build -> review -> ship`.
- Direct implementation request: `build -> review -> ship`, loading `breakdown` first only when execution order or verification is unclear.
- Debug loop: `debug -> build -> proof gate -> review`; return to `debug` if proof fails or new symptoms appear.
- Health finding that needs repair: `health -> build` for contained fixes, or `health -> review` when the finding needs independent validation before mutation.

Do not add these as shipped modules; they are routing sequences over the existing nine modules.

## Handoff packet contract

Whenever one module hands work to another, carry a concise packet:

- `source module`: module producing the handoff
- `target module`: module to load next
- `goal`: one-sentence outcome for the next module
- `evidence`: facts, command output, user decisions, or citations already established
- `files`: relevant paths and whether they are read-only, mutable, or protected
- `risks`: known uncertainty, skipped checks, safety constraints, or rollback concerns
- `next check`: the gate, command, question, or review the target should run first

If the user overrides a gate, review, or sequence step, record the explicit override in the packet with the risk accepted. Never silently bypass hard safety constraints such as protected files, secret handling, isolation requirements, destructive operations, or policy restrictions; stop and ask or refuse as appropriate.

## Re-entry contract

When a module temporarily routes to another module and then resumes, the returning module must receive the handoff packet plus the result.

- Build -> Debug -> Build: carry the failing symptom, reproduction command, suspected root cause, files inspected, fix recommendation, and proof command. On return to Build, rerun isolation if mutation scope changed, rerun proof for the original symptom, and rerun review if the fix touches behavior, public API, security, data, or release surfaces.
- Build -> Research/Shape/Breakdown -> Build: carry the clarified decision or plan delta. On return, rerun the relevant Build preflight only for changed scope; do not redo unchanged gates without reason.
- Review -> Debug/Build -> Review: carry review findings and changed files. On return, review the addressed findings and any newly touched risk area.
- Health -> Build/Review: carry health evidence, severity, and recommended first check. Build may fix only contained, well-evidenced issues; uncertain or broad health findings go to Review first.

## Subagents and reasoning

When a module may delegate work, consult `modules/helpers/subagents.md` for host capability, safe delegation rules, and the recommended reasoning level for each Keystone module. If the host cannot enforce per-subagent reasoning, include the desired level in the subagent prompt or work inline.

## Routing table

| User intent | Primary module |
|---|---|
| Choose the right Keystone path, classify intent, resolve module ambiguity | `modules/router.md` |
| Read, inspect, summarize, extract, research, compare sources, investigate options | `modules/research.md` |
| Draft, rewrite, UI/UX, visual direction, product decisions, architecture, feature scope | `modules/shape.md` |
| Breakdown approved design into executable tasks and verification steps | `modules/breakdown.md` |
| Implement or change files/code/content | `modules/build.md` |
| Diagnose failures, failing behavior, errors, bug reports, regressions, unexpected behavior | `modules/debug.md` |
| Review work without changing it | `modules/review.md` |
| Finalize completed work for delivery or integration | `modules/ship.md` |
| Agent/tooling health, repository condition, skill drift, context rot, risks | `modules/health.md` |

## Ambiguity rule

If several modules could apply, choose the module matching the next irreversible action. If still ambiguous, ask one concise clarifying question before loading a primary module.
