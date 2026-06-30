# Checkpoint Gate

## Purpose
Prevent Keystone modules from ending at the wrong boundary.

A checkpoint is the visible stop-or-continue decision made before any user-facing final response, module handoff, or long-running delegated step. It turns orchestration from memory into an explicit ledger.

This gate is binary: pass or fail.

## Required checks
1. Identify the active sequence and current module.
2. List gates already satisfied with evidence, not labels.
3. Decide the next required module or `none`.
4. Decide the next check the target module must run first.
5. Choose the continuation action:
   - `continue now` when Keystone can safely load the next required module without new user permission;
   - `ask user` when the next step needs approval, credentials, destructive action, or scope clarification;
   - `pending pointer` when the next step must be done by a human or unavailable tool;
   - `stop` only when no Keystone handoff remains or the user explicitly requested stopping at this boundary.
6. If stopping before the normal sequence completes, record why and the risk accepted.

## Auto-advance rule
If a module completes and the next step is required by the active Keystone sequence or by a gate, Keystone must continue to that next module in the same session when safe. Do not end with a generic “done” or bury the next step in prose.

Common required continuations:
- `build` with mutations -> `review`, unless the user explicitly asked to stop after implementation or the change is truly trivial and self-review is sufficient under `gates/review.md`.
- `review` with no blockers and delivery requested -> `ship`.
- `ship` with missing proof/review/ship evidence -> route to `build`, `debug`, `review`, or `health` instead of finalizing.

## Prompt rule
When Keystone cannot auto-advance, the final response must include an explicit prompt or pointer:

```text
Keystone checkpoint: <current module> -> <target module|none>
Completed: <evidence-backed gates/checks>
Blocked by: <approval/tool/scope/human review/none>
Next check: <first action for the target module>
Action: continue now / ask user / pending pointer / stop
Prompt: <exact question or handoff pointer, omitted only when Action is stop because target is none>
```

## Pass condition
Pass only when the response makes the next event impossible to miss: either Keystone continues to the next module, or the user receives an explicit question/pending pointer.

## Fail action
Do not claim the work is done. Re-open the checkpoint, name the missing next event, and route or ask.
