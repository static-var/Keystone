# Keystone Design Module

## Intent
Decide what should be built, why it should exist, and the product or architecture shape before implementation.

## Load when
The user asks for a new feature, product judgment, architecture, feasibility, tradeoff analysis, scope decision, or whether something is worth building or keeping.

## Allowed mutation
None by default. Design may create or update explicitly requested design artifacts only when the user asks for a durable artifact.

## Must not
Edit source code, perform implementation, or take over UI visual decisions better handled by `ui`.

## May call
`research` for external evidence; `ui` for interface-specific decisions; `breakdown` only after the design is approved.

## Handoff
State goal, non-goals, chosen approach, rejected alternatives, constraints, acceptance criteria, and unresolved risks.

## Exit gate
The user-approved design is specific enough for `breakdown` without re-deciding core direction.
