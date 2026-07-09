---
name: implementation
description: Use when the user asks to implement, add, change, edit, update, wire, migrate, fix after diagnosis, or execute approved scoped code/content/config/documentation changes.
---

# Implementation

## Core principle

Implementation changes through evidence, not vibes: isolate first, specify the next observable behavior, prove the test can fail, make the smallest correct change, then refactor without changing behavior.

Implementation is the mutation module. It may edit scoped project artifacts after the isolation gate passes, but it does not decide that work is shipped. Completion means "implemented with proof and handed to a change-review/shipping checkpoint," not finalized.

## Load when

Use Implementation when the user asks to:

- implement, create, edit, or wire behavior
- add a feature, screen, endpoint, command, migration, or integration
- refactor existing code while preserving behavior
- change architecture, module boundaries, interfaces, or contracts
- apply an approved plan from `task-creation`
- delegate independent implementation work when a subagent tool is available
- make focused content or configuration changes that require mutation

## Not for

Do not use Implementation for:

- routing unclear work: use `context-survey`
- context-surveying unknowns without mutation: use `context-survey`
- shaping requirements or acceptance criteria: use `product-planning`
- decomposing large work before implementation: use `task-creation`
- diagnosing a failure whose cause is unknown: use `root-cause-analysis`
- reviewing completed changes: use `change-review`
- releasing, merging, publishing, or finalizing: use `shipping`

## Outcome contract

Before Implementation exits, it must be able to report:

- isolation was checked before the first mutation via `../_shared/gates/isolation.md`
- the exact user scope and protected files were respected
- the intended behavior or refactor invariant is stated plainly
- tests, examples, or checks prove the change, or gaps are explicitly disclosed
- `../_shared/gates/red.md` passed for behavior changes
- `../_shared/gates/proof.md` passed before any success claim
- delegated work, if any, was verified by the parent before acceptance
- `../_shared/gates/checkpoint.md` decided the next required event

Implementation must not claim work is done because code "looks right." Proof and an explicit change-review/shipping checkpoint are required before completion claims.

## Modes

### TDD feature implementation

Use when adding or changing observable behavior.

Contract:

- define one behavior slice at a time
- write or identify the smallest test/check that should fail before the change
- run it and confirm the failure is meaningful, not caused by setup noise
- implement the smallest code that makes it pass
- run the focused check again
- run relevant regression checks
- refactor only while checks stay green

Load and pass `../_shared/gates/red.md` for the red signal or its explicit exception. Prefer checks that exercise real behavior over mocks, implementation details, or snapshots.

### Refactor

Use when preserving behavior while improving structure, names, duplication, readability, or boundaries.

Contract:

- name the behavior that must not change
- find existing tests or add characterization tests before edits when coverage is weak
- make small mechanical changes first
- keep public contracts stable unless the user requested a contract change
- run regression checks before and after meaningful refactor steps
- stop if behavior questions appear; route back to `product-planning` or `root-cause-analysis` as needed

A characterization test captures what the current system does before you change structure. It is not a claim that current behavior is ideal; it is a tripwire that prevents accidental behavior changes while refactoring. Write it around externally visible behavior, important edge cases, or bug-compatible outputs that must stay stable until the user approves a behavior change.

Concise example: before extracting invoice total formatting, add a test that `renderInvoiceSummary({ subtotal: 1000, discount: 125, currency: "USD" })` still returns `"Subtotal $10.00 · Discount $1.25 · Total $8.75"`; then refactor behind that externally visible output.

Refactoring is not a license to redesign everything nearby.

### Architecture-sensitive implementation

Use when the change affects boundaries, state management, cross-module dependencies, platform conventions, or long-lived maintainability.

Contract:

- identify the domain shape before choosing architecture
- choose the lightest architecture that fits the problem
- define contracts/interfaces only at real boundaries where they reduce coupling or clarify ownership
- keep domain rules separate from transport, UI, persistence, and framework glue
- use patterns only when they remove current pressure, not to decorate simple code
- validate observable maintainability with the pressure-test below

