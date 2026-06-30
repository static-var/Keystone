# Keystone Shape Module

## Core principle
Shape is a specification algorithm: turn an unclear intent into exact behavior, constraints, tradeoffs, and acceptance criteria before anyone builds. It decides what should be true, not whether code is complete.

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
- product behavior and UX states, including happy, empty, loading/pending, error/failure, and edge/constraint states where relevant;
- copy or content direction when user-facing text matters;
- architecture and scope tradeoffs at the level needed for planning, not implementation;
- alternatives considered and why one direction is preferred;
- acceptance criteria and non-goals;
- recommended next module (`breakdown`, `build`, `review`, `research`) or `none` if no Keystone handoff is warranted.

## Modes
- **Product shape:** specify the user job, trigger, actor permissions, core flow, business rules, constraints, success metrics, non-goals, and acceptance criteria.
- **UX/UI shape:** specify layout hierarchy, navigation, interaction model, responsiveness, accessibility, visual constraints, and the 5-state UX checklist: happy, empty, loading/pending, error/failure, edge/constraint.
- **Copy shape:** specify audience, message hierarchy, claims, tone, CTA, labels, empty/error text, and prohibited vague claims.
- **Technical shape:** specify boundary placement, API granularity, data flow, state ownership, dependency direction, persistence/integration seams, and architectural tradeoffs without writing code.
- **Alternative exploration:** present multiple viable directions before choosing or asking the user to choose.

## Process
1. Classify the request into one or more modes: product, UX/UI, copy, technical, or alternatives.
2. Identify the goal, primary user/audience, job-to-be-done, context of use, and success criteria.
3. Inspect existing product patterns, domain language, and provided material before inventing new conventions.
4. Convert intent into exact rules:
   - Product: actor, trigger, preconditions, action, result, permissions, limits, and measurable success.
   - UX/UI: screen/region hierarchy, controls, transitions, accessibility behavior, responsive behavior, and 5-state UX checklist.
   - Copy: exact headline/body/CTA/error text or content rules, with claims grounded in known facts.
   - Technical: components/modules involved, ownership boundaries, contracts, data flow, failure handling, migration or rollout constraints.
5. Apply technical shaping heuristics when architecture matters:
   - **Boundary placement:** put boundaries where ownership, volatility, testability, or external systems change; do not split stable one-step logic.
   - **API granularity:** prefer operations that match caller intent; avoid both chatty micro-methods and god endpoints that hide unrelated behavior.
   - **Data flow:** name source of truth, state transitions, sync/async edges, validation points, and where errors surface.
   - **Architectural tradeoffs:** state what becomes simpler, harder, slower, safer, more testable, or more coupled.
6. Ban fluffy terms unless translated to behavior. Words like “modern,” “clean,” “intuitive,” “delightful,” “seamless,” or “user-friendly” must become observable rules.
7. Offer alternatives when the direction is not obvious. Include the “do nothing / decide later” option if legitimate.
8. Convert the chosen direction into acceptance criteria that can be implemented and reviewed.
9. Stop at the spec boundary. If the user asks for design plus build, finish Shape with the spec and recommended handoff to `build`; do not implement code.

## Subagents and reasoning
Use subagents for bounded alternatives, critique, or parallel concepts when the active host exposes safe delegation. Use lightweight analysis for narrow copy/behavior edits and deeper analysis for multi-screen flows, accessibility-sensitive experiences, design-system impact, pricing/positioning, architecture boundaries, or major scope decisions. When delegation is available, encode required evidence depth, constraints, and risk standard in the prompt. Subagents should produce options or critique, not unrequested implementation.

## Hard rules
- Shape is not build: do not edit production code or runtime behavior.
- If the user asks for design and implementation together, Shape stops after the specification and hands off to `build`.
- Ground claims in research or existing product evidence; call `research` when facts are missing.
- Always identify user/audience and success criteria for product-facing work.
- Include acceptance criteria before handing off to implementation.
- Translate fluffy descriptors into exact behavior; otherwise remove them.
- Avoid action bias: if the best answer is “do nothing” or “decide later,” say so with criteria.

## Failure modes
- **Abstract advice:** principles without actors, states, rules, tradeoffs, or acceptance criteria.
- **Pretty but unusable:** visual ideas without behavior, states, or acceptance criteria.
- **Fluffy spec:** “modern/user-friendly” language without exact behavior.
- **Spec as proof:** implying a design solves the problem before implementation or validation.
- **Audience blur:** writing for everyone and satisfying no one.
- **Scope fog:** hiding hard tradeoffs until build time.
- **Premature code:** implementing while still deciding what should exist.

## Examples
Good product shape: “When a workspace has no projects, show an empty state with title ‘Create your first project,’ one-sentence explanation, primary ‘New project’ CTA, and no table chrome. Success: first project creation rate increases.”
Bad product shape: “Make the dashboard more useful and modern.”

Good UX/UI shape: “On save, disable the Save button, keep the form editable fields visible, show inline progress text ‘Saving…’, then restore focus to the first invalid field on failure.”
Bad UX/UI shape: “Use a clean, user-friendly save experience.”

Good copy shape: “CTA says ‘Start free trial’ because billing is not required; avoid ‘Buy now.’ Error text names the failed action and recovery: ‘We couldn’t send the invite. Check the email address and try again.’”
Bad copy shape: “Use friendly copy that reduces friction.”

Good technical shape: “Keep validation in the domain service because API and background import both need it; expose one `createInvite` operation that returns accepted, duplicate, or invalid-email outcomes.”
Bad technical shape: “Add a helper/manager layer so the architecture is scalable.”

Worked technical shape: “For export retries, keep the queue worker as the owner of retry state, expose `requestExport(accountId, format)` from the API, persist `pending|running|failed|ready` status in `exports`, and surface failures through the existing job status endpoint. Tradeoff: one extra status read, but retry policy stays out of controllers and can be tested without HTTP.”

## Output format
Always include goal, audience/user when relevant, mode(s), acceptance criteria, and recommended next step. Include UX/copy/technical/alternatives sections only when they change the decision; omit empty or irrelevant headings.

```markdown
## Shaped direction
Goal: ...
Audience/user: ...
Mode(s): product | UX/UI | copy | technical | alternatives

### Proposed behavior / experience
- Actor/trigger/preconditions: ...
- Rules/results: ...

### UX states and copy (when relevant)
- Happy: ...
- Empty: ...
- Loading/pending: ...
- Error/failure: ...
- Edge/constraint: ...
- Key copy: ...

### Technical shape (when relevant)
- Boundaries/API/data flow: ...
- Tradeoffs: ...

### Scope and tradeoffs
- In: ...
- Out: ...
- Tradeoffs: ...

### Alternatives considered (when relevant)
- Option A: ...
- Option B / do nothing: ...

### Acceptance criteria
- ...

### Recommended next step
Module or `none`, with rationale

### Checkpoint
Use the required fields from `gates/checkpoint.md`.

```
