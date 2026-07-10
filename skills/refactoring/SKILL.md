---
name: refactoring
description: Use when the user asks to refactor, clean up, simplify, extract, inline, reduce duplication, improve maintainability, address code smells, improve boundaries/types, or reorganize code without intended behavior changes.
---

# Refactoring

## Core principle

Refactoring changes structure while preserving behavior. Improve design in small, reversible steps, with characterization or regression proof when behavior could drift.

## Load when

Use when the user asks to refactor, clean up, simplify, extract functions/classes, inline needless indirection, reduce duplication, rename for clarity, improve type boundaries, remove code smells, or reorganize code without asking for new behavior.

If the user wants behavior change, use `implementation`. If a failure cause is unknown, use `root-cause-analysis`. If the refactor is broad or risky, create a refactor doc before mutation.

## Outcome contract

A complete refactor reports:

- the behavior invariant that must not change;
- smells or pressures addressed;
- isolation checked before mutation via `../_shared/gates/isolation.md`;
- characterization/regression proof used before risky edits;
- files changed and why each changed;
- verification commands/results or explicit proof gaps;
- checkpoint handoff to `change-review` when review is needed.

## Process

1. Classify size and risk.
   - Small/local: one area, clear invariant, existing proof likely enough.
   - Large/cross-cutting: multiple boundaries, weak coverage, shared contracts, or context-window risk.
   - Completion criterion: refactor path is either safe for direct mutation or documented first.
2. For large refactors, write a refactor doc under `docs/keystone/refactors/YYYY-MM-DD-<slug>.md` before editing.
   - Include goal, invariants, smells, affected areas, slices, proof, rollback, and review focus.
   - Completion criterion: doc is specific enough for `task-creation` or `implementation`.
3. Pass isolation before mutation.
   - Load/check `../_shared/gates/isolation.md`.
   - Respect unrelated dirty files and protected scope.
   - Completion criterion: mutation scope is safe.
4. Establish behavior proof.
   - Prefer existing behavior tests; add characterization coverage when the invariant lacks a tripwire.
   - Completion criterion: there is a tripwire for accidental behavior change or a documented proof gap.
5. Apply small refactorings.
   - Prefer rename, extract, inline, move, split, consolidate, simplify conditionals, remove dead code, and clarify ownership.
   - Keep public contracts stable unless explicitly approved.
   - Completion criterion: each step is understandable and reversible.
6. Use engineering standards.
   - Load `../_shared/engineering-standards.md` for architecture or ownership decisions.
   - Remove abstractions that lack current pressure.
   - Completion criterion: the result has clearer ownership, state, naming, or boundaries.
7. Verify.
   - Load and pass `../_shared/gates/proof.md` for the preserved invariant.
   - Completion criterion: behavior invariant is supported by observed evidence.
8. Checkpoint and hand off.
   - Use `../_shared/gates/checkpoint.md`.
   - Hand off to `change-review` for non-trivial refactors or leave an explicit review pointer.

## Smell prompts

Investigate duplication, long functions, god objects, feature envy, primitive obsession, data clumps, shotgun surgery, divergent change, hidden control flow, speculative generality, vague managers/helpers, mixed abstraction levels, duplicated state, and unclear ownership.

## Hard rules

- Preserve behavior unless the user explicitly approves a behavior change.
- Do not disguise feature work as refactoring.
- Do not perform broad refactors without a refactor doc.
- Do not trust “looks equivalent” without proof or an explicit proof gap.
- Do not introduce patterns for imagined futures.

## Output format

```markdown
## Refactor report
Invariant: ...
Size/risk: small / large
Smells addressed: ...
Files changed: ...
Verification: ...
Risks/gaps: ...

### Checkpoint
Current skill: refactoring
Completed gates: ...
Next required skill: change-review / implementation / none
Next check: ...
Action: continue now / ask user / pending pointer / stop
```
