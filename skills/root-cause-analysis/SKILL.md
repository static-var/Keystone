---
name: root-cause-analysis
description: Use when the user reports a bug, regression, failing test, error, flaky behavior, unexpected output, broken workflow, suspicious logs, performance anomaly, or asks for RCA/root cause.
---

# Root-Cause Analysis

## Core principle
Find the root cause before fixing. Root-cause analysis is an evidence ladder: observe the failure, reproduce it, minimize it, trace the mechanism, test falsifiable hypotheses, prove the cause, fix narrowly, guard against regression, verify with exact output, and clean up. No guess-and-check, no cargo-cult edits, no shipping/finalization work.

## Load when
Load when the user reports an error, failing test, broken behavior, regression, flaky result, performance anomaly, unexpected output, integration failure, suspicious logs, silent failure, data corruption, or asks to troubleshoot why something happened.

Also load when the task involves:
- deciding whether a failure is local, historical, environmental, data-dependent, timing-dependent, or cross-system;
- diagnosing nondeterminism, race conditions, retries, timeouts, queues, caches, or distributed boundaries;
- interpreting logs/traces/metrics to explain a symptom;
- proving whether a suspected fix actually addresses the cause.

## Not for
- Implementing new behavior unrelated to the failure.
- General code improvements without a reproduced problem.
- Release finalization, merge strategy, or deployment handoff; use `shipping` after proof and review.
- Broad repository audits; use `project-audit`.
- Spec decisions where no failure exists; use `product-planning`.
- Replacing review, test strategy, or gate validation modules.

## Outcome contract
Deliver a root-cause analysis report with:
- symptom, impact, affected users/systems, and failure classification;
- reproduction steps, exact command/input/environment, or why reproduction was not possible;
- minimized failing case when feasible, including what was removed and what still fails;
- evidence gathered through logs, tests, code inspection, history, metrics, traces, or instrumentation;
- hypotheses considered, which were disproven, and the surviving root-cause hypothesis;
- proof that the root cause explains the symptom and predicts observed behavior;
- exact fix made or proposed, scoped to the proven cause;
- regression test, guard, monitor, or explicit reason none is feasible;
- verification commands and exact results/output evidence;
- cleanup performed, temporary diagnostics removed, and remaining uncertainty or escalation.

Stop only when one of these is true:
- the root cause is proven, the narrow fix is verified, and regression protection is in place or justified;
- reproduction is impossible after documented attempts and the best available evidence has been preserved;
- escalation criteria are met.

## Modes
- **Triage:** classify severity, scope, reproducibility, recency, ownership, and risk before fixing.
- **Reproduce/minimize:** create the smallest reliable case that demonstrates the failure.
- **Instrument/trace:** add temporary logs, probes, traces, assertions, metrics, or diagnostics to observe reality.
- **Hypothesis test:** test one falsifiable explanation at a time and record pass/fail evidence.
- **Fix:** make the smallest change that addresses the proven root cause.
- **Stabilize flaky behavior:** collect repeated runs, isolate nondeterminism, and prove the stabilizing change.
- **Performance investigation:** measure baseline, localize bottleneck, prove causality, then optimize narrowly.
- **Log/silent-failure investigation:** reconstruct the timeline from logs/traces/state when direct failure output is absent.
- **Escalation:** stop local edits and ask for data, access, owner input, incident handling, or risk approval.

