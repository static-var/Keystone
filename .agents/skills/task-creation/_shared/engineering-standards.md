# Keystone Engineering Standards

Language-agnostic reference for implementation, refactoring, change review, and project audit.

## Core standard

Write code that makes ownership, state, behavior, and change pressure obvious. Prefer direct, boring structures until the domain shows real variation. A pattern earns its place only when it removes current pressure.

## Ownership and boundaries

- Put behavior with the concept that owns it.
- Keep domain rules separate from UI, transport, persistence, and framework glue.
- Make state ownership explicit; avoid duplicated sources of truth.
- Cross boundaries through named contracts, not shared mutable objects or hidden globals.
- Place interfaces where callers need stable intent or implementations genuinely vary.

## State and side effects

- One source of truth per fact.
- Side effects should be visible at boundaries and testable through behavior.
- Avoid accidental singletons, ambient registries, and global mutation unless the lifecycle is truly process-wide.
- Prefer factories for objects that need scoped dependencies, runtime parameters, or lifecycle control.
- Make invalid states hard to represent where the language/project makes that practical.

## Abstractions and patterns

Use patterns to solve current pressure, not to decorate simple code.

A pattern is justified when it:

- names a real domain seam;
- reduces coupling at a boundary;
- isolates volatility;
- improves testability of meaningful behavior;
- lets the next likely change land in one clear place.

A pattern is suspicious when it:

- has one call site and no variation pressure;
- hides a simple operation behind vague names;
- spreads one behavior across many files;
- exists because AI defaulted to `manager`, `provider`, `service`, or `helper`.

## Taste checks

Ask before and after a non-trivial change:

- Can a new maintainer find where this behavior belongs?
- Does each module/function/class have one clear reason to change?
- Are names specific to the domain rather than generic plumbing?
- Is data transformed in one understandable path?
- Are errors surfaced where recovery decisions can be made?
- Does the test prove behavior instead of implementation trivia?
- Did cleanup preserve behavior, or did it smuggle in a feature change?

## Smell checklist

Investigate these smells before accepting a design:

- duplicated state or competing sources of truth
- domain logic inside views, controllers, serializers, or persistence adapters
- UI or transport code reaching across layers to policy decisions
- god functions/classes that validate, orchestrate, persist, format, and handle errors
- vague `manager`, `helper`, `util`, `common`, or `service` names
- hidden control flow through magic registration, callbacks, observers, or lifecycle hooks
- stringly APIs for states, commands, permissions, or field names
- boolean parameter clusters that encode multiple modes
- speculative interfaces, factories, builders, repositories, or adapters
- accidental singleton state where scoped instances or factories fit better
- broad refactors without characterization or regression checks

## Review posture

Treat these standards as prompts for evidence, not dogma. If a simple design violates a fashionable pattern but keeps ownership and behavior clear, keep it simple. If a familiar pattern obscures responsibility, remove it or justify it with current pressure.
