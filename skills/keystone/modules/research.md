# Keystone Research Module

## Intent
Investigate unknowns, collect evidence, compare options, and synthesize reliable answers.

## Load when
The user asks for research, source comparison, feasibility investigation, market/technical discovery, or evidence before choosing a path.

## Allowed mutation
Only notes or research artifacts the user explicitly requests.

## Must not
Implement decisions, present speculation as fact, or omit source quality caveats.

## May call
`read` for repository context; `write` for a polished research brief.

## Subagents and reasoning
Default reasoning: `medium`. Use scout or oracle subagents for independent evidence gathering; escalate to `high` for decisions that affect architecture, safety, market claims, or releases. See `helpers/subagents.md`.

## Handoff
Provide findings, confidence, sources or evidence consulted, and recommended next module.

## Exit gate
Key claims are supported by cited evidence or clearly marked as assumptions.