## Process
1. **Classify the failure.** Decide whether it is deterministic, flaky, regression, environment-specific, data-dependent, multi-system boundary, performance, silent/log-only, data corruption, security-sensitive, or destructive. Record severity, scope, recency, and owner.
2. **Capture the exact symptom.** Include command, input, error text, expected vs actual, environment, versions, seed/timezone/locale, frequency, affected data, and recent changes.
3. **Reproduce before fixing.** Run the smallest known failing command or scenario. If reproduction is impossible, state the constraint, preserve available evidence, and switch to log/history/data analysis.
4. **Minimize the case.** Reduce inputs, files, flags, mocks, services, data rows, timing windows, browser/device matrix, or integration surface while keeping the failure. Do not minimize away the bug.
5. **Inspect code, data, and history.** Distinguish trigger from cause. If the failure is likely historical, use bisect or targeted history review before guessing.
6. **Trace/instrument narrowly.** Add the smallest temporary diagnostic that can confirm or falsify a hypothesis. Prefer assertions, structured logs, counters, spans, query plans, snapshots, or deterministic seeds over broad logging.
7. **Form falsifiable hypotheses.** A good hypothesis names a mechanism and prediction. Test one at a time. Record disproven hypotheses instead of silently abandoning them.
8. **Prove the root cause.** Show that the cause explains the symptom, reproduces or predicts the failure, and that removing/changing the cause removes the failure. Symptoms alone are not proof.
9. **Fix narrowly.** When this branch will mutate files, load and pass `../_shared/gates/isolation.md`, then load `../_shared/gates/red.md` and satisfy its observed-red or exception contract before the fix. Change only what the proven cause requires.
10. **Add a regression guard.** Prefer a failing-before/passing-after test. If impractical, add an assertion, monitor, fixture, replay, seed, contract test, migration check, or documented manual proof.
11. **Verify with exact output.** For a mutated fix, load and pass `../_shared/gates/proof.md`; run focused verification first, then broader commands if risk warrants.
12. **Clean up.** Remove temporary diagnostics, revert failed experiments, leave useful permanent observability only when justified, and report remaining uncertainty.

Branch checklists:
- **Cannot reproduce:** verify environment/input parity, collect logs/traces/state, check recent changes, ask for missing data, and escalate if blocked.
- **Historical regression:** establish known-good and known-bad revisions with the same command/data/environment; use side-effect-safe bisect only after reproduction is deterministic enough; prove the mechanism in current code before treating the first bad commit as root cause.
- **Flaky/race:** run 20/50/100 iterations as risk warrants; vary order, parallelism, clock, seed, async waits, network, cache, filesystem, and shared state; beware instrumentation changing timing.
- **Service boundary:** trace correlation/request IDs; compare contracts, schemas, auth, encoding, idempotency, retries, timeout budgets, and partial failures; identify the first system that diverges.
- **Performance:** measure baseline and bad metric; localize CPU, memory, IO, network, DB, lock contention, rendering, bundle size, or algorithmic complexity; prove the fix changes that bottleneck.
- **Logs/silent failure:** reconstruct a timeline from logs, traces, metrics, state transitions, audit records, and exit codes; check swallowed exceptions, ignored returns, missing awaits, nonzero exits, dropped events, sampling, and log-level/config differences.
- **Data corruption:** freeze destructive actions, preserve samples, identify source of truth, writer/read path, migrations/backfills/imports, concurrency, validation, serialization, timezone/locale, precision, blast radius, and rollback safety.

Good/bad hypotheses:
- **Good:** “The checkout total is doubled because retrying `capturePayment` replays a non-idempotent side effect; if true, two calls with the same request ID will create two ledger rows.”
- **Bad:** “Payments are broken.”
- **Good:** “The test flakes because it asserts before the debounce timer fires; if true, using fake timers or awaiting the debounce settles it across 100 runs.”
- **Bad:** “Probably async weirdness.”
- **Good:** “The query slowed after commit X because the new filter prevents index `idx_orders_account_created` from being used; if true, `EXPLAIN` will show a sequential scan and restoring the predicate shape will restore the plan.”
- **Bad:** “The database is slow.”

Good/bad minimization:
- **Good:** Reduce a failing import from a production-sized CSV to three rows that preserve the bad encoding, duplicate key, and null timestamp that trigger the failure.
- **Bad:** Replace the import with a mock that no longer exercises parsing, deduplication, or timestamp handling.
- **Good:** Reduce a browser failure to one route, one viewport, one user role, and one API response fixture while keeping the visible defect.
- **Bad:** Disable authentication, caching, and the API client so the boundary bug disappears.
- **Good:** For a flaky test, run the same test alone, in file order, shuffled, with fixed seed, and in parallel to identify the minimal timing/order dependency.
- **Bad:** Add arbitrary sleeps until the failure stops appearing once.

