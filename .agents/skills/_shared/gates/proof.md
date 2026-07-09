# Proof Gate

## Purpose
Verify claims with evidence before reporting success.

This file owns evidence pass/fail. Phase skills choose the claim and strongest practical check for their domain; they do not redefine what counts as proof.

This gate rejects vibe-based completion. Code inspection can support a claim, but inspection alone is not proof that behavior works. Proof must connect the intended outcome to observable evidence.

## Required checks
1. Name the claim:
   - What changed?
   - What user-visible or maintainer-visible outcome is now true?
2. Choose evidence that matches the scope:
   - Logic: unit tests, integration tests, property checks, reproduction scripts, or before/after examples.
   - UI: browser/app interaction, screenshots, accessibility checks, visual diff, or manual steps with observed result.
   - Config/build: validation command, dry run, parser/linter, build, deploy preview, or tool output.
   - Docs/content: link/render check, validator, examples that exercise the documented path, or human-readable diff against requirements.
3. Run the strongest practical verification. Prefer the narrowest check that directly exercises the claim; add broader checks when contracts, integration points, public behavior, or regression risk changed.
4. Capture concrete output:
   - Command name.
   - Pass/fail result.
   - Relevant output, screenshot path, or inspected artifact.
5. Disclose gaps:
   - Untested paths.
   - Commands unavailable.
   - Manual assumptions.

## Not proof
- "The code looks right."
- "I updated the file."
- "This should work."
- "No errors in my editor."
- Reviewing a diff without executing or validating the affected behavior.

## Good proof examples
- `pytest tests/test_pricing.py -q` passes and includes the changed rule.
- Browser flow: open checkout, apply discount, observe total updates to `$42`.
- `python3 scripts/validate-keystone.py` passes after editing skill modules.
- Config proof: `terraform plan` exits 0 and shows only expected resource changes.

## Pass condition
Pass only when the success claim is backed by evidence that directly exercises or validates the changed scope, and all known gaps are disclosed.

## Fail action
Do not claim completion. If verification cannot be run, provide a fallback proof plan instead of pretending.

```text
Proof Gate: FAIL
Claim needing proof: <claim>
Attempted evidence: <commands/inspection/manual steps>
Result: <output or blocker>
Unverified risk: <what may still be wrong>
Fallback proof plan: <exact command/manual check/human verification needed>
Completion language allowed: <"implemented, not verified" or "blocked pending proof">
```
