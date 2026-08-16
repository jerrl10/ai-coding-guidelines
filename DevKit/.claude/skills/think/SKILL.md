---
name: think
description: "Use this skill at the start of EVERY ticket to produce a plan.md before any code is written — bug fixes, features, refactors, migrations, anything beyond a single-line doc/comment fix. The agent MUST invoke this skill explicitly. No code changes, no file edits, no implementation work happens before plan.md exists and Gate #1 is cleared."
---

# think

Structured reasoning before code. Produces `plan.md` as the Gate #1 document.

## When to load

**The agent MUST invoke this skill explicitly at the start of EVERY ticket.**

No exceptions except: pure documentation typos, single-line comment fixes, or markdown formatting changes.

**Hard rule: Zero file writes occur before `plan.md` is created and Gate #1 is cleared.**

If the user says "implement the ticket", "fix this", "do this work", or any variant — the first action is `skill: think`. Not research. Not file reads for implementation. Not code changes. The plan comes first.

## Job

Produce `.agent/tickets/<ticket-id>/plan.md` — a 30-second go/no-go document for the human reviewer at Gate #1. The plan is the agent's thesis about the ticket: what the problem is, what approach will solve it, what files will change, what assumptions are in play.

## Codebase exploration

Before drafting plan.md, if the ticket requires more than trivial codebase context, delegate exploration to a subagent rather than reading widely in the main context. This preserves the main agent's context window for the implementation phase.

Two options, in order of preference:

1. **Built-in Plan subagent** — already specialized for plan-mode research. Invoke explicitly:

   > Use the Plan subagent to explore the codebase for ticket `<ticket-id>`. Focus on: `<specific area>`. Return: file paths likely to change, relevant existing patterns, and any constraints discovered.

   The Plan subagent returns research findings without preloading CLAUDE.md (kept fast and cheap). Its findings are read in the main agent's full-CLAUDE.md context, so harness rules still apply when interpreting the results.

2. **Built-in Explore subagent** — for narrower, read-only file discovery (e.g., "find all callers of `parseToken`"). Use when the question is specifically about codebase structure, not about strategic planning.

Skip exploration entirely for trivial tickets (single-file changes, doc edits, small refactors with obvious scope). Plan.md goes straight to drafting.

**Don't manually read 10+ files in the main context.** That's the failure mode this delegation exists to prevent.

## Output

- File: `.agent/tickets/<ticket-id>/plan.md` — follows `plan-template.md` in this skill dir.
- Side effect: post a comment on the GitHub issue linking to the plan. For 🟡 or 🔴 risk, wait for human acknowledgement before proceeding. For 🟢, may proceed after posting.

## Rules

**Length:** target 200 words, hard cap 400. If you cannot fit the plan in 400 words, the ticket is too big — halt and propose splitting.

**Problem in your own words:** the "Problem" section must be a restatement of the ticket in your own words. Copy-pasting the ticket text verbatim is not acceptable — it indicates you haven't thought about the problem. If you cannot restate the problem, halt and escalate.

**Approach must name files:** the "Approach" section must reference at least one specific file or function. Vague approaches like "refactor the auth layer" or "clean up the API" fail Gate #1.

**Files expected to change is a list, not prose:** one bullet per path with a one-phrase description of what changes. This list feeds the OWNERSHIP check and is compared to the actual diff at PR time.

**Assumptions and Blockers are distinct:**

- Assumption = "I think X, will proceed until proven wrong. Verify by Y."
- Blocker = "I can't proceed without an answer to X."

If there are non-empty Blockers, do not start coding. Escalate.

**OWNERSHIP check is mandatory:** run the classification from the `safe-edit` rule against every path in the Files list. List any `review`-tier or `forbidden` paths in the OWNERSHIP check section. If any path is `forbidden`, halt the plan and load `escalation`.

**Confidence:** single `cs` score (0–10) on the overall plan. If `cs < 5`, explain the uncertainty in one sentence.

**Tests planned:** must be non-empty for bug fixes and features. If no tests are planned, `test-first` will block at implementation time — address it in the plan, not after.

**Out of scope is explicit:** list what this plan deliberately does not do, that a reader might otherwise expect.

## Gate #1 protocol (risk-tiered)

After writing `plan.md`:

1. Determine risk using the hardcoded rubric (see the `risk-rubric` rule in `CLAUDE.md`).
2. Post a comment on the GitHub issue linking to the plan and stating the risk label.
3. If 🟢: proceed to implementation immediately after posting.
4. If 🟡 or 🔴: wait for explicit human acknowledgement (GitHub reaction, comment approval, or explicit sign-off). Do not start implementation without it.

Timeout for 🟡/🔴: configurable per project, default 30 minutes of business hours. On timeout, load `handoff` with trigger `blocker` and stop.

## Plan changelog

`plan.md` includes an append-only changelog at the bottom. Any material change to the plan mid-ticket adds a changelog entry and re-opens Gate #1:

- **Material** (re-gate): approach changed, new review-tier path added, scope class changed (small → medium), new assumption.
- **Trivial** (no re-gate): added one file to the list, reworded problem statement, fixed a typo.

## Failure mode

- Problem restatement identical to ticket text → refuse, prompt agent to read the ticket and articulate in own words.
- Approach has no named file → refuse, load `reproduce` (if bug) or do more codebase reconnaissance.
- Blockers non-empty → do not write plan. Load `escalation` with the blockers.
- OWNERSHIP check finds a forbidden path in the Files list → halt plan. Load `escalation` to produce a draft-patch proposal for the forbidden path.

## See also

- `plan-template.md` in this skill dir
- `test-first`, `escalation`, `pr-hygiene` skills
- `safe-edit` rule (in `CLAUDE.md`) — pre-write OWNERSHIP classification
- `planning-required` rule (in `CLAUDE.md`) — enforces this skill being invoked before any implementation write
- `adr-loader` skill — surfaces relevant ADRs before planning; `plan.md` should explicitly note which ADRs the plan follows or contradicts
- `adr-author` skill — if the plan introduces a new architectural decision, propose an ADR before implementing
- `.agent/PROJECT.md` , `.agent/OWNERSHIP.md`, `.agent/LEARNINGS.md` in the target repo
- `doc/adr/` in the target repo (ADR repository)
