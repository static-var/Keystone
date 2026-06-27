# Keystone Shape Module

## Core principle
Shape decides what should be true before anyone builds it. Define the goal, audience, behavior, UX states, copy, constraints, alternatives, and acceptance criteria without claiming implementation is complete.

## Load when
Load when the user asks to draft, rewrite, design, spec, define product behavior, improve UI/UX, choose visual direction, name or explain a feature, make scope or architecture tradeoffs, prepare acceptance criteria, or turn research into an implementation-ready direction.

## Not for
- Writing implementation code or changing runtime behavior; hand off to `build`.
- Diagnosing failures; use `debug`.
- Broad repository health or release readiness; use `health` or `ship`.
- Inventing facts that should be researched first.
- Polishing completed work as shippable proof.

## Outcome contract
Deliver a shaped proposal that includes:
- goal, user/audience, and success criteria;
- product behavior and UX states, including empty/loading/error/edge states where relevant;
- copy or content direction when user-facing text matters;
- architecture and scope tradeoffs at the level needed for planning, not implementation;
- alternatives considered and why one direction is preferred;
- acceptance criteria and non-goals;
- recommended next module (`breakdown`, `build`, `review`, `research`, or no-op).

## Modes
- **Product shape:** define behavior, user journey, constraints, and acceptance criteria.
- **UX/UI shape:** describe layout, hierarchy, interaction states, accessibility, responsiveness, and visual direction.
- **Copy shape:** write or rewrite user-facing language with audience, tone, CTA, and information hierarchy.
- **Technical shape:** choose boundaries, APIs, data flow, or scope tradeoffs without coding.
- **Alternative exploration:** present multiple viable directions before choosing or asking the user to choose.

## Process
1. Identify the goal, primary user/audience, job-to-be-done, and context of use.
2. Inspect existing product patterns or provided material before inventing new conventions.
3. Define the desired behavior in user terms first; then note technical implications and scope boundaries.
4. Cover UX states: happy path, empty state, loading/pending, errors, permissions, edge cases, and recovery.
5. Draft copy when words affect comprehension or conversion; keep claims grounded in known facts.
6. Name architecture/scope tradeoffs: what becomes simpler, harder, delayed, or risky.
7. Offer alternatives when the direction is not obvious. Include the no-op option if it is legitimate.
8. Convert the chosen direction into acceptance criteria that can be implemented and reviewed.
9. Stop at the spec boundary unless the user explicitly asks to implement.

## Subagents and reasoning
Default reasoning: `medium`. Use writer, UI, design, or architecture subagents for bounded alternatives, critique, or parallel concepts. Use `high` for multi-screen flows, accessibility-sensitive experiences, design-system impact, pricing/positioning, architecture boundaries, or major scope decisions. Subagents should produce options or critique, not unrequested implementation.

## Hard rules
- Shape is not build: do not edit production code unless the user explicitly requested a design artifact file.
- Ground claims in research or existing product evidence; call `research` when facts are missing.
- Always identify user/audience and success criteria for product-facing work.
- Include acceptance criteria before handing off to implementation.
- Avoid no-op avoidance: if the best answer is “do nothing” or “decide later,” say so with criteria.

## Failure modes
- **Pretty but unusable:** visual ideas without behavior, states, or acceptance criteria.
- **Spec as proof:** implying a design solves the problem before implementation or validation.
- **Audience blur:** writing for everyone and satisfying no one.
- **Scope fog:** hiding hard tradeoffs until build time.
- **Premature code:** implementing while still deciding what should exist.

## Output format
```markdown
## Shaped direction
Goal: ...
Audience/user: ...

### Proposed behavior / experience
- ...

### UX states and copy
- Happy path: ...
- Empty/loading/error/edge: ...
- Key copy: ...

### Scope and tradeoffs
- In: ...
- Out: ...
- Tradeoffs: ...

### Alternatives considered
- Option A: ...
- Option B/no-op: ...

### Acceptance criteria
- ...

### Recommended next step
Module and rationale
```
