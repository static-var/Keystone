# Keystone Shape Module

## Intent
Shape what the user-facing output should be before implementation. This module combines prose, product direction, UI/UX, visual direction, interface copy, and design tradeoffs.

## Load when
The user asks to draft, rewrite, structure prose, define product behavior, design a feature, make architecture or scope tradeoffs, improve a UI, critique a screen, choose visual direction, or prepare implementation-ready acceptance criteria.

## Allowed mutation
None by default. Shape may create or update explicitly requested design artifacts, specs, copy docs, mock content, or scoped UI/source files only when the user asks for a durable artifact.

## Must not
Implement code behavior without a `build` handoff, own root-cause debugging, invent facts, or treat a design/spec as proof of completion.

## May call
`research` for source material or external evidence; `breakdown` after the shape is approved; `build` when the user explicitly asks to implement approved shape; `review` for critique.

## Subagents and reasoning
Default reasoning: `medium`. Use writer/UI/design subagents for bounded alternatives or critiques; escalate to `high` for multi-screen flows, accessibility, design-system impact, architecture, product viability, or irreversible scope decisions. See `helpers/subagents.md`.

## Handoff
State the chosen shape, audience/user path, constraints, non-goals, acceptance criteria, rejected alternatives, and whether the next step is `breakdown`, `build`, or `review`.

## Exit gate
The output is specific enough to decompose, implement, or review without re-deciding the core direction.
