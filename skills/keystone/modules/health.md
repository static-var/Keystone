# Keystone Health Module

## Core principle
Health is a read-only, whole-project condition scan. It turns repository evidence into mechanical findings about system drift, fragility, and maintenance risk; it does not repair, refactor, update, or reconfigure anything by default.

Health answers “what is the condition of this project or subsystem?” Review answers “is this specific change acceptable?” If the task centers on a PR/diff/patch, use `review`; if it centers on repo-wide readiness, drift, tooling, docs, tests, releases, or operational condition, use `health`.

## Load when
Load when the user asks for a health check, readiness scan, risk assessment, project status audit, tooling audit, dependency/config review, maintenance assessment, drift detection, “what should we worry about?”, or “is this repo in good shape?”

## Not for
- Fixing issues found during the audit.
- Reviewing a specific change, PR, patch, or commit; use `review`.
- Debugging a specific failure to root cause; use `debug`.
- Shipping a completed branch; use `ship`.
- Designing new product behavior; use `shape`.
- Research briefs about a narrow question; use `research`.

## Outcome contract
Deliver a health report where every finding maps:

`finding -> evidence -> impact -> confidence -> next Keystone module`

The report must include:
- audit scope and evidence inspected;
- concrete checklist status for tooling/CI drift, docs-vs-reality, config/env rot, dependency health, test health/flakiness, package/release health, and instruction/skill drift;
- risks ranked by severity and confidence using the Health priority rubric;
- checks not run and why;
- explicit no-fix confirmation unless repairs were requested.

Health priority rubric:
- **Critical:** Broken now, release-blocking, security-sensitive, data-loss-prone, or prevents required project operation. Urgency: act before `ship` or before depending on the affected subsystem. Next Keystone module: usually `debug` for failing behavior or `build` for repairs; use `ship` only for release gate follow-up after the issue is fixed.
- **Watch:** Risky, stale, drifting, or likely to become blocking, but not proven broken under current evidence. Urgency: schedule remediation or investigation soon; do not let it become untracked backlog. Next Keystone module: usually `research` to verify unknowns, `breakdown` to plan multi-step remediation, or `build` for contained repairs.
- **Info:** Healthy signal, minor inconsistency, low-impact cleanup, or explicitly unknown/unchecked area. Urgency: no immediate action unless priorities change. Next Keystone module: `no-op` when informational, or `review`/`ship` when the next step is validation rather than repair.

## Modes
- **Project snapshot:** summarize structure, active areas, scripts, tests, CI, docs, and current branch state.
- **Tooling/CI drift audit:** compare manifests, scripts, Make targets, task runners, hooks, CI workflows, matrix versions, cache keys, and required checks against actual files and commands.
- **Docs-vs-reality audit:** compare README, contributor docs, runbooks, release docs, examples, and command snippets with actual repo layout and executable scripts.
- **Config/env rot audit:** inspect templates, `.env.example`, config schemas, secrets documentation, Docker/compose/devcontainer files, SDK/runtime pins, and environment assumptions for staleness or inconsistency.
- **Dependency health audit:** inspect manifests, lockfiles, version pins, deprecated packages, engine/toolchain constraints, known update pressure, and manifest-lock consistency.
- **Test health/flakiness audit:** inspect test commands, skipped/quarantined tests, retries, snapshots, coverage signals, slow/flaky markers, CI-only behavior, and failure history when available.
- **Package/release health audit:** inspect package metadata, allowlists, build artifacts, version/changelog flow, release scripts, publish dry-run support, tags, and multi-target release paths.
- **Instruction/skill drift audit:** inspect project instructions, agent docs, skill/module docs, validator rules, and examples for contradictions or stale references.
- **Release readiness health:** assess project-level risk categories before `ship`, without preparing release artifacts.
- **Risk triage:** rank issues by impact, likelihood, evidence strength, and recommended next module.

## Process
1. Define scope: whole repo, subsystem, tooling, release readiness, dependencies, docs, instructions, or operational process.
2. Confirm read-only posture. Say what will be inspected and avoid state-changing commands unless the user explicitly requested repairs.
3. Inspect before judging: read manifests, scripts, CI, tests, docs, configs, package/release files, instruction files, recent status, and relevant gates.
4. Apply the concrete audit checklists:
   - **Tooling/CI drift:** declared scripts exist; CI calls valid commands; local and CI tool versions align; required checks match current project; generated/cache paths are current; hooks and Make/package targets agree.
   - **Docs-vs-reality:** documented setup/test/build/release commands exist; referenced paths still exist; examples match current APIs/CLIs; screenshots/output snippets are not misleading; contributor docs match workflow.
   - **Config/env rot:** sample env files cover required variables; config names match code; defaults are safe; obsolete variables are not documented as required; runtime/container/dev environment pins are current.
   - **Dependency health:** manifests and lockfiles agree; package managers are not mixed accidentally; runtime engine constraints are plausible; deprecated/abandoned/high-risk dependencies are called out with evidence; update risk is separated from breakage.
   - **Test health/flakiness:** test entrypoints are discoverable; skips/todos/quarantine/retry settings are listed; flaky markers or timing-sensitive tests are noted; coverage signals are reported only if measured; CI-only gaps are identified.
   - **Package/release health:** package allowlists include required files and exclude junk; build artifacts are reproducible or documented; version/changelog/release scripts align; publish dry-run or validation exists; multi-target outputs are accounted for.
   - **Instruction/skill drift:** AGENTS/CLAUDE/GEMINI/Codex/plugin docs and Keystone skill docs agree; module boundaries are current; validators and examples match required headings/behavior.
