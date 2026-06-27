# Keystone Build Module

## Core principle

Build changes through evidence, not vibes: isolate first, specify the next observable behavior, prove the test can fail, make the smallest correct change, then refactor without changing behavior.

Build is the mutation module. It may edit scoped project artifacts after the isolation gate passes, but it does not decide that work is shipped. Completion means "implemented with proof and ready for review/ship," not finalized.

## Load when

Use Build when the user asks to:

- implement, create, edit, or wire behavior
- add a feature, screen, endpoint, command, migration, or integration
- refactor existing code while preserving behavior
- change architecture, module boundaries, interfaces, or contracts
- apply an approved plan from `breakdown`
- delegate independent implementation work to subagents/workers
- make focused content or configuration changes that require mutation

## Not for

Do not use Build for:

- routing unclear work: use `router`
- researching unknowns without mutation: use `research`
- shaping requirements or acceptance criteria: use `shape`
- decomposing large work before implementation: use `breakdown`
- diagnosing a failure whose cause is unknown: use `debug`
- reviewing completed changes: use `review`
- releasing, merging, publishing, or finalizing: use `ship`

## Outcome contract

Before Build exits, it must be able to report:

- isolation was checked before the first mutation via `gates/isolation.md`
- the exact user scope and protected files were respected
- the intended behavior or refactor invariant is stated plainly
- tests, examples, or checks prove the change, or gaps are explicitly disclosed
- red-capable tests were used for behavior changes whenever practical
- delegated work, if any, was verified by the parent before acceptance

Build must not claim work is done because code "looks right." Proof is required before completion claims.

## Modes

### TDD feature build

Use when adding or changing observable behavior.

Contract:

- define one behavior slice at a time
- write or identify the smallest test/check that should fail before the change
- run it and confirm the failure is meaningful, not caused by setup noise
- implement the smallest code that makes it pass
- run the focused check again
- run relevant regression checks
- refactor only while checks stay green

Prefer tests that exercise real behavior over tests that only verify mocks, implementation details, or snapshots. If a failing test cannot be created, state why and use the strongest available proof.

TDD exceptions are rare but real. When a red-capable automated test is impractical, state the reason before editing and write an alternative proof plan. Acceptable cases include documentation-only edits, generated files, one-off migrations where rollback is the proof, external systems unavailable in the environment, exploratory spikes that will be thrown away, or emergency config changes. The alternative proof plan must name the observable check, manual verification, diff review, sample input/output, dry run, or rollback validation that will replace red/green.

### Refactor

Use when preserving behavior while improving structure, names, duplication, readability, or boundaries.

Contract:

- name the behavior that must not change
- find existing tests or add characterization tests before edits when coverage is weak
- make small mechanical changes first
- keep public contracts stable unless the user requested a contract change
- run regression checks before and after meaningful refactor steps
- stop if behavior questions appear; route back to `shape` or `debug` as needed

A characterization test captures what the current system does before you change structure. It is not a claim that current behavior is ideal; it is a tripwire that prevents accidental behavior changes while refactoring. Write it around externally visible behavior, important edge cases, or bug-compatible outputs that must stay stable until the user approves a behavior change.

Refactoring is not a license to redesign everything nearby.

### Architecture-sensitive build

Use when the change affects boundaries, state management, cross-module dependencies, platform conventions, or long-lived maintainability.

Contract:

- identify the domain shape before choosing architecture
- choose the lightest architecture that fits the problem
- define contracts/interfaces where they reduce coupling or clarify ownership
- keep domain rules separate from transport, UI, persistence, and framework glue
- use patterns only when they remove real pressure, not to decorate simple code
- validate that the result is pleasant for developers to read, understand, maintain, and look at

SOLID is a pressure-test, not dogma:

- **SRP:** Can this unit change for one clear reason, or are unrelated policies bundled together?
- **OCP:** Can the next known variation be added without editing fragile existing logic, or is a simpler edit safer for now?
- **LSP:** Can substitutes honor the same contract without surprising callers?
- **ISP:** Are callers forced to depend on methods, fields, events, or permissions they do not use?
- **DIP:** Do high-level policies depend on stable abstractions at real boundaries, or are abstractions hiding one local call?