Architecture pressure-test:

- Does the architecture match domain complexity rather than a desire to sound senior?
- Is each module/class/function responsible for one understandable thing?
- Are domain concepts named in the user's language?
- Is state ownership explicit, with side effects isolated enough to test meaningful behavior?
- Would a developer know where to add the next similar behavior?
- Is the simplest path readable, or has simplicity become cleverness?
- Is duplication removed only after the repeated concept is real?
- Do patterns such as Strategy, Repository, Adapter, Observer, MVVM, MVI, or Clean Architecture relieve current pressure?
- **SOLID check:** one reason to change; known variation handled safely; substitutes honor contracts; callers avoid unused surface; high-level policies depend on stable abstractions only at real boundaries.
- Smell stop-list: god functions, vague managers/helpers, hidden control flow, stringly APIs, layer violations, speculative interfaces.

### Delegated/parallel implementation

Use when two or more implementation slices are independent enough to proceed without shared mutable state or ambiguous ownership.

Contract:

- split by outcome, not by vague activity
- pass each worker a narrow scope, files or directories, constraints, and completion criteria
- define contracts/interfaces before parallel work begins when slices must meet
- state what must not be edited
- require each worker to report files changed, checks run, and risks
- verify delegated work yourself before integrating or claiming completion
- reconcile overlaps deliberately; do not let workers race on the same files

Do not delegate fuzzy architecture judgment without a concrete interface or decision boundary.

Concise subagent brief template:

```markdown
Goal: one observable outcome
Scope: allowed files/directories
Do not edit: protected files/behaviors
Contract: interfaces, invariants, data shape, or acceptance criteria
Proof: required tests/checks/manual verification
Report: files changed, verification output, risks/gaps
```

## Process

1. Confirm scope.
   - Restate the requested mutation in one sentence.
   - Identify protected files and out-of-scope behavior.
   - If scope is unsafe or ambiguous, ask one focused question or route to `product-planning`.

2. Pass isolation before mutation.
   - Load/check `../_shared/gates/isolation.md`.
   - Know the workspace, branch/worktree state, and dirty files.
   - Stop if unrelated changes could be overwritten.

3. Choose the mode.

4. Define the next outcome.
   - Write the smallest observable behavior, invariant, or contract.
   - Avoid "make it better" as an implementation target.

5. Establish the signal before code.
   - For behavior changes, load and pass `../_shared/gates/red.md` before editing.
   - For refactors, establish characterization or regression coverage.

6. Implement the smallest correct slice.
   - Edit only files in scope.
   - Keep changes narrow and reversible.
   - Prefer clear names and direct control flow.
   - Do not invent broad architecture to satisfy a small behavior.

7. Green.
   - Run the focused test/check.
   - If it fails unexpectedly, use `root-cause-analysis`; do not stack guesses.

8. Refactor.
   - Remove duplication introduced by the slice.
   - Improve readability without broadening behavior.
   - Keep tests green after cleanup.

9. Regression check.
   - Load and pass `../_shared/gates/proof.md` against the intended outcome.

10. Early smell check.
   - Stop and simplify if the diff hits the architecture smell stop-list.

11. Architecture pressure-test.
   - For architecture-sensitive changes, answer the inline pressure-test and remove abstractions that do not survive it.

12. Checkpoint and handoff.
   - Load/check `../_shared/gates/checkpoint.md`.
   - Summarize changed files and behavior.
   - Include commands run and results.
   - Disclose unverified areas.
   - Decide whether `change-review` is required now, can be satisfied by self-review, or must be left as a pending review pointer.
   - If review is required and Keystone can safely continue, hand off to `change-review` before the final response. If not, ask the user or include the pending review pointer from `../_shared/gates/review.md`.

## Subagents and reasoning

