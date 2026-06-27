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
`read` for context; `research` for unknowns; `review` to critique the plan.

## Handoff
Provide steps with dependencies, verification gates, and recommended next primary module.

## Exit gate
Each work item has a clear outcome and verification method.
