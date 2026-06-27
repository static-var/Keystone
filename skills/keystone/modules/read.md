# Keystone Read Module

## Intent
Understand existing files, docs, plans, code, or user-provided material and report accurate findings.

## Load when
The user asks to inspect, summarize, explain, inventory, compare existing artifacts, or gather context before deciding.

## Allowed mutation
None.

## Must not
Edit files, infer beyond evidence, or turn reading into implementation without a handoff.

## May call
`research` for missing external context; `health` for broad project condition checks.

## Handoff
Summarize evidence, cite files or inputs read, and recommend the next primary module if action is needed.

## Exit gate
Findings are grounded in inspected material and unresolved unknowns are named.
