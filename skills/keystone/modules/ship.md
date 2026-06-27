# Keystone Ship Module

## Intent
Finalize already-completed work for delivery, integration, handoff, or release readiness.

## Load when
The user asks to finish, prepare PR/merge notes, finalize a branch, package delivery, or confirm work is ready to ship.

## Allowed mutation
Only finalization artifacts explicitly requested, after proof and review gates are satisfied.

## Must not
Perform initial isolation, start new implementation, bypass review, or treat unverified work as shippable.

## May call
`gates/proof.md`, `gates/review.md`, and `gates/ship.md`; `health` for readiness checks.

## Handoff
Provide final status, evidence, unresolved risks, and any human actions needed for integration.

## Exit gate
Work is complete, verified, reviewed as required, and finalization is limited to delivery steps.
