# Keystone Handoff Packet

Use this packet whenever one Keystone skill hands work to another. Keep it concise and evidence-backed.

## Fields

- `source skill`: skill producing the handoff
- `target skill`: skill to load next
- `goal`: one-sentence outcome for the target skill
- `evidence`: facts, command output, user decisions, citations, or artifacts already established
- `files`: relevant paths and whether each is read-only, mutable, or protected
- `risks`: uncertainty, skipped checks, safety constraints, rollback concerns, or accepted tradeoffs
- `next check`: gate, command, question, review, or first inspection the target should run
- `overrides`: explicit user waivers or decisions, with risk accepted

## Rules

- Do not silently bypass protected files, secret handling, isolation requirements, destructive operations, or policy restrictions.
- Treat subagent output as evidence to verify, not truth to repeat.
- If the next step is unsafe or ambiguous, ask the smallest question that makes the handoff safe.
- If shipping or irreversible external effects are requested, require explicit user intent plus proof/review evidence.
