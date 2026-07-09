# Red Gate

## Purpose
Establish a meaningful failing signal before implementation when practical.

This file owns red-signal pass/fail and its exception. Mutation and diagnosis skills choose the behavior-specific signal; they do not redefine the exception contract.

The red signal proves the current system lacks the desired behavior and that the chosen check can detect the fix. It is binary: either a red-capable check exists, or an explicit alternative proof plan is recorded.

## Required checks
1. State expected behavior in concrete terms.
2. Identify a red-capable check:
   - Test that should fail before the change.
   - Reproduction command or script.
   - Acceptance example with expected/actual output.
   - UI flow that currently shows the defect.
   - Validator that rejects the current artifact.
3. Run the check before implementation when safe and available.
4. For observed red, confirm the failure is meaningful:
   - It fails for the right reason.
   - It would pass after the intended behavior exists.
   - It is not only testing mocks, fixtures, snapshots, or implementation details.
5. If red is skipped, record why it is unsafe, unavailable, or impractical before using a documented red exception.
6. For a skipped-red exception, confirm the alternative proof plan is meaningful:
   - It can verify the intended outcome after implementation.
   - It names exact commands, manual steps, artifacts, or reviewers.
   - It is stronger than a vague promise to inspect later.
7. Preserve the red evidence or exception in notes, test output, or commit/PR description.

## Good red examples
- A unit test expects tax to round half-up and currently receives half-even.
- A browser flow submits an empty required field and currently allows submission.
- A docs validator fails because a required gate file lacks a failure report template.

## Bad red examples
- A test that only checks a mocked service was called.
- A snapshot update with no behavioral assertion.
- A failing linter unrelated to the requested change.
- A test that fails because the test setup is broken.

## When red is impractical
Red may be impractical for copy-only changes, emergency fixes, unavailable environments, non-deterministic external systems, or when writing the check would exceed the change risk.

If red is skipped, name the reason and substitute a stronger proof plan:
- targeted validator,
- manual reproduction steps,
- review checklist,
- before/after artifact comparison,
- deploy-preview or staging verification.

## Pass condition
Pass only when either:
- a meaningful red-capable signal was observed before implementation, or
- running red was explicitly unsafe/unavailable/impractical, the reason is recorded, and an alternative proof plan is concrete enough to verify the outcome later.

## Fail action
Do not proceed as if behavior is proven. Stop or record the exception before implementation.

```text
Red Gate: FAIL
Expected behavior: <specific outcome>
Proposed red check: <test/repro/validator/manual flow>
Why it is not usable: <reason>
Risk of skipping red: <what could regress or remain unproven>
Alternative proof plan: <exact post-change evidence required>
```
