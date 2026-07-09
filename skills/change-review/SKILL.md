---
name: change-review
description: Use when the user asks for code review, change review, diff/branch/PR review, regression review, readiness assessment, critique, or blocker finding without edits.
---

# Change Review

## Core principle
Change Review is an independent, read-only attempt to disprove readiness.

Ask two questions at the same time:
1. **Spec axis:** does the work satisfy the stated requirements and acceptance criteria?
2. **Standards axis:** is it secure, correct, maintainable, tested, and safe to operate?

Do not assume changed lines are the blast radius. Trace callers, callees, contracts,
data flow, tests, runtime paths, and user impact before giving a verdict.

## Load when
Load when the user asks for code review, critique, audit, readiness assessment,
release/merge review, security review, regression review, or review of a diff, branch,
PR, patch, migration, fix, plan output, or completed implementation.

Also load when another Keystone skill needs `../_shared/gates/review.md` satisfied before shipping.

## Not for
Do not use Change Review for:
- fixing, refactoring, formatting, or rewriting code
- committing, merging, tagging, publishing, or shipping
- initial implementation planning before a reviewable artifact exists
- open-ended context-survey with no concrete artifact to assess
- debugging where the requested outcome is a fix

If asked to review and fix, review first, stop, and hand findings to `implementation`, `root-cause-analysis`,
`context-survey`, `shipping`, or a human only after explicit permission.

## Outcome contract
A complete review returns:
- verdict: **Block**, **Caution**, or **Looks good**
- findings ordered P0, P1, P2, P3, then Nitpicks
- evidence for every finding: file/line, behavior path, contract, test, log, or doc
- user impact and why the severity is justified
- remediation guidance without applying the fix
- tests that should be added or updated for affected behavior
- scope reviewed, validation run, limitations, and read-only confirmation

The review is incomplete if it only inspects the diff, only comments on style, or
cannot explain how the work behaves at runtime.

## Change Review passes
Perform multiple passes. New evidence from one pass expands later passes.
### Pass 0: scope and baseline
- Identify artifact reviewed: diff, branch, files, release candidate, or plan result.
- Read the user request, issue, spec, acceptance criteria, and claimed completion.
- Check repository status without modifying files.
- Record uncommitted work as context, not cleanup.

### Pass 1: spec compliance
- Compare implementation against explicit requirements and non-goals.
- Check edge cases, error states, and acceptance criteria.
- Separate spec misses from standards concerns.
- Treat a clean implementation of the wrong behavior as a finding.

### Pass 2: correctness and runtime paths
- Trace primary success and failure paths end to end.
- Follow changed functions into helpers, services, adapters, persistence, UI, jobs, and
  serializers.
- Validate inputs, outputs, invariants, state transitions, retries, ordering,
  concurrency assumptions, and error propagation.
- Look for nullability, off-by-one, time, encoding, pagination, caching, idempotency,
  cancellation, and partial-failure issues.

### Pass 3: regression and compatibility
- Identify callers, consumers, and workflows that rely on old behavior.
- Check public APIs, CLIs, schemas, migrations, persisted data, environment variables,
  feature flags, configuration defaults, and documentation.
- Consider rollback, downgrade, mixed-version, and incremental rollout risks.
- Search for tests or fixtures that encode previous behavior.

### Pass 4: security, privacy, and abuse resistance
- Review authentication, authorization, tenancy, secrets, logging, validation,
  injection, XSS, SSRF, path traversal, unsafe deserialization, and RCE surfaces.
- Check whether sensitive data leaks through errors, logs, telemetry, URLs, caches,
  exports, screenshots, or third-party calls.
- Consider malicious users, compromised clients, replay, races, resource exhaustion,
  privilege escalation, and denial of service.

### Pass 5: tests and proof
- Map changed behavior to existing tests.
- Identify missing unit, integration, contract, regression, migration, security,
  accessibility, performance, or end-to-end coverage.
- Prefer behavior assertions over implementation trivia.
- Run focused read-only validation when practical: existing tests, type checks, lint,
  builds, or targeted commands.
- If validation cannot run, state why and what should be run.

### Pass 6: maintainability and architecture
- Assess clarity, cohesion, naming, dependency direction, duplication, complexity,
  observability, and debuggability.
- Check architectural boundaries, local conventions, and API contracts.
- Flag brittle abstractions, hidden coupling, unnecessary cleverness, and premature
  generalization when they create real maintenance risk.

### Pass 7: user impact and final consistency
- Translate technical issues into affected personas, workflows, data, accessibility,
  performance, reliability, and support burden.
- Re-rank findings by blast radius, likelihood, recoverability, and detectability.
- De-duplicate findings, verify evidence, and state limitations honestly.

## Severity rubric
Severity reflects realistic impact, not fix size.

### P0: Critical blocker
Immediate or likely severe harm. Examples:
- data loss, corruption, or irreversible destructive action
- unauthorized access, privilege escalation, secret exposure, or major privacy breach
- production outage or release artifact that cannot safely deploy
- legal/compliance risk with material impact

P0 means do not ship or merge without accountable human acceptance and mitigation.

### P1: Blocking defect
High-impact issue that violates core requirements or creates serious regression risk.
Examples:
- primary workflow broken for a meaningful user segment
- incorrect billing, permissions, persistence, or business logic
- migration or compatibility gap that can break real deployments
- high-risk behavior lacking tests plus a plausible failure mode

P1 normally blocks shipping.

### P2: Important non-blocker or conditional blocker
Material issue with bounded impact, lower likelihood, or workaround. Examples:
- edge case with clear user impact
- moderate-risk test gap
- maintainability issue likely to cause near-term bugs
- weak observability for a risky path

State whether release context makes it blocking.

