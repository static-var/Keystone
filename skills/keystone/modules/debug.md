# Keystone Debug Module

## Core principle
Find the root cause before fixing. Debugging is an evidence ladder: observe the failure, reproduce it, minimize it, trace the mechanism, test falsifiable hypotheses, prove the cause, fix narrowly, guard against regression, verify with exact output, and clean up. No guess-and-check, no cargo-cult edits, no shipping/finalization work.

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
- Shipping, release finalization, merge strategy, or deployment handoff; use `ship` after proof/review.
- Broad repository audits; use `health`.
- Spec decisions where no failure exists; use `shape`.
- Replacing review, test strategy, or gate validation modules.

## Outcome contract
Deliver a debug report with:
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
9. **Fix narrowly.** Change only the code/config/data handling required by the proven cause. Avoid opportunistic refactors, rewrites, or unrelated cleanup.
10. **Add a regression guard.** Prefer a failing-before/passing-after test. If impractical, add an assertion, monitor, fixture, replay, seed, contract test, migration check, or documented manual proof.
11. **Verify with exact output.** Run focused verification first, then broader commands if risk warrants. Capture command names and result snippets, not just “tests pass.”
12. **Clean up.** Remove temporary diagnostics, revert failed experiments, leave useful permanent observability only when justified, and report remaining uncertainty.

Debug decision tree / failure classification:
- **Cannot reproduce?** Verify environment/input parity, collect logs/traces/state, check recent changes, ask for missing data, and escalate if still blocked.
- **Reproduces reliably now but worked before?** Treat as historical regression; run targeted history review or bisect.
- **Fails intermittently?** Treat as flaky/race; run many iterations, fix seed/time/timezone/network where possible, and look for shared state, ordering, async waits, retries, clocks, locks, caches, and resource leaks.
- **Fails at a service boundary?** Trace request IDs across systems, compare contracts, schemas, auth, serialization, retries, timeouts, idempotency, and partial failure handling.
- **Slow or resource-heavy?** Measure before changing, identify the bounded bottleneck, compare profiles/plans/metrics, and prove the optimization changes the measured bottleneck.
- **Only logs show failure or behavior is silent?** Reconstruct timeline from logs, traces, metrics, state transitions, audit records, and exit codes; add diagnostics only to close evidence gaps.
- **Data is wrong or corrupted?** Freeze destructive actions, preserve samples, identify writer/read path, migration/import history, concurrency, validation gaps, and blast radius before fixing.

Operational playbook:
- **Reproduce:** exact command/input/environment; note frequency and baseline output.
- **Minimize:** remove variables until the smallest failing case remains; document removed variables.
- **Trace/instrument:** observe the suspected mechanism with scoped, reversible diagnostics.
- **Hypothesize:** write falsifiable mechanism + prediction; test one hypothesis per experiment.
- **Prove:** connect evidence to cause; show why alternatives fail or are less likely.
- **Fix narrowly:** edit only the proven mechanism.
- **Regression guard:** create failing-before/passing-after proof or equivalent guard.
- **Cleanup:** remove debug litter and failed experiments; keep only justified observability.

Bisect strategy when historical regression is likely:
- Establish one known-good and one known-bad revision using the same command, data, and environment.
- Make the reproduction deterministic enough for `git bisect`; if flaky, use a looped script with a clear pass/fail threshold.
- Keep the bisect command side-effect safe; reset generated files between runs.
- When bisect identifies a commit, inspect the diff for mechanism and still prove causality in current code.
- Do not treat the first bad commit as the root cause until the mechanism explains the symptom.

Scenario checklists:
- **Regression:** What changed? Is there a known-good revision? Can the same command prove good vs bad? Is the failing behavior tied to code, dependency, config, data, or environment?
- **Flaky test/race:** How often does it fail over 20/50/100 runs? Does order, parallelism, clock, seed, async wait, network, cache, filesystem, or shared state affect it? Does instrumentation change timing?
- **Multi-system boundary:** What is the correlation/request ID? Which system first diverges from expected state? Are contracts, schemas, auth, encoding, idempotency, retries, timeout budgets, and partial failures aligned?
- **Performance:** What metric is bad and by how much? What is the baseline? Is the bottleneck CPU, memory, IO, network, DB, lock contention, rendering, bundle size, or algorithmic complexity? Does the fix improve that metric?
- **Logs/silent failure:** What timeline do logs/traces/metrics imply? Are there swallowed exceptions, ignored return values, missing awaits, nonzero exits, dropped events, sampling gaps, or log-level/config differences?
- **Data corruption:** What data is affected? Is the source of truth known? Which writer last touched it? Are migrations, backfills, imports, concurrent writes, validation, serialization, timezone/locale, or precision involved? Is rollback/destructive repair safe?

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
Default reasoning: `high`. Use oracle/debug subagents for independent root-cause analysis, log review, performance profile interpretation, bisect planning, or hypothesis generation. Use `xhigh` for intermittent, cross-system, security, performance, data-loss, privacy, destructive, or production-impacting failures.

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
- **Diagnostic litter:** leaving logs, probes, sleeps, flags, generated data, or debug-only state behind.

## Output format
```markdown
## Debug report
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
```
