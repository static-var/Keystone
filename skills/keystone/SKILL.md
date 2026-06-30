---
name: keystone
description: Use when the user invokes /keystone or explicitly asks Keystone to route work.
---

# Keystone

Keystone is a router/orchestrator skill. It selects the right internal module for the user's current request, carries handoffs between modules, and keeps only one public entrypoint: `/keystone`.

## Routing rule

Load exactly one primary module for the current task. Load gates or helper modules only when the primary module explicitly needs them. Do not expose internal modules as public slash commands. Actively route the work: name the selected module, preserve the current handoff packet, and state the next gate or check before taking irreversible action.

Every Keystone module completion must pass `modules/gates/checkpoint.md` before a user-facing final response. The checkpoint decides whether Keystone continues now, asks the user, leaves a pending pointer, or stops because no handoff remains.

## Orchestration sequences

Use these common paths as navigation maps plus checkpoint defaults. Load only the next primary module needed now unless the user's immediate next action clearly points elsewhere. When a module completes and the next step is required by the sequence or a gate, continue to that module in the same session when safe; otherwise ask or leave a pending pointer:

- Product or feature work: `research -> shape -> breakdown -> build -> review -> ship`.
- Existing plan or approved design: `breakdown -> build -> review -> ship`.
- Direct implementation request: `build -> review -> ship`, loading `breakdown` first only when execution order or verification is unclear.
- Bug fix: `debug -> build -> proof gate -> review -> ship`.
- Debug loop: `debug -> build -> proof gate -> review`; return to `debug` if proof fails or new symptoms appear.
- Health finding that needs repair: `health -> build` for contained fixes, or `health -> review` when the finding needs independent validation before mutation.

Do not add these as shipped modules; they are routing sequences over the existing nine modules.

## Checkpoint gate

Before any final answer, load `modules/gates/checkpoint.md`; it is the single source of truth for checkpoint fields and actions. If the checkpoint action is `continue now`, load the next primary module instead of ending the turn. If Keystone cannot continue safely, the final answer must make the next event explicit with a question or pending review/ship pointer. Never end a build/change with only “done,” “implemented,” or a buried “Next” line when review or ship remains.

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

Use subagents when the active host exposes them and delegation has a clear boundary, useful artifact, and lower coordination cost than doing the work inline.

For Pi, Keystone is tuned for `@tintinweb/pi-subagents` (https://github.com/tintinweb/pi-subagents). Install it with `pi install npm:@tintinweb/pi-subagents`. When available, use `Agent` for bounded work, `get_subagent_result` for background results, and `steer_subagent` only to redirect live work. Do not assume named roles, model selection, or thinking controls; use only the fields exposed by the active tool schema.

Keep subagents read-only unless mutation is explicitly requested. Use background/parallel agents only for independent tasks with no shared mutable files. Treat subagent output as evidence, not truth; the parent must verify before acting. If the host cannot provide subagents or explicit reasoning controls, encode the desired analysis depth in the prompt or work inline. Do not invent unsupported subagent tools.

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
