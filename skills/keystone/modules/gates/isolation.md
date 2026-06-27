# Isolation Gate

## Purpose
Confirm mutation can happen safely before the first file change.

This gate protects user work, local experiments, and unrelated files. It is binary: either the workspace is isolated for the requested blast radius, or mutation stops.

## Required checks
1. Identify the workspace:
   - Run `git rev-parse --show-toplevel`.
   - Run `git branch --show-current`.
   - Run `git worktree list` or compare `git rev-parse --git-dir` with `git rev-parse --git-common-dir`.
2. Capture dirty state:
   - Run `git status --porcelain` before editing.
   - Treat every listed path as user-owned until proven otherwise.
3. State the planned blast radius:
   - List the exact files or directories expected to change.
   - List protected files, generated files, scripts, tests, and modules that must not change.
4. Compare dirty files to planned changes:
   - Planned + clean: safe to edit.
   - Planned + already dirty: ask whether to build on, inspect, or avoid those changes.
   - Unplanned + dirty: do not touch.
5. Build a collision matrix before mutation.

## Collision matrix

| Dirty path | Planned to edit? | Owner known? | Action |
| --- | --- | --- | --- |
| No dirty paths | N/A | N/A | Pass |
| Dirty path inside blast radius | Yes | User/unknown | Ask before editing that file |
| Dirty path outside blast radius | No | User/unknown | Leave untouched |
| Dirty path is generated artifact | Maybe | Tool/unknown | Do not delete unless user approved |
| Dirty path conflicts with requested scope | Yes | Unknown | Fail until clarified |

## Pass condition
Pass only when all are true:
- Workspace root, branch, and worktree state are known.
- `git status --porcelain` has been captured.
- Planned blast radius is explicit.
- Dirty files are either absent, inside approved scope, or guaranteed untouched.
- No auto-stash, auto-commit, reset, checkout, cleanup, or generated-file deletion is needed.

## Fail action
Stop before changing files. Do not auto-stash, auto-commit, reset, or "clean up" user work.

Report:

```text
Isolation Gate: FAIL
Workspace: <root>
Branch/worktree: <branch and worktree state>
Planned blast radius: <files/dirs>
Dirty files: <git status --porcelain output>
Collision: <which dirty paths overlap or create risk>
Needed decision: <ask user to approve, narrow scope, or provide a clean workspace>
```