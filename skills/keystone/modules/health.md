# Keystone Health Module

## Core principle
Health audits reveal project/tooling risk with evidence. Detect drift, fragility, missing proof, and operational hazards without fixing anything unless the user explicitly asks for repairs.

## Load when
Load when the user asks for a health check, readiness scan, risk assessment, project status audit, tooling audit, dependency/config review, maintenance assessment, drift detection, or “what should we worry about?”

## Not for
- Fixing issues found during the audit.
- Debugging a specific failure to root cause; use `debug`.
- Shipping a completed branch; use `ship`.
- Designing new product behavior; use `shape`.
- Research briefs about a narrow question; use `research`.

## Outcome contract
Deliver a health report that includes:
- audit scope and evidence inspected;
- status by category;
- risks ranked by severity and confidence;
- drift detected between docs/configs/tests/code/dependencies/CI;
- checks not run and why;
- recommended next module for each follow-up;
- explicit no-fix confirmation unless repairs were requested.

## Modes
- **Project snapshot:** summarize structure, active areas, scripts, tests, CI, docs, and current branch state.
- **Tooling audit:** inspect package/build/test/lint/typecheck/CI configuration and command health.
- **Release readiness health:** assess risk categories before ship, without preparing release artifacts.
- **Drift detection:** compare declared scripts/docs/configs with actual files and behavior.
- **Risk triage:** rank issues by impact, likelihood, evidence strength, and recommended owner/module.

## Process
1. Define scope: whole repo, subsystem, tooling, release readiness, dependencies, docs, or operational process.
2. Inspect before judging: read manifests, scripts, CI, tests, docs, configs, recent status, and relevant gates.
3. Collect evidence categories:
   - branch/worktree state;
   - build/test/lint/typecheck scripts;
   - dependency and lockfile consistency;
   - CI/release/package configuration;
   - docs vs actual commands;
   - test coverage signals and skipped/flaky markers;
   - security/secrets/config exposure signals;
   - ownership, TODOs, deprecations, and stale artifacts.
4. Run safe focused checks when useful and allowed; avoid destructive or broad state-changing commands.
5. Detect drift: documentation pointing to missing scripts, scripts referencing missing files, stale generated assets, inconsistent versions, orphaned configs, CI mismatch.
6. Rank risks with severity, likelihood, evidence, and confidence. Avoid treating unverified suspicion as fact.
7. Recommend next action per item: `research`, `debug`, `shape`, `breakdown`, `build`, `review`, `ship`, or no-op.
8. Stop at reporting unless the user explicitly requested fixes.

## Subagents and reasoning
Default reasoning: `medium`. Use read-only scout subagents for broad inventory and reviewer subagents for independent risk triage. Use `high` for release readiness, security-sensitive audits, large monorepos, severe tooling drift, or when health findings affect go/no-go decisions. Subagents must remain read-only unless repairs are explicitly requested.

## Hard rules
- No fixing, formatting, dependency updates, or cleanup unless explicitly requested.
- Evidence categories must be named; unchecked areas must be listed.
- Do not overstate confidence. Label inferred risks and explain what would verify them.
- Prefer safe read-only or focused validation commands.
- Separate “broken now,” “risky,” “stale,” and “unknown.”
- Health can recommend `ship`, but does not replace ship proof gates.

## Failure modes
- **Audit-as-fix:** making opportunistic changes during a scan.
- **Checklist theater:** listing categories without evidence.
- **False certainty:** declaring healthy because a narrow check passed.
- **Drift blindness:** missing mismatches between docs, scripts, CI, and actual files.
- **Unranked dump:** overwhelming the user with findings but no severity or next module.

## Output format
```markdown
## Health report
Scope: ...
No-fix status: confirmed / repairs requested

### Evidence inspected
- ...

### Category status
| Category | Status | Evidence | Confidence |
|---|---|---|---|
| Build/test/tooling | ... | ... | ... |

### Risks and drift
1. Severity — finding
   - Evidence:
   - Impact/likelihood:
   - Recommended next module:

### Checks not run
- ...

### Overall assessment
Healthy / Watch / At risk / Blocked — rationale
```
