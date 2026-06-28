# Keystone Router Module

## Intent
Classify the user's request and select one Keystone primary module.

## Load when
The task is ambiguous, explicitly asks for routing, or starts from `/keystone` without a clear module fit.

## Allowed mutation
None, except writing a short routing decision in the conversation.

## Must not
Modify files, perform implementation, or expose internal modules as public slash commands.

## May call
One primary module after classification. Gates only if that primary module requires them.

## Subagents and reasoning
Default reasoning: `low`. Do not deploy subagents for simple routing; ask one clarifying question if a safe single route is not clear. See `helpers/subagents.md`.

## Routing heuristics
Prefer the module indicated by the user's strongest current need, not the first verb alone. Weigh multiple signals together:
- Failure, error, broken behavior, repro, or "fix" language points to `debug` before implementation.
- Review, verify, approve, merge, or ship language points to `review` before release or cleanup.
- New capability requests route by maturity: use `shape` when intent is fuzzy, `breakdown` when the outcome is clear but work needs decomposition, and `build` when scope and acceptance criteria are already concrete.

## Disambiguation examples
- "debug this and fix it" -> select `debug`; establish cause before changing code.
- "review and ship" -> select `review`; verify readiness before any shipping step.
- "add feature" -> select `shape`, `breakdown`, or `build` based on maturity; ask one concise clarifying question if maturity is not inferable.

## Handoff
Name the selected primary module and the reason in one sentence, then continue under that module's contract.

## Exit gate
Exactly one primary module is selected, or one clarifying question is asked.
