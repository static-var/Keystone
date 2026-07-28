# Keystone Handoff Packet

Use this packet whenever `gates/checkpoint.md` selects another Keystone skill. This file owns handoff completeness; the source skill supplies branch-specific evidence.

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

- When the target skill is `shipping`, the `evidence` field is an authorization snapshot: it carries the user's verbatim explicit delivery request and exact authorized action set at handoff time.
- Before a Shipping action, reconcile that snapshot with the latest explicit user instructions:
  - Remove any action the user clearly narrows or revokes, and apply that restriction immediately.
  - Add an action beyond the snapshot only when a new explicit user request names it.
  - Ask for confirmation only when the current instruction cannot be mapped unambiguously to concrete actions.
- Do not silently bypass protected files, secret handling, isolation requirements, destructive operations, or policy restrictions.
- Treat subagent output as evidence to verify, not truth to repeat.
- If the next step is unsafe or ambiguous, ask the smallest question that makes the handoff safe.
- If shipping or irreversible external effects are requested, require explicit user intent plus proof/review evidence.
