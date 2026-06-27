# Keystone Health Module

## Intent
Assess project condition, readiness, risks, drift, and operational hygiene.

## Load when
The user asks for a health check, readiness scan, risk assessment, status audit, or project condition report.

## Allowed mutation
None, unless the user explicitly requests a health report file.

## Must not
Fix issues, commit, ship, or overstate confidence beyond checked evidence.

## May call
`research` for repository inspection; `review` for focused critique; `proof` gate only when verifying claims.

## Subagents and reasoning
Default reasoning: `medium`. Use scout subagents for broad read-only inventory and reviewer subagents for risk triage; escalate to `high` for release readiness or severe tooling drift. See `helpers/subagents.md`.

## Handoff
Report health categories, evidence, risks, and recommended next primary module.

## Exit gate
Status distinguishes checked facts from assumptions and lists follow-up actions.
