# Keystone Build Module

## Intent
Make scoped changes to files, code, content, or configuration.

## Load when
The user asks to implement, create, edit, refactor, migrate, or otherwise mutate project artifacts.

## Allowed mutation
Only files and behavior explicitly in scope.

## Must not
Mutate before passing `gates/isolation.md`, broaden scope, silently alter protected files, or ship/finalize work.

## May call
`gates/isolation.md` before the first mutation; `gates/red.md` when tests or examples should fail first; `debug` for failures; `review` after changes.

## Handoff
Report files changed, verification performed, and remaining risks or next module.

## Exit gate
Isolation gate was checked before first mutation, changes are limited to scope, and proof is available or gaps are disclosed.
