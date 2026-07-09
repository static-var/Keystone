# Review Gate

## Purpose
Confirm work has received the required review before finalization.

Review is evidence, not a feeling. This gate separates blocking findings from non-blocking follow-ups and prevents shipping work that needs independent review.

This gate is binary: pass or fail.

## Required checks
1. Identify required review type:
   - Self-review is sufficient only for docs-only changes, low-risk config, or tiny low-risk refactors with green proof.
   - Independent review is required for security, data, public API, billing/payment, auth/permissions, architecture, migrations, releases, broad refactors, or user-impacting changes.
   - Use a human reviewer, automated reviewer, domain owner, security review, or design review as appropriate.
2. Provide review input:
   - Scope summary.
   - Files changed.
   - Requirements or acceptance criteria.
   - Proof evidence already gathered.
   - Known risks and skipped checks.
3. Capture review evidence:
   - Reviewer name/tool.
   - Date or run identifier.
   - Link, comment, command output, or quoted findings.
4. Separate findings:
   - Blockers: correctness, scope violation, data loss, security, broken verification, missing required proof.
   - Non-blockers: style, cleanup, future refactors, optional docs, nice-to-have tests.
5. Resolve or explicitly accept blockers before shipping.

## Pending review pointer
A pending review pointer is never pass evidence. When review cannot be performed by the worker, leave a pointer that lets a reviewer inspect without changing work:

```text
Review requested for: <branch/worktree/PR/diff>
Scope: <requested change>
Changed files: <files>
Proof: <commands and results>
Known gaps: <unverified items>
Please classify findings as BLOCKER or NON-BLOCKER.
```

## Pass condition
Pass only when required review evidence exists and either no blocking findings remain unresolved, or the user explicitly accepts the remaining blockers.

## Fail action
Return to the appropriate module or gate. Do not ship while blockers are open.

```text
Review Gate: FAIL
Review source: <human/tool/pending>
Evidence: <link/output/comment or "none">
Blockers: <list>
Non-blockers: <list>
Required next action: <fix, re-review, user acceptance, or request review>
Pending review pointer: <branch/PR/diff path if review is pending>
```