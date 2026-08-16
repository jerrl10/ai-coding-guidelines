# Plan — #<ticket-id> — <ticket-title>

**Created:** <ISO timestamp>
**Agent:** <agent-id>
**Scope:** small | medium | large
**Risk:** 🟢 low | 🟡 medium | 🔴 high

## Problem

<One to two sentences. What is wrong or what is needed. In your own words, not copy-pasted from the ticket.>

## Reproduction

<For bugs: how the bug was reproduced, with steps. Or "Could not reproduce — halting." Or "N/A — feature request.">

## Root cause

<For bugs: one sentence. What is actually causing the behavior. If unknown: "Not yet isolated — plan is to add logging at <X> to localize." Gate #1 reviewer may redirect.>

## Approach

<Two to four sentences. What you will do, specifically. Name files and functions. Vague plans ("refactor the auth layer") fail Gate #1.>

## Files expected to change

- `path/to/file.ts` — <one-phrase description>
- `path/to/other.test.ts` — <one-phrase description>

## Assumptions

- Assuming X. Will verify by Y. If wrong: Z.

## Blockers

<Empty if none. If non-empty: do not start coding. Escalate.>

## Out of scope

<What this plan deliberately does not do, that a reader might expect.>

## Tests planned

- <test name> — <what it proves>

## OWNERSHIP check

<Review-tier paths this plan touches, with what to check. Empty if none.>
<If a forbidden path is in Files list: halt. Escalation skill takes over.>

## Confidence

**cs<N>** — <one-sentence explanation if cs < 5>

---

## Changelog

- <ISO timestamp> — initial plan
