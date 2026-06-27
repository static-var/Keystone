# Keystone Ship Module

## Core principle
Ship only already-completed work with evidence. Finalization is proof, review, packaging, release notes, branch/PR/handoff, and risk disclosure — not new implementation.

## Load when
Load when the user asks to finish a branch, prepare PR or merge notes, package a release, write changelog/release notes, confirm readiness, hand off completed work, tag/version, or decide whether work is shippable.

## Not for
- Starting new implementation or sneaking in last-minute fixes.
- Root-cause debugging; use `debug`.
- General project risk audits; use `health`.
- Shaping unfinished requirements; use `shape`.
- Bypassing proof, review, or human release approvals.

## Outcome contract
Deliver a shipping packet that includes:
- current branch/worktree status;
- scope of completed work and explicit non-scope;
- proof evidence (tests, builds, manual checks, artifacts) with commands/results;
- review evidence or required review status;
- package/release evidence where applicable (versions, artifacts, checksums, dry runs, links);
- changelog/release-note text or summary;
- unresolved risks and rollback/handoff notes;
- exact human actions needed next.

## Modes
- **PR handoff:** summarize diff, proof, risks, review status, and reviewer instructions.
- **Release prep:** verify versioning, changelog, build/package artifacts, environment, and approvals.
- **Integration finish:** prepare merge guidance, branch cleanup, and post-merge checks.
- **Delivery packet:** produce final notes for a stakeholder without changing code.
- **Readiness verdict:** say ship / do not ship / ship with risk, backed by evidence.

## Process
1. Confirm the work is implementation-complete. If new behavior is still needed, stop and route to `build` or `debug`.
2. Inspect branch and diff status without modifying unrelated files.
3. Identify the proof gate required for the change: focused tests, full test suite, build, lint, typecheck, manual QA, screenshots, package dry run, or deploy preview.
4. Run or cite verification evidence. Do not claim passing checks you did not observe.
5. Confirm review gate: self-review, code review, security/product/design review, or note what remains pending.
6. Prepare release evidence layers as applicable: version, changelog, release notes, artifact names, package contents, compatibility notes, migration steps, rollback plan.
7. Write PR/handoff text that is concise, evidence-backed, and honest about risks.
8. Avoid implementation. If a gate fails, report failure and route to `debug`/`build`; do not fix under `ship` unless explicitly asked.
9. End with a clear verdict and next human action.

## Subagents and reasoning
Default reasoning: `medium`. Use subagents for bounded release-note drafting, checklist verification, artifact inspection, or independent review of the shipping packet. Use `high` for multi-platform packaging, production releases, security-sensitive changes, migrations, or unresolved release risk. Subagents must not introduce new implementation.

## Hard rules
- No new implementation in ship mode. Gate failures create a handoff, not stealth fixes.
- Evidence before assertions: every readiness claim needs command output, artifact proof, or documented review.
- Do not bypass review or package gates because the change “looks small.”
- Keep changelog/release notes user- or operator-relevant; avoid dumping raw commit noise.
- State branch name and working tree cleanliness when available.
- If readiness is uncertain, say “not ready” or “ready with risk,” not “done.”

## Failure modes
- **Victory lap without proof:** announcing completion before tests/build/review evidence.
- **Last-mile coding:** making new fixes under the cover of release prep.
- **Release-note mush:** vague notes that omit impact, migration, or risk.
- **Dirty handoff:** leaving untracked files, unclear branch state, or hidden manual steps.
- **Gate theater:** listing checks without results or timestamps/context.

## Output format
```markdown
## Ship packet
Verdict: Ship / Do not ship / Ship with risk
Branch/status: ...

### Scope
- Completed: ...
- Not included: ...

### Proof evidence
- Command/artifact/result: ...

### Review evidence
- ...

### Release notes / changelog
- ...

### Risks and rollback
- ...

### Next human actions
- ...
```
