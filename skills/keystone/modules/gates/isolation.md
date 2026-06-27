# Isolation Gate

## Purpose
Confirm mutation can happen safely before the first file change.

## Required checks
- Current workspace and branch/worktree state are known.
- User scope and protected files are identified.
- No unrelated dirty changes will be overwritten.

## Pass condition
It is safe to mutate only scoped files, or the user has approved the risk.

## Fail action
Stop and ask for direction before changing files.
