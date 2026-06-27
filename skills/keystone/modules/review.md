# Keystone Review Module

## Intent
Evaluate work for correctness, scope, risk, maintainability, and readiness without changing it.

## Load when
The user asks for review, critique, audit, code review, plan review, or readiness assessment.

## Allowed mutation
None.

## Must not
Fix, commit, ship, edit files, or perform finalization. Review reports only.

## May call
`research` for evidence; `gates/review.md` for required review criteria; `health` for broader risk context.

## Subagents and reasoning
Default reasoning: `high`. Prefer read-only reviewer subagents for focused reviews; escalate to `xhigh` for security, migration, release, or public API review. See `helpers/subagents.md`.

## Handoff
Return findings ordered by severity with evidence and recommended owner module for follow-up.

## Exit gate
Verdict, blockers, non-blocking findings, and evidence are clearly separated.
