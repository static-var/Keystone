---
name: shipping
description: Use only when the user explicitly asks to ship, commit, prepare a PR, merge, tag, publish, release, deploy, package, hand off, or finalize already-completed work.
---

# Shipping

## Core principle
Shipping is deterministic finalization for already-completed work. It proves, reviews, packages, and hands off a release or PR; it never sneaks in new implementation or last-mile fixes.

A shipping decision consumes three shared contracts: load `../_shared/gates/proof.md`, `../_shared/gates/review.md`, and `../_shared/gates/ship.md`. Those files own pass/fail; Shipping gathers evidence and performs explicitly authorized delivery mechanics.

If any final check fails, abort shipping and route to an existing Keystone module: `implementation` for contained fixes, `root-cause-analysis` for unexplained failures, `change-review` for unresolved review risk, or `project-audit` for broad release/tooling readiness concerns.

## Load when
Load when the user asks to finish a branch, prepare PR or merge notes, package a release, write changelog/release notes, confirm readiness, hand off completed work, tag/version, prepare deploy notes, validate release candidates, or decide whether work is shippable.

## Not for
- Starting new implementation or sneaking in last-minute fixes.
- Root-cause debugging; use `root-cause-analysis`.
- Fixing test/build/package failures; use `implementation` for contained repairs or `root-cause-analysis` when the cause is unclear.
- General project risk audits; use `project-audit`.
- Reviewing code quality of a specific change; use `change-review`.
- Shaping unfinished requirements; use `product-planning`.
- Bypassing proof, change-review, package, deploy, or human release approvals.

## Outcome contract
Deliver a strict shipping packet that includes:
- current branch/worktree status and cleanliness;
- scope of completed work and explicit non-scope;
- proof gate evidence with commands/artifacts/results;
- review gate evidence or exact pending review status;
- shipping gate evidence including CI/CD status, deploy preview/staging status when applicable, package/release readiness, rollback plan, and handoff actions;
- multi-target package/release notes where applicable;
- changelog/release-note text or summary;
- unresolved risks and go/no-go verdict;
- exact human actions needed next.

## Modes
- **PR handoff:** summarize diff, proof, risks, review status, CI status, and reviewer instructions.
- **Release prep:** verify versioning, changelog, build/package artifacts, environment, approvals, rollback, and release command readiness.
- **Deploy handoff:** verify CI/CD pipeline state, deploy preview or staging evidence, environment/feature flag notes, monitoring, and rollback path.
- **Multi-target package/release:** verify each target separately, such as npm/PyPI/GitHub release/Docker/Homebrew/browser extension/mobile artifact, with versions, artifacts, and dry-run evidence.
- **Integration finish:** prepare merge guidance, branch cleanup, post-merge checks, and follow-up owner actions.
- **Delivery packet:** produce final stakeholder notes without changing code.
- **Readiness verdict:** say Shipping / Do not ship / Shipping with risk, backed by gate evidence.

## Process
1. Confirm implementation is complete. If new behavior, fixes, migrations, or cleanup are still needed, stop and route to `implementation` or `root-cause-analysis` before shipping.
2. Inspect branch/worktree state: branch name, base branch, dirty files, untracked files, commits/diff summary, and whether unrelated changes are present.
3. Define the required gates for this change:
   - Load the shared proof, review, and ship gates and identify the evidence each requires for this delivery mode.
4. Run or cite verification evidence. Do not claim passing checks you did not observe. Include command, context, result, and timestamp/context when useful.
5. Check CI/CD awareness: list relevant workflows/pipelines, required checks, latest known status, deploy preview URL or staging environment if available, and any checks not observable locally.
6. Check package/release readiness when applicable: version, changelog, artifact names, package contents, checksums/digests, dry-run output, target registries/platforms, compatibility notes, migration steps, and signing/notarization needs.
7. For multi-target releases, create one evidence row per target. A green web build does not prove a CLI package, Docker image, mobile binary, or plugin package is ready.
8. Confirm rollback and recovery: revert plan, previous version, feature flag/kill switch, database rollback/migration constraints, artifact rollback, owner, and monitoring signals.
9. Prepare PR handoff or release packet: concise summary, scope/non-scope, proof/review/shipping gates, risks, rollout, rollback, and next human actions.
10. Evaluate `../_shared/gates/ship.md`. If it or a prerequisite gate fails, abort finalization, include the failed evidence, and route to the correct module.
11. Run the checkpoint gate and end with a clear verdict: Shipping, Do not ship, or Shipping with risk. If any gate is missing, the checkpoint action is not `stop`; route or prompt for the next required module/check.

