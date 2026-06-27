# Review Gate

## Purpose
Confirm work has received the required review before finalization.

Review is evidence, not a feeling. This gate separates blocking findings from non-blocking follow-ups and prevents shipping work that has only been self-approved.

## Required checks
1. Identify required review type:
   - Human reviewer, automated reviewer, domain owner, security review, design review, or read-only review pointer.
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

## Read-only review pointer
When review cannot be performed by the worker, leave a read-only pointer that lets a reviewer inspect without changing work:

```text
Review requested for: <branch/worktree/PR/diff>
Scope: <requested change>
Changed files: <files>
Proof: <commands and results>
Known gaps: <unverified items>
Please classify findings as BLOCKER or NON-BLOCKER.
```

## Pass condition
Pass only when review evidence exists and no blocking findings remain unresolved, or the user explicitly accepts the remaining blockers.

## Fail action
Return to the appropriate module or gate. Do not ship while blockers are open.

```text
Review Gate: FAIL
Review source: <human/tool/pending>
Evidence: <link/output/comment or "none">
Blockers: <list>
Non-blockers: <list>
Required next action: <fix, re-review, user acceptance, or request review>
Read-only review pointer: <branch/PR/diff path if review is pending>
```