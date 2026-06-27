# Keystone Debug Module

## Intent
Diagnose and fix bugs, failures, regressions, or unexpected behavior from evidence.

## Load when
The user reports an error, failing test, broken behavior, regression, flaky result, or asks to troubleshoot.

## Allowed mutation
Only minimal diagnostic artifacts and scoped fixes after the cause is supported by evidence.

## Must not
Guess fixes, conflate symptoms with root cause, or ship the result.

## May call
`read` for context; `build` for scoped fixes; `gates/proof.md` to verify the fix.

## Subagents and reasoning
Default reasoning: `high`. Use oracle subagents for root-cause analysis; escalate to `xhigh` for intermittent, cross-system, performance, security, or data-loss failures. See `helpers/subagents.md`.

## Handoff
State symptom, root cause evidence, fix made or proposed, and verification.

## Exit gate
The cause is explained with evidence and the fix is proven or remaining uncertainty is explicit.
