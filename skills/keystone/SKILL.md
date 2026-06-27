---
name: keystone
description: Use when the user invokes /keystone or asks Keystone to route product, research, writing, UI, design, planning, implementation, debugging, review, shipping, health, or skill-maintenance work through its canonical orchestrator.
---

# Keystone

Keystone is a router/orchestrator skill. It selects the right internal module for the user's current request and keeps only one public entrypoint: `/keystone`.

## Routing rule

Load exactly one primary module for the current task. Load gates or helper modules only when the primary module explicitly needs them. Do not expose internal modules as public slash commands.

## Routing table

| User intent | Primary module |
|---|---|
| Choose the right Keystone path, classify intent, resolve module ambiguity | `modules/router.md` |
| Read, inspect, summarize, understand existing material | `modules/read.md` |
| Gather external/internal information, compare sources, investigate options | `modules/research.md` |
| Draft, edit, rewrite, structure prose | `modules/write.md` |
| UI copy, flows, component behavior, screen-level product UX | `modules/ui.md` |
| Visual direction, interaction feel, design system choices | `modules/design.md` |
| Break work into implementable steps, make a plan | `modules/breakdown.md` |
| Implement or change files/code/content | `modules/build.md` |
| Diagnose failures, bugs, regressions, unexpected behavior | `modules/debug.md` |
| Review work without changing it | `modules/review.md` |
| Finalize completed work for delivery or integration | `modules/ship.md` |
| Check repository/project condition, risks, readiness | `modules/health.md` |
| Maintain Keystone skill content itself | `modules/skill-engineering.md` |

## Ambiguity rule

If several modules could apply, choose the module matching the next irreversible action. If still ambiguous, ask one concise clarifying question before loading a primary module.
