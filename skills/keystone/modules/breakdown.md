# Keystone Breakdown Module

## Core principle
Breakdown turns a goal into sequenced, reviewable vertical slices of work.

A good breakdown makes implementation easier because every slice has a visible result, clear constraints, and a verification path. It makes review easier because reviewers can compare changes against stated goals, requirements, risks, and acceptance checks.

Breakdown is planning, not execution. A plan is not proof; only inspected changes, tests, demos, or other evidence prove completion.

## Load when
Use this module when the user asks to:

- break down a feature, fix, refactor, migration, tool, system, or project
- produce milestones, implementation steps, tickets, issues, vertical slices, or phases
- decide sequencing, dependencies, iterations, scope cuts, or parallelization
- turn an ambiguous goal into implementable work
- prepare work for coding agents, reviewers, or subagents
- plan greenfield architecture before implementation
- split a large task into reviewable chunks without exposing `/plan`

Also load when implementation is requested but the goal is broad enough that coding immediately would hide major product, architecture, or sequencing decisions.

## Not for
Do not use Breakdown for:

- implementation, file edits, refactors, migrations, or generated code
- debugging a known failure; use `debug` first, then return to Breakdown if a repair plan is needed
- research-only tasks; use `research` first when facts are missing
- copy/design shaping as the primary work; use `shape` first when output is prose, UX, or design direction
- final verification, release readiness, or completion claims; use `review`, `health`, or `ship`
- renaming this module to `plan`, creating `/plan`, or exposing the internal planner name as a public command

## Outcome contract
A Breakdown output must include:

1. Goal: the intended outcome in one or two sentences.
2. Context inspected: files, docs, requirements, or assumptions used.
3. Requirements inventory: critical requirements, non-functional requirements, good-to-haves, constraints, and open questions.
4. Stack and architecture context: current or proposed technologies, boundaries, integrations, and limitations.
5. Iteration layering: iteration 1, iteration 2, iteration 3, etc., with explicit scope cuts.
6. Vertical slices: ordered work items that each deliver an end-to-end outcome.
7. Verification gates: how each slice can be tested, reviewed, or demonstrated.
8. Risks and dependencies: what can block, invalidate, or reorder the work.
9. Handoff: recommended next primary module and any subagent/reasoning suggestions.

If information is missing, state the assumption or ask the smallest set of questions required to avoid a bad plan.

## Modes

### Feature breakdown
Use for new capabilities in an existing product. Focus on the user/operator goal, existing entry points, data paths, APIs, UI surfaces, tests, deployment constraints, and the smallest end-to-end slice that proves the feature path. Add progressive enrichment after the core loop works. Avoid horizontal buckets like "database", "backend", "frontend", and "tests" unless they are nested inside a vertical slice.

### Greenfield architecture breakdown
Use for new projects, tools, services, apps, packages, or substantial standalone systems. Start architecture-first: name the primary users, runtime, language, framework, hosting, storage, auth, observability, CI, packaging constraints, system boundaries, and integration points. Iteration 1 should prove the architecture can run, test, deploy, and support one meaningful vertical path, not merely create folders.

### Refactor/migration breakdown
Use when behavior should remain stable while internals change. Focus on the current behavior contract, compatibility expectations, affected surfaces, consumers, migration seams, adapters, flags, dual-run paths, rollback strategy, observability, and characterization tests. Prefer strangler-style or seam-first slices over broad rewrites.

### Subagent-parallel breakdown
Use when independent workstreams can proceed safely in isolated workspaces. Build the dependency graph before delegation. Name shared files, interfaces, merge-risk hotspots, delegation purpose, desired reasoning intensity, context packets, expected artifacts, integration order, and review checkpoints. Only parallelize slices that can be verified independently or integrated behind a clear contract.

## Process

1. Identify the goal.
   - Restate the desired end state, not just the requested activity.
   - Identify who benefits and what observable change proves value.
   - If the goal is unclear and cannot be inferred from context, ask one focused question.
2. Inspect before asking broad questions.
   - Read relevant files, docs, issues, architecture notes, tests, package manifests, and existing modules when available.
   - Use `research` for unfamiliar libraries, external constraints, or repository-wide discovery.
   - Ask clarifying questions only when inspection cannot resolve a decision that materially changes the breakdown.
3. Build the requirements inventory.
   - Separate critical requirements from non-functional requirements and good-to-haves.
   - Capture explicit user constraints, protected files, deadlines, compatibility needs, and review expectations.
   - Mark assumptions and unknowns instead of silently inventing requirements.
4. Identify stack and constraints.
   - Note languages, frameworks, package managers, deployment targets, test tooling, persistence, auth, APIs, and platform limits.
   - For greenfield work, propose architecture choices only after naming tradeoffs and constraints.
   - For existing systems, prefer the established stack unless the goal requires a change.
5. Choose iteration layers.
   - Define iteration 1 as the smallest coherent outcome that proves the path.
   - Define later iterations as progressively richer outcomes, not random leftovers.
   - Make explicit what is intentionally deferred.
6. Slice vertically.
   - Each slice should cross needed layers to produce a reviewable result.
   - Include data/model/API/UI/test/docs work inside the slice when needed for that result.
   - Avoid phase plans that finish entire subsystems before any end-to-end value appears.
7. Add verification gates.
   - Give each slice an acceptance check, test command, manual review path, or demo criterion.
   - Include regression checks for migrations and refactors.
   - State when review should happen and what reviewers should inspect.
