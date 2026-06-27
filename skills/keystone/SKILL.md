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
| Read, inspect, summarize, extract URL/PDF/source material | `modules/read.md` |
| Gather external/internal information, compare sources, investigate options | `modules/research.md` |
| Draft, rewrite, structure prose and copy | `modules/write.md` |
| Interface design, screens, components, visual direction, screenshot aesthetics | `modules/ui.md` |
| Product decisions, feature scope, architecture, value judgment before build | `modules/design.md` |
| Breakdown approved design into executable tasks and verification steps | `modules/breakdown.md` |
| Implement or change files/code/content | `modules/build.md` |
| Diagnose failures, failing behavior, errors, bug reports, regressions, unexpected behavior | `modules/debug.md` |
| Review work without changing it | `modules/review.md` |
| Finalize completed work for delivery or integration | `modules/ship.md` |
| Maintain Keystone skill content itself | `modules/skill-engineering.md` |
| Agent/tooling health, repository condition, skill drift, context rot, risks | `modules/health.md` |

## Ambiguity rule

If several modules could apply, choose the module matching the next irreversible action. If still ambiguous, ask one concise clarifying question before loading a primary module.
