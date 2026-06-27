# Keystone Research Module

## Intent
Understand existing material and investigate unknowns. This module combines reading, inspection, summarization, source gathering, comparison, and evidence synthesis.

## Load when
The user asks to read, inspect, summarize, extract, explain, inventory, compare sources, investigate options, perform market/technical research, or gather context before choosing a path.

## Allowed mutation
None by default. Only write notes or research artifacts when the user explicitly requests a durable artifact.

## Must not
Edit project files, implement decisions, present speculation as fact, or omit source-quality caveats.

## May call
`shape` when findings need to become prose, UI/product direction, or design decisions; `health` for broad repository/tooling condition checks; `review` for critique of research conclusions.

## Subagents and reasoning
Default reasoning: `medium`. Use read-only scout subagents for large repositories or independent evidence gathering; use `low` for simple file summaries and escalate to `high` when findings affect architecture, safety, market claims, or release decisions. See `helpers/subagents.md`.

## Handoff
Summarize what was inspected, cite files/sources, separate facts from assumptions, state confidence, and recommend the next primary module if action is needed.

## Exit gate
Key findings are grounded in inspected material or cited evidence, and unresolved unknowns are named.
