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
`read` for evidence; `gates/review.md` for required review criteria; `health` for broader risk context.

## Handoff
Return findings ordered by severity with evidence and recommended owner module for follow-up.

## Exit gate
Verdict, blockers, non-blocking findings, and evidence are clearly separated.