Examples of appropriate taste:

- mobile UI may use MVVM/MVI when state, events, and rendering need separation
- clean architecture may fit when domain rules must survive UI, database, or API changes
- SOLID and design patterns are justified only when they relieve current pressure

### Delegated/parallel build

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
   - If scope is unsafe or ambiguous, ask one focused question or route to `shape`.

2. Pass isolation before mutation.
   - Load/check `gates/isolation.md`.
   - Know the workspace, branch/worktree state, and dirty files.
   - Stop if unrelated changes could be overwritten.

3. Choose the mode.

4. Define the next outcome.
   - Write the smallest observable behavior, invariant, or contract.
   - Avoid "make it better" as an implementation target.

5. Establish proof before code.
   - For behavior changes, create or identify a red-capable test/check.
   - Run the focused check and confirm the failure would pass only for the intended change.
   - For refactors, establish characterization or regression coverage.
   - If proof is impossible in the environment, record the limitation before editing and use an alternative proof plan.

6. Implement the smallest correct slice.
   - Edit only files in scope.
   - Keep changes narrow and reversible.
   - Prefer clear names and direct control flow.
   - Do not invent broad architecture to satisfy a small behavior.

7. Green.
   - Run the focused test/check.
   - If it fails unexpectedly, use `debug`; do not stack guesses.

8. Refactor.
   - Remove duplication introduced by the slice.
   - Improve readability without broadening behavior.
   - Keep tests green after cleanup.

9. Regression check.
   - Run the most focused relevant suite available.
   - Never replace verification with a summary.

10. Early smell check.
   - Stop and simplify if the diff introduces god functions, vague `manager`/`helper` names, hidden control flow, stringly APIs, layer violations, or speculative interfaces.

11. Architecture pressure-test.
   - For architecture-sensitive changes, answer the SOLID questions and remove abstractions that do not survive them.

12. Handoff.
   - Summarize changed files and behavior.
   - Include commands run and results.
   - Disclose unverified areas.
   - Recommend `review` or `ship` as the next module when appropriate.

## Architecture taste checklist

Use this checklist before accepting the design:

- Does the architecture match the domain complexity rather than the agent's desire to sound senior?
- Is each module/class/function responsible for one understandable thing?
- Are domain concepts named in the user's language?
- Are interfaces/contracts placed at real boundaries, not between every pair of functions?
- Is state ownership explicit?
- Are side effects isolated enough to test meaningful behavior?
- Would a developer know where to add the next similar behavior?
- Is the simplest path also readable, or has simplicity become cleverness?
- Is duplication removed only after the repeated concept is real?
- Are patterns such as Strategy, Repository, Adapter, Observer, MVVM, MVI, or Clean Architecture justified by current pressure?
- Does the diff pass the SOLID pressure-test questions without adding dogmatic ceremony?
- Does the diff avoid god functions, vague managers/helpers, hidden control flow, stringly APIs, layer violations, and speculative interfaces?

## Subagents and reasoning

Default reasoning: `medium`.

Escalate to `high` when:

- architecture boundaries are being changed
- tests are failing for unclear reasons
- multiple agents must coordinate through contracts
- data loss, security, billing, release, or migration risk exists
- the user asks for broad refactoring or platform-specific architecture judgment

Use subagents/workers when:

- slices can be verified independently
- files do not overlap, or ownership is explicitly assigned
- exploration can happen without mutation

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

- Build must pass `gates/isolation.md` before the first mutation.
- Build must not ship, merge, publish, release, or finalize work.
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
- **Finalization leak:** Build says work is shipped, merged, or ready for users instead of ready for review/ship.

## Output format

When handing back from Build, respond with:

- `Summary`: what changed, in bullets
- `Files changed`: exact paths
- `Verification`: commands/checks run and results
- `Delegation`: subagents used, contracts passed, and how their work was verified; or `none`
- `Risks / gaps`: anything unverified, deferred, or worth reviewing
- `Next`: usually `review` or `ship`, never a claim that Build finalized the work