5. Run safe focused checks when useful and allowed, such as `git status --short`, listing workflow files, reading manifests, `--help`, dry-run validation, or project validators. Avoid install/update/format/fix/publish commands by default.
6. Detect drift mechanically: documentation pointing to missing scripts, scripts referencing missing files, stale generated assets, inconsistent versions, orphaned configs, CI mismatch, package metadata mismatch, or contradictory instructions.
7. For each finding, write the required chain: severity, finding, evidence, impact, confidence, and next Keystone module (`research`, `debug`, `shape`, `breakdown`, `build`, `review`, `ship`, or no-op). Assign severity from the Health priority rubric; do not produce unranked findings. If the finding is about tests or package metadata, still route to one of those modules, usually `build` for repairs, `debug` for failing behavior, `review` for validation, or `ship` for final package readiness.
8. Separate statuses: **broken now**, **risky**, **stale**, **unknown**, and **healthy**. Map broken-now items to Critical unless evidence shows low impact; map risky or stale items to Watch unless release/security impact makes them Critical; map healthy, minor, and unchecked informational notes to Info. Do not convert unknowns into failures.
9. Stop at reporting unless the user explicitly requested fixes. If repairs are requested, route to the appropriate module instead of silently switching modes.

## Subagents and reasoning
Default reasoning: `medium`. Use read-only scout subagents for broad inventory and reviewer subagents for independent risk triage. Use `high` for release readiness, security-sensitive audits, large monorepos, severe tooling drift, instruction drift affecting agent behavior, or when health findings affect go/no-go decisions. Subagents must remain read-only unless repairs are explicitly requested.

## Hard rules
- Read-only by default: no fixing, formatting, dependency updates, cleanup, generation, or config changes unless explicitly requested.
- Health is whole-project/system condition; Review is a specific change. Do not use Health to approve a PR diff.
- Every finding must include severity, finding, evidence, impact, confidence, and next Keystone module.
- Use only the Health priority rubric for severity (`Critical`, `Watch`, `Info`) unless the user explicitly requests equivalent labels; do not emit unranked dumps.
- Evidence categories must be named; unchecked areas must be listed with reasons.
- Do not overstate confidence. Label inferred risks and explain what would verify them.
- Prefer safe read-only or focused validation commands.
- Separate “broken now,” “risky,” “stale,” and “unknown.”
- Health can recommend `ship`, but does not replace ship proof gates.

## Failure modes
- **Audit-as-fix:** making opportunistic changes during a scan.
- **Review confusion:** judging a specific PR/change instead of system condition.
- **Checklist theater:** listing categories without evidence.
- **Evidence gaps:** reporting findings that lack impact, confidence, or next module.
- **False certainty:** declaring healthy because a narrow check passed.
- **Drift blindness:** missing mismatches between docs, scripts, CI, package metadata, instructions, and actual files.
- **Unranked dump:** overwhelming the user with findings but no severity or next module.

## Output format
```markdown
## Health report
Scope: ...
No-fix status: confirmed / repairs requested
Boundary: Health system-condition scan, not Review of a specific change

### Evidence inspected
- ...

### Checklist status
| Checklist | Status | Evidence | Confidence |
|---|---|---|---|
| Tooling/CI drift | ... | ... | ... |
| Docs-vs-reality | ... | ... | ... |
| Config/env rot | ... | ... | ... |
| Dependency health | ... | ... | ... |
| Test health/flakiness | ... | ... | ... |
| Package/release health | ... | ... | ... |
| Instruction/skill drift | ... | ... | ... |

### Health priority rubric
| Severity | Use when | Urgency | Typical next Keystone module |
|---|---|---|---|
| Critical | Broken now, release-blocking, security-sensitive, data-loss-prone, or prevents required project operation | Act before `ship` or before relying on the affected subsystem | `debug` for failing behavior; `build` for repairs; `ship` only for post-fix release gates |
| Watch | Risky, stale, drifting, or likely to become blocking, but not proven broken under current evidence | Schedule investigation/remediation soon | `research`, `breakdown`, or `build` |
| Info | Healthy signal, minor inconsistency, low-impact cleanup, or explicitly unknown/unchecked area | No immediate action unless priorities change | `no-op`, `review`, or `ship` for validation/final gates |

### Findings
1. Critical / Watch / Info — finding
   - Evidence:
   - Impact:
   - Confidence: High / Medium / Low
   - Next Keystone module:

### Checks not run
- ...

### Overall assessment
Healthy / Watch / At risk / Blocked — rationale
```