### P3: Low-risk improvement
Valid concern with limited impact. Examples:
- confusing name or local complexity that slows future work
- minor non-hot-path performance inefficiency
- incomplete docs for non-critical behavior
- small test organization weakness

P3 should not block unless it compounds with related risks.

### Nitpick
Cosmetic, preference-level, or optional feedback: unenforced formatting, wording tweaks,
or style suggestions with no correctness or maintainability impact. Keep nitpicks
separate from severity findings.

## Impact tracing
For each meaningful change, trace:
- **Entry points:** user action, API route, CLI, job, event, hook, or import.
- **Callers:** who invokes this and what assumptions they make.
- **Callees:** helpers, libraries, persistence, network calls, and side effects.
- **Data flow:** input, validation, transformation, storage, serialization, output.
- **Contracts:** types, schemas, public APIs, flags, config, docs, and errors.
- **Runtime paths:** success, failure, retry, timeout, cancellation, concurrency.
- **Tests:** existing coverage, missing assertions, fixtures, mocks, snapshots.
- **Users:** visible behavior, accessibility, performance, reliability, trust.

If tracing leaves uncertainty, gather more read-only evidence or report the limitation.
Do not invent confidence.

## Security and regression checklist
Ask for every non-trivial review:
- Can a user access, modify, infer, or delete data they should not?
- Are authn, authz, tenancy, and ownership checked at the right layer?
- Can untrusted input reach queries, interpreters, shells, paths, templates, redirects,
  or deserializers unsafely?
- Are secrets, tokens, PII, or internal identifiers exposed in logs, errors, telemetry,
  URLs, caches, or client bundles?
- Did defaults, permissions, feature flags, or safeguards become unsafe?
- Are races, duplicate submissions, retries, replay, and out-of-order events safe?
- Can persisted data be corrupted, stranded, or made hard to rollback?
- Are public APIs, stored data, configs, and integrations backward compatible?
- Does failure degrade safely without hidden partial success?
- Are performance, resource use, accessibility, localization, and platform differences
  acceptable for realistic users and abuse?
- Do tests cover the affected behavior and important regression paths?

## Subagents and reasoning
Use read-only subagents for separable risks: security/privacy, test coverage,
architecture/API compatibility, persistence/migration, accessibility/user impact,
performance, concurrency, or release risk. Use deeper analysis for security-sensitive,
data-loss, billing, permissions, public API, migration, or cross-system reviews. When delegation is available, encode required evidence depth and review standard in the prompt.

Subagents must receive the read-only contract and return evidence-backed findings, not
patches. Reconcile duplicates and conflicts before reporting. The primary reviewer
owns final severity and verdict.

## Hard rules
- Read-only: inspect files without editing, formatting, generating, staging, committing, merging, tagging, or publishing them.
- Report issues without silently fixing them.
- Do not run destructive or project-mutating commands.
- Do not rely only on changed lines; inspect impacted code paths and contracts.
- Do not approve solely because tests pass.
- Do not report speculation as fact; mark uncertainty.
- Do not bury blockers under minor comments.
- Do not disguise style preferences as correctness findings.
- Do not omit needed tests when behavior changed.
- Do not satisfy `../_shared/gates/review.md` unless blockers and non-blockers are separated.
- Run the checkpoint gate before the final response; if review passes and delivery/finalization was requested, route to `shipping` or leave an explicit shipping prompt.

## Failure modes
Avoid these anti-patterns:
- **Single-pass skim:** one read of changed lines plus generic comments.
- **Diff tunnel vision:** missing callers, callees, contracts, and user impact.
- **Checklist theater:** naming security/tests without tracing actual risk.
- **Green-test rubber stamp:** assuming current tests prove new behavior.
- **Spec blindness:** judging code quality while requirements are unmet.
- **Standards blindness:** accepting unsafe or fragile code because the narrow spec passes.
- **Severity inflation:** turning preferences into blockers.
- **Severity deflation:** downgrading real user harm because the fix is small.
- **Patch creep:** fixing, refactoring, or committing instead of reviewing.
- **Unowned uncertainty:** failing to state what was not verified.
- **Lost next event:** Change Review passes but never routes or prompts for `shipping` when finalization remains.

## Output format
Worked finding example:
```markdown
### P1
- Missing tenant check on invoice export
  - Evidence: `api/exportInvoice.ts:42` accepts `invoiceId` and loads the invoice without comparing `invoice.accountId` to the authenticated account; `/invoices/:id/export` is reachable by any logged-in user.
  - Impact: A user who guesses another invoice ID can download billing data from a different account, which is a privacy and authorization breach.
  - Recommendation: Enforce tenant ownership before export and return the existing unauthorized response on mismatch.
  - Tests needed: Add an integration test where account A requests account B's invoice and receives 403/no file, plus a happy-path same-account export test.
```

Use this structure:
```markdown
## Verdict
Block | Caution | Looks good

## Scope reviewed
- Artifact reviewed:
- Key files/paths inspected:
- Validation run:
- Review limitations:
- Read-only confirmation: no files changed by this review

## Findings
### P0
- [Title]
  - Evidence:
  - Impact:
  - Recommendation:
  - Tests needed:
### P1
None

### P2
None

### P3
None

## Nitpicks
None

## Tests to add or update
- Behavior:
  - Suggested coverage:
  - Why it matters:
## Handoff
- Blockers:
- Non-blocking follow-up:
- Suggested owner module: implementation, root-cause-analysis, context-survey, shipping, or human

### Checkpoint
Use the required fields from `../_shared/gates/checkpoint.md`.

```

If a severity has no findings, write `None`. Recommendations must be actionable but
must not be applied by Change Review.

## Shared standards

For architecture-sensitive or code-quality-sensitive work, load `../_shared/engineering-standards.md` and apply it as reference, not dogma.
