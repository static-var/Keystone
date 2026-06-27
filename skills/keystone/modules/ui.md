# Keystone UI Module

## Intent
Design user-facing interfaces: screens, components, visual hierarchy, interaction states, screenshots, typography, motion, and aesthetic direction.

## Load when
The user asks for UI, UX, component design, page layout, visual polish, screenshot-grounded feedback, interface copy in context, or a screen that looks wrong, unclear, ugly, inconsistent, or generic.

## Allowed mutation
Only UI specs, mock content, visual assets, or scoped UI/source files the user explicitly asks to change.

## Must not
Own product viability, backend architecture, broad feature scope, or implementation without a `build` handoff.

## May call
`design` for product/architecture decisions; `write` for standalone prose; `build` after UI direction is approved; `debug` if screenshot evidence proves a regression or broken behavior.

## Subagents and reasoning
Default reasoning: `medium`. Use UI/design-focused subagents for independent screen critiques or alternatives; escalate to `high` for multi-screen flows, accessibility, or design-system impact. See `helpers/subagents.md`.

## Handoff
Provide visual thesis, interface states, accessibility constraints, responsive concerns, implementation notes, and next module if build/debug work remains.

## Exit gate
The interface direction and state model are explicit enough to implement or review.
