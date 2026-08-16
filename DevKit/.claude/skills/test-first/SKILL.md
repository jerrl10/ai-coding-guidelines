---
name: test-first
description: "Use this skill whenever the agent is about to write a bug fix, add a feature, or modify behavior covered by tests. Writes a failing test BEFORE writing the fix. If the test passes before the fix is written, the test is wrong. Forces honest test-driven discipline. Skip only when the change has no testable behavior (pure documentation, type-only changes, comment edits)."
---
# test-first

Write a failing test before writing a fix or feature. Ensures tests actually prove what they claim.

## When to load

Load when the agent is about to implement a bug fix or a feature. Runs before any source-code write.

## Job

For bug fixes:
1. Write a test that reproduces the reported bug.
2. Run the test. Confirm it fails *for the right reason* (the reason described in the ticket, not an unrelated error).
3. Implement the fix.
4. Run the test again. Confirm it passes.

For features:
1. Write a test that exercises the new behavior.
2. Run the test. Confirm it fails (missing functionality).
3. Implement.
4. Run the test. Confirm it passes.

## Output

- Test file(s) added to the diff.
- Test names listed in `plan.md` under "Tests planned" (should already be there from `think`).
- After implementation: all tests green in the local run.

## Rules

**Failing-first is mandatory for bug fixes.** A passing test written alongside the fix does not prove it covers the bug. If the test passes before the fix, it's testing the wrong thing.

**Right reason for failure:** the test should fail with an assertion that reflects the reported behavior. A test that fails because of a syntax error, missing import, or wrong setup doesn't count — fix that first, then confirm the assertion itself fails.

**Use the project's test runner.** Read `STACK.md` for the declared runner. Do not introduce a new test runner without explicit human approval.

**Test file location follows project conventions.** Look at existing tests near the code being changed. Match that pattern.

**One test per bug, minimum.** If the bug has multiple failure modes (e.g., happy path works, edge case broken), write one test per mode. Coverage here prevents regression later.

**For untestable layers:** if the bug is in code that genuinely cannot be isolated into a test (e.g., a build-time script, a visual-only rendering bug with no assertion surface), fall back to a manual repro script in `plan.md` under Reproduction, and flag the testability debt in `LEARNINGS.md` at ticket close. Do not skip the test silently.

## Failure mode

**Cannot write a test that fails for the right reason:**
- Either the bug isn't reproducible (escalate — maybe the ticket is wrong).
- Or the codebase isn't testable at that layer (fall back to manual repro, flag debt).

**Test passes before the fix is written:**
- The test is wrong. Rewrite it until it fails for the right reason. Do not implement the fix.

**Integration test needed but test env can't reach dependencies:**
- Record as a blocker in `plan.md`. Ask for test-env access (via human). Don't mock things that shouldn't be mocked.

## Interaction with pr-hygiene

`pr-hygiene` blocks PR open if the Tests.Added section is empty on a bug fix. If a ticket genuinely has no testable change (pure doc update, comment fix), `test-first` doesn't fire and `pr-hygiene` recognizes the non-code-change case.

## See also

- `plan.md` Tests planned section
- `.agent/STACK.md` for the project's test runner
- `.agent/LEARNINGS.md` (append testability debt entries here)