## Subagents and reasoning
Use subagents for bounded release-note drafting, checklist verification, artifact inspection, CI/CD status inspection, package manifest review, or independent review of the shipping packet when the active host exposes safe delegation. Use deeper analysis for multi-platform packaging, production releases, security-sensitive changes, migrations, deploys with customer impact, or unresolved release risk. When delegation is available, encode required evidence depth and release standard in the prompt. Subagents must not introduce new implementation.

## Hard rules
- No new implementation in shipping mode. Gate failures create a handoff, not stealth fixes.
- Enforce proof, change-review, and shipping gates. Do not collapse them into one vague readiness statement.
- Evidence before assertions: every readiness claim needs command output, artifact proof, CI/CD status, deploy preview/staging proof, or documented review.
- No stealth fixes: if final checks fail, abort and route to `implementation`, `root-cause-analysis`, `change-review`, or `project-audit`.
- Do not bypass review or package gates because the change “looks small.”
- Keep changelog/release notes user- or operator-relevant; avoid dumping raw commit noise.
- State branch name and working tree cleanliness when available.
- If readiness is uncertain, say “Do not ship” or “Shipping with risk,” not “done.”
- Never publish, deploy, tag, merge, or push unless the user explicitly requested that action and the gates support it.
- Run the checkpoint gate before the final response; a shipping packet with missing gates must name the next event instead of sounding final.

## Failure modes
- **Victory lap without proof:** announcing completion before tests/build/review evidence.
- **Last-mile coding:** making new fixes under the cover of release prep.
- **Stealth release:** tagging, publishing, deploying, or merging without explicit approval.
- **CI blindness:** relying only on local checks while required CI/CD, preview, or staging is red or unknown.
- **Single-target tunnel vision:** treating one package/build target as proof for all targets.
- **Rollback omission:** shipping without a practical revert, rollback, or recovery path.
- **Release-note mush:** vague notes that omit impact, migration, rollout, or risk.
- **Dirty handoff:** leaving untracked files, unclear branch state, or hidden manual steps.
- **Gate theater:** listing checks without results or timestamps/context.
- **Terminal ambiguity:** ending with no clear human action, rollback owner, or next Keystone module when shipping is not cleanly complete.

## Output format
```markdown
## Shipping packet
Verdict: Shipping / Do not ship / Shipping with risk
Branch/status: ...
Gate summary: Proof ... / Change Review ... / Shipping ...

### Scope
- Completed: ...
- Not included: ...

### Proof gate
| Evidence | Good/Bad | Result | Notes |
|---|---|---|---|
| Good: `npm test` observed exit 0 on this branch | Good | Pass | Include command/output summary |
| Bad: “tests should pass” without running or CI link | Bad | Missing | Not acceptable evidence |

### Change Review gate
- Good evidence: approved PR review, completed self-review checklist, security/design approval when required.
- Bad evidence: “looks fine,” assumed approval, or stale review from before major changes.
- Status: ...

### Shipping gate
- CI/CD: workflow/status/link or not observable and why.
- Deploy preview/staging: URL/environment/check result or not applicable.
- Package/release targets: versions, artifacts, checksums/digests, dry runs, compatibility notes.
- Rollback plan: exact revert/redeploy/unpublish/feature-flag path and owner.

### Release notes / changelog
- ...

### Risks and aborts
- Failed/missing gates:
- Risks accepted:
- Route if not shippable: implementation / root-cause-analysis / change-review / project-audit

### PR handoff / release packet
- Summary:
- Proof:
- Change Review:
- Rollout:
- Rollback:
- Next human actions:

### Checkpoint
Use the required fields from `../_shared/gates/checkpoint.md`.

```

## Explicit-only finalization

Commit, PR, merge, tag, publish, release, deploy, and destructive cleanup require explicit user request. Preparing notes is allowed; performing the action is not implicit.