Use deeper analysis when architecture boundaries are being changed, tests fail for unclear reasons, multiple agents must coordinate through contracts, data loss/security/billing/release/migration risk exists, or the user asks for broad refactoring or platform-specific architecture judgment. When delegation is available, encode required evidence depth and risk standard in the prompt.

Use read-only exploration subagents when independent inspection can reduce uncertainty without mutation. Use implementation subagents only when the user requested mutation, isolation has passed, allowed files are scoped, each slice can be verified independently, and file overlaps are prevented by ownership or explicit handoff.

A delegation brief must include:

- goal/outcome
- allowed files or directories
- forbidden files or behaviors
- relevant interfaces/contracts
- expected tests/checks
- report format for files changed, verification, and risks/gaps

Verify delegated work by:

- reading the diff, not just the report
- running or reviewing the reported checks
- checking contract compatibility between slices
- rejecting broad edits, invented abstractions, or unproved claims

## Hard rules

- Implementation must pass `../_shared/gates/isolation.md` before the first mutation.
- Implementation must not ship, merge, publish, release, or finalize work.
- Implementation must run the checkpoint gate before any final response.
- After mutation, Implementation must not stop at “implemented” when review remains; continue to `change-review` when safe or leave an explicit review prompt/pending pointer.
- Do not edit files outside the user's scope.
- Do not claim completion without proof or explicit disclosure of missing proof.
- Do not skip red/green/refactor for behavior changes unless there is a stated, practical reason and alternative proof plan.
- Do not use subagents as a way to avoid understanding the result.
- Do not introduce architecture that the current domain pressure does not justify.

## Failure modes

Watch for these and correct course:

- **Green-only development:** tests are added after implementation and never proven red.
- **Mock theater:** tests prove mocks were called, not that behavior works.
- **Scope creep:** nearby cleanup, README edits, scripts, or unrelated modules change without request.
- **Invented architecture:** factories, managers, providers, repositories, or layers appear without pressure.
- **Shallow abstraction:** a wrapper hides one call site and makes the code harder to follow.
- **Brittle hack:** timing sleeps, magic constants, global state, or special cases mask the real issue.
- **God function:** one routine owns validation, orchestration, persistence, formatting, and error policy.
- **Vague names:** `manager`, `helper`, `util`, or `common` hide responsibility instead of naming it.
- **Hidden control flow:** callbacks, observers, magic registration, or framework hooks make execution hard to trace without clear benefit.
- **Stringly API:** strings encode commands, states, fields, or permissions that should be typed, enumerated, or centralized.
- **Layer violation:** UI, transport, persistence, or framework code reaches across boundaries into another layer's policy.
- **Speculative interface:** abstraction exists for imagined future variants, not current pressure.
- **Ambiguous delegation:** workers receive goals like "improve this" without contracts or boundaries.
- **Unverified handoff:** delegated changes are accepted from a summary alone.
- **Finalization leak:** Implementation says work is shipped, merged, or ready for users instead of ready for change-review/shipping.
- **Lost next event:** Implementation ends with “done” or only a passive Next line while change-review, shipping, or a user approval is still required.

## Output format

When handing back from Implementation, respond with these sections, including `### Checkpoint`:

- `Summary`: what changed, in bullets
- `Files changed`: exact paths
- `Verification`: commands/checks run and results
- `Delegation`: subagents used, contracts passed, and how their work was verified; or `none`
- `Risks / gaps`: anything unverified, deferred, or worth reviewing
- `### Checkpoint`: current skill, completed gates, next required skill, next check, action (`continue now`, `ask user`, `pending pointer`, or `stop`)
- `Next`: usually `change-review` or `shipping`, phrased as an action/prompt or already-executed handoff; never a claim that Implementation finalized the work

## Shared standards

For architecture-sensitive or code-quality-sensitive work, load `../_shared/engineering-standards.md` and apply it as reference, not dogma.
