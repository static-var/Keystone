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

## Handoff
Name the selected primary module and the reason in one sentence, then continue under that module's contract.

## Exit gate
Exactly one primary module is selected, or one clarifying question is asked.
