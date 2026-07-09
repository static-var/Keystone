# Ship Gate

## Purpose
Ensure finalization happens only after completed, verified, reviewed work is ready for delivery.

This file owns finalization pass/fail. `shipping` gathers the delivery-specific evidence and executes explicitly authorized mechanics; it does not redefine readiness.

Shipping is a handoff decision. This gate confirms the work can be understood, verified, rolled back, and continued by someone else. It is binary: ready to hand off or not ready.

## Required checks
1. Proof gate status:
   - Evidence commands and results are recorded.
   - Unverified areas are disclosed.
   - Any proof exception is explicit.
2. Review gate status:
   - Review evidence is recorded.
   - Blockers are resolved or explicitly accepted by the user.
   - Non-blockers are listed as follow-ups.
3. Delivery notes:
   - What changed.
   - Why it changed.
   - Files changed.
   - Validation performed.
   - Risks and limitations.
4. Rollback or recovery evidence:
   - Revert commit/PR guidance, feature flag, config rollback, backup path, or "docs-only revert is safe" note.
   - Data migrations, destructive actions, or irreversible steps are called out.
5. Handoff evidence:
   - Next human action, deployment step, release note, PR link, or review pointer.
   - Owners for follow-ups are identified when known.
6. No stealth fix:
   - Do not include unrelated fixes.
   - Do not hide failed checks.
   - Do not silently modify files outside the approved blast radius.

## Good ship note
```text
Changed: Expanded five Keystone gate docs into operational pass/fail gates.
Validation: python3 scripts/validate-keystone.py passed.
Review: Completed self-review plus read-only reviewer pass; no blockers, one non-blocking wording follow-up recorded.
Rollback: Revert this docs-only change; no migration or runtime state.
Follow-ups: Confirm wording matches Keystone doctrine before next release.
```

Pending review is not a passing ship note. If required review is pending, fail this gate and route to `review.md` or the `change-review` skill first.

## Pass condition
Pass only when proof, review, delivery notes, rollback/handoff evidence, and scope compliance are all present.

## Fail action
Stop finalization and route to the missing gate. Do not merge, release, mark complete, or imply production readiness.

```text
Ship Gate: FAIL
Missing proof: <none or details>
Missing review: <none or details>
Missing delivery notes: <none or details>
Rollback/handoff gap: <none or details>
Scope violation or stealth fix risk: <none or details>
Required next action: <which gate or skill to run before shipping>
```
