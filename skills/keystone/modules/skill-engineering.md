# Keystone Skill Engineering Module

## Intent
Maintain Keystone skill content, module contracts, routing, and gate documentation.

## Load when
A Keystone maintainer explicitly asks to create, edit, audit, or validate Keystone skill files.

## Allowed mutation
Only Keystone skill files and only within the maintainer-approved scope.

## Must not
Run as a general user module, expose internal modules as public commands, change product code, or rename `breakdown` to `plan`.

## May call
`read` for current skill state; `review` for contract audit; gates as needed for proof.

## Subagents and reasoning
Default reasoning: `high`. Use worker subagents only for independent Keystone-maintenance slices and reviewer subagents for contract audits; escalate to `xhigh` when routing, public entrypoint, or packaging semantics change. See `helpers/subagents.md`.

## Handoff
List changed skill files, contract decisions, and validation performed.

## Exit gate
Maintainer-only scope is confirmed and every changed module preserves the required contract sections.
