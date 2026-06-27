# Keystone Breakdown Module

## Intent
Break a goal into ordered, scoped, verifiable work items.

## Load when
The user asks for a plan, decomposition, sequencing, milestones, task list, or implementation approach.

## Allowed mutation
Only planning artifacts explicitly requested.

## Must not
Implement tasks, rename this module to `plan`, or treat the plan as proof of completion.

## May call
`research` for context and unknowns; `review` to critique the plan.

## Subagents and reasoning
Default reasoning: `high`. Identify independent tasks that can be delegated, assign expected role/reasoning per task, and request reviewer subagents for risky plans. See `helpers/subagents.md`.

## Handoff
Provide steps with dependencies, verification gates, and recommended next primary module.

## Exit gate
Each work item has a clear outcome and verification method.
