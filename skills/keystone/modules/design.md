# Keystone Design Module

## Intent
Define visual direction, interaction feel, layout principles, design tokens, and aesthetic decisions.

## Load when
The user asks for visual design, style systems, art direction, polish, motion feel, or design alternatives.

## Allowed mutation
Only design artifacts or explicitly scoped style files.

## Must not
Ship implementation, ignore accessibility, or replace product-flow decisions owned by `ui`.

## May call
`ui` for flow clarity; `write` for design rationale; `build` after design is approved for implementation.

## Handoff
State the design direction, constraints, and implementation-ready decisions.

## Exit gate
The design guidance is specific enough to execute or review.