Escalation/stuck criteria:
- Escalate after **three disproven hypotheses** without a stronger next test.
- Escalate when there is **no reproduction** and required logs/data/access are unavailable.
- Escalate immediately for destructive actions, data-loss risk, security/privacy exposure, production incident impact, legal/compliance concerns, or uncertain repair of corrupted data.
- Escalate when the next diagnostic requires credentials, production data, high-cost infrastructure, schema/data mutation, or owner approval.
- Escalation output must include symptom, impact, attempts, disproven hypotheses, missing evidence, requested help/access, and safest next action.

## Subagents and reasoning
Use subagents for independent root-cause analysis, log review, performance profile interpretation, bisect planning, or hypothesis generation when the active host exposes safe delegation. Use deeper analysis for intermittent, cross-system, security, performance, data-loss, privacy, destructive, or production-impacting failures. When delegation is available, encode required evidence depth and risk standard in the prompt.

Subagents may inspect and reason independently, but fixes should converge on one evidence-backed root cause. Ask subagents for competing hypotheses and evidence gaps, not broad code review. When subagents disagree, run the smallest test that distinguishes their explanations. Do not let parallel analysis become parallel guess-and-check edits.

## Hard rules
- No fix before evidence supports the root cause.
- No “try this” edits unless explicitly labeled as diagnostic experiments and reverted if disproven.
- Symptoms are not root causes; keep asking what mechanism produced the symptom.
- One hypothesis per experiment; record the prediction and result.
- Three disproven hypotheses without progress triggers escalation or a new evidence source.
- Regression coverage is required when practical; if impractical, explain why and provide alternate proof.
- Temporary instrumentation must be removed or clearly documented before handoff.
- Do not declare fixed without command output, exact output proof, metric delta, trace evidence, or equivalent verification evidence.
- Do not broaden scope into feature work, refactoring, shipping, finalization, or unrelated cleanup.
- For data-loss/security/destructive risk, preserve evidence and escalate before mutation.

## Failure modes
- **Guess-and-check spiral:** changing code until symptoms disappear without knowing why.
- **Confirmation bias:** keeping the first hypothesis despite contradictory evidence.
- **No-op advice:** saying “check logs,” “add tests,” or “investigate further” without specifying which evidence, command, owner, or stop condition.
- **Overbroad fix:** refactoring or redesigning more than the failure requires.
- **Unreproducible confidence:** claiming success from one weak signal on flaky behavior.
- **Minimization that removes the bug:** simplifying the case until the relevant boundary, data shape, or timing condition disappears.
- **Instrumentation Heisenbug:** diagnostics change timing, ordering, load, or state enough to hide the failure.
- **First-bad-commit tunnel vision:** assuming bisect output is the mechanism without proof.
- **Boundary blame ping-pong:** assuming another service owns the issue without request-level evidence.
- **Diagnostic litter:** leaving logs, probes, sleeps, flags, generated data, or diagnosis-only state behind.

## Output format
```markdown
## Root-Cause Analysis report
Symptom: ...
Impact/scope: ...
Failure classification: ...
Stop condition: fixed / blocked / escalated ...

### Reproduction
- Steps/command: ...
- Environment/input: ...
- Frequency: ...
- Minimal case: ...

### Evidence and root cause
- Evidence ladder:
  1. Observation: ...
  2. Trace/minimization: ...
  3. Hypothesis test: ...
  4. Proof: ...
- Disproven hypotheses: ...
- Root cause: ...

### Fix
- Changed: ...
- Why this addresses the cause: ...
- Scope intentionally not changed: ...

### Regression protection
- Test/guard: ...
- Failing-before/passing-after proof or alternate guard: ...

### Verification
- Command/result: ...
- Exact output proof: ...

### Cleanup / remaining uncertainty
- Temporary diagnostics removed: ...
- Remaining risk/uncertainty: ...
- Escalation needed, if any: ...

### Checkpoint
Use the required fields from `../_shared/gates/checkpoint.md`.

```
