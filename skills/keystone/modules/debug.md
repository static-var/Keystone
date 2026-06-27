# Keystone Debug Module

## Core principle
Find the root cause before fixing. Reproduce, minimize, instrument, hypothesize, prove, fix narrowly, add regression coverage, verify, and clean up. No guessing.

## Load when
Load when the user reports an error, failing test, broken behavior, regression, flaky result, performance anomaly, unexpected output, integration failure, or asks to troubleshoot why something happened.

## Not for
- Implementing new behavior unrelated to the failure.
- General code improvements without a reproduced problem.
- Shipping or release finalization; use `ship` after proof/review.
- Broad repository audits; use `health`.
- Spec decisions where no failure exists; use `shape`.

## Outcome contract
Deliver a debug report with:
- symptom and impact;
- reproduction steps or why reproduction was not possible;
- minimized failing case when feasible;
- evidence gathered through logs, tests, code inspection, or instrumentation;
- root cause hypothesis and proof;
- exact fix made or proposed;
- regression test or guard;
- verification commands and results;
- cleanup performed and remaining uncertainty.

## Modes
- **Triage:** classify severity, scope, reproducibility, and likely owner without fixing yet.
- **Reproduce/minimize:** create the smallest reliable case that demonstrates the failure.
- **Instrument:** add temporary logs, probes, traces, assertions, or diagnostics to observe reality.
- **Fix:** make the smallest change that addresses the proven root cause.
- **Stabilize flaky behavior:** collect multiple runs, isolate nondeterminism, and prove the stabilizing change.

## Process
1. Capture the exact symptom: command, error, expected vs actual, environment, frequency, and recent changes.
2. Reproduce before fixing. If reproduction is impossible, state the constraint and gather the best available evidence.
3. Minimize the case: reduce inputs, files, flags, data, timing, or integration surface until the signal is clear.
4. Inspect relevant code and history. Distinguish triggering conditions from root cause.
5. Instrument only enough to answer a hypothesis. Keep diagnostics scoped and removable.
6. Form hypotheses and test them one at a time. Prefer falsifiable checks over broad edits.
7. Fix the proven cause narrowly. Do not opportunistically refactor unrelated code.
8. Add or update a regression test/guard that fails before the fix and passes after, when feasible.
9. Verify with focused commands, then broader commands if risk warrants.
10. Remove temporary diagnostics and report residual risks.

## Subagents and reasoning
Default reasoning: `high`. Use oracle/debug subagents for independent root-cause analysis, log review, or hypothesis generation. Use `xhigh` for intermittent, cross-system, security, performance, data-loss, or production-impacting failures. Subagents may inspect and reason independently, but fixes should converge on one evidence-backed root cause.

## Hard rules
- No fix before evidence supports the root cause.
- No “try this” edits unless explicitly labeled as diagnostic experiments and reverted if disproven.
- Symptoms are not root causes; keep asking what mechanism produced the symptom.
- Regression coverage is required when practical; if impractical, explain why and provide alternate proof.
- Temporary instrumentation must be removed or clearly documented before handoff.
- Do not declare fixed without command output or equivalent verification evidence.

## Failure modes
- **Guess-and-check spiral:** changing code until symptoms disappear without knowing why.
- **Confirmation bias:** keeping the first hypothesis despite contradictory evidence.
- **Overbroad fix:** refactoring or redesigning more than the failure requires.
- **Unreproducible confidence:** claiming success from one weak signal on flaky behavior.
- **Diagnostic litter:** leaving logs, probes, or debug-only state behind.

## Output format
```markdown
## Debug report
Symptom: ...
Impact/scope: ...

### Reproduction
- Steps/command: ...
- Minimal case: ...

### Evidence and root cause
- Evidence: ...
- Root cause: ...

### Fix
- Changed: ...
- Why this addresses the cause: ...

### Regression protection
- Test/guard: ...

### Verification
- Command/result: ...

### Cleanup / remaining uncertainty
- ...
```
