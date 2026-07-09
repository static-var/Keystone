# Checkpoint Gate

## Purpose
Prevent Keystone skills from ending at the wrong boundary.

This file owns the stop-or-continue contract. Phase skills decide what work is next; they do not redefine checkpoint pass/fail. When the decision targets another skill, load `../handoff-packet.md` and carry its fields forward.

A checkpoint is the visible stop-or-continue decision made before any user-facing final response, skill handoff, or long-running delegated step. It turns continuation from memory into an explicit ledger.

This gate is binary: pass or fail.

## Required checks
1. Identify the active sequence and current skill.
2. List gates already satisfied with evidence, not labels.
3. Decide the next required skill or `none`.
4. Decide the next check the target skill must run first.
5. Choose the continuation action:
   - `continue now` when Keystone can safely load the next required skill without new user permission;
   - `ask user` when the next step needs approval, credentials, destructive action, or scope clarification;
   - `pending pointer` when the next step must be done by a human or unavailable tool;
   - `stop` only when no Keystone handoff remains or the user explicitly requested stopping at this boundary.
6. Update the harness todo/checklist ledger when the host exposes one. The last item must always be `Next / upcoming task: <specific next action>`, or `Next / upcoming task: none — sequence complete` when no handoff remains.
7. If stopping before the normal sequence completes, record why and the risk accepted.

## Auto-advance rule
If a skill completes and the next step is required by the active Keystone sequence or by a gate, Keystone must continue to that next skill in the same session when safe. Do not end with a generic “done” or bury the next step in prose.

Common required continuations:
- `implementation` with non-trivial mutations -> `change-review`, unless the user explicitly asked to stop after implementation or the change is truly trivial and self-review is sufficient under `review.md`.
- `change-review` with no blockers and explicit delivery requested -> `shipping`.
- `shipping` with missing proof/review/ship evidence -> route to `implementation`, `root-cause-analysis`, `change-review`, or `project-audit` instead of finalizing.

## Prompt rule
When Keystone cannot auto-advance, the final response must include an explicit prompt or pointer:

```text
Keystone checkpoint: <current skill> -> <target skill|none>
Completed: <evidence-backed gates/checks>
Blocked by: <approval/tool/scope/human review/none>
Next check: <first action for the target skill>
Action: continue now / ask user / pending pointer / stop
Todo tail: Next / upcoming task: <target skill + first concrete check/action, or none — sequence complete>
Prompt: <exact question or handoff pointer, omitted only when Action is stop because target is none>
```

## Pass condition
Pass only when the response makes the next event impossible to miss: either Keystone continues to the next skill, or the user receives an explicit question/pending pointer.

## Fail action
Do not claim the work is done. Re-open the checkpoint, name the missing next event, and route or ask.