8. Prepare the handoff.
   - Recommend the next Keystone module.
   - Identify subagent opportunities, required context, and reasoning level.
   - Call out risks, dependencies, and open questions that should block implementation if unresolved.

## Requirements inventory
Use this inventory before sequencing work:

- Goal: what outcome the user wants.
- Critical requirements: must be true or the work fails.
- Non-functional requirements: performance, security, reliability, accessibility, privacy, maintainability, observability, compatibility, cost, release, and operational concerns.
- Good-to-haves: valuable but deferrable enhancements.
- Constraints: protected files, APIs, tech stack, deadlines, repo conventions, deployment targets, team/process limits.
- Current state: what exists now, with file/source references when available.
- Unknowns: decisions or facts still unresolved.
- Assumptions: temporary beliefs used to proceed.

When requirements conflict, surface the conflict before writing slices.

## Iteration layering
Iteration layers should describe increasing confidence and capability:

- Iteration 1: skeleton or core path. One thin, end-to-end result that validates the architecture, integration point, or user journey.
- Iteration 2: completeness and resilience. Add common cases, validation, error states, compatibility, and tests around the proven path.
- Iteration 3: polish and scale. Add edge cases, performance, accessibility, observability, docs, migration cleanup, and nice-to-haves.
- Later iterations: optional expansion, hardening, automation, or product refinements.

For greenfield projects, iteration 1 must include a runnable or executable foundation plus one meaningful vertical path. For migrations, iteration 1 should establish safety: characterization checks, seams, adapters, or observability before broad movement.

## Task quality bar
Each task or slice must have:

- a name that describes the delivered outcome
- user/operator/developer value
- inputs and dependencies
- files or areas likely involved, when known
- exact acceptance criteria
- verification method
- rollback or safety note when risk is non-trivial
- review focus: what a reviewer should inspect

A weak task says "build backend" or "add tests". A strong slice says "Persist saved searches end-to-end behind the existing search UI, with API validation, storage migration, and regression coverage for loading saved searches."

## Subagents and reasoning
Default reasoning: `high`.

Use subagents when planning benefits from independent context gathering, critique, or parallel workstream design:

- read-only research on separate code areas, external APIs, or prior art
- architecture critique for greenfield foundations and migrations
- risk critique for security, data loss, compatibility, or release plans
- implementation delegation only after slices are independent and interfaces are stable

For each proposed delegation, specify purpose, desired reasoning intensity, context packet, expected output artifact, files or areas off limits, and integration/review checkpoint. Do not use subagents to bypass ambiguity. Resolve shared interfaces and sequencing first.

## Hard rules

- No implementation under Breakdown.
- No file mutation unless the user explicitly requested a planning artifact and the artifact itself is in scope.
- Do not rename `breakdown` to `plan`.
- Do not expose `/plan`.
- Do not claim the plan proves completion.
- Do not skip goal identification.
- Do not ask broad clarifying questions before inspecting available context.
- Do not produce horizontal-only plans.
- Do not hide assumptions, unresolved questions, or conflicts.
- Do not route risky plans directly to `build` without verification gates and review points.

## Failure modes

- Activity plan: lists actions but never states the outcome.
- Horizontal buckets: separates backend/frontend/tests so no slice is independently valuable.
- Big-bang architecture: designs everything before proving one runnable path.
- Faux certainty: treats assumptions as facts.
- Question spam: asks what inspection could answer.
- Implementation leak: starts coding, editing files, or choosing exact code structure beyond planning needs.
- Review-hostile output: lacks acceptance criteria, test commands, or reviewer focus.
- Parallelism theater: delegates coupled workstreams that collide on shared files or undefined interfaces.
- Plan-as-proof: reports success because a plan exists.

## Output format
Use this structure unless the user requested a different planning artifact:

```markdown
# Breakdown: <goal>

## Goal
<one or two sentences describing the desired outcome>

## Context inspected
- <files, docs, issues, sources, or "none available">

## Requirements inventory
### Critical requirements
- <must-have>

### Non-functional requirements
- <quality/operational constraint>

### Good-to-haves
- <deferrable enhancement>

### Stack and architecture context
- Stack: <technologies, frameworks, platforms, deployment targets>
- Boundaries: <modules, layers, services, UI/data/domain seams>
- Integrations: <APIs, persistence, queues, auth, payment, external systems>
- Limitations and constraints: <protected files, compatibility, process, deadline, cost, operational limits>

### Unknowns and assumptions
- Unknown: <question that matters>
- Assumption: <assumption used for this breakdown>

## Iteration layering
### Iteration 1: <core path / architecture skeleton / safety seam>
- Outcome: <reviewable result>
- Scope: <included>
- Deferred: <not included>

### Iteration 2: <complete common cases>
- Outcome: <reviewable result>
- Scope: <included>
- Deferred: <not included>

### Iteration 3: <hardening / polish / scale>
- Outcome: <reviewable result>
- Scope: <included>
- Deferred: <not included>

## Vertical slices
1. <slice name>
   - Value: <who benefits and how>
   - Work: <end-to-end changes at a planning level>
   - Dependencies: <prior slices or decisions>
   - Acceptance: <observable completion criteria>
   - Verification: <test/review/demo method>
   - Review focus: <what reviewers should inspect>

## Risks and dependencies
- <risk, impact, mitigation>

## Subagent opportunities
- <delegation purpose, desired reasoning intensity, context packet, expected artifact>

## Handoff
Next module: `<research|build|debug|review|health|ship|shape>` because <reason>.
```

Keep the output detailed enough to guide implementation and review, but short enough that each slice remains actionable.
