---
name: learnings-loop
description: "Use this skill at every ticket close (PR merged or ticket closed without merge) to decide whether the ticket taught something worth recording in LEARNINGS.md. 'Nothing learned' is a valid and common outcome — most tickets teach nothing new and padding LEARNINGS.md with non-learnings dilutes its signal. Routes architectural decisions to adr-author instead of LEARNINGS.md. May propose a PROJECT.md edit as a separate PR if the ticket revealed a persistent project-wide truth."
---
# learnings-loop

Append to `LEARNINGS.md` at ticket close if something was learned. Propose `PROJECT.md` edits via PR if a persistent truth was revealed.

## When to load

Load at ticket close (PR merged, or ticket closed without merge). Runs as the last skill in the ticket lifecycle.

## Job

1. Review `plan.md`, `handoff.md`, and PR discussion for surprises, root causes, gotchas.
2. Decide: was anything learned that future agents should know?
3. If yes: append one entry to `LEARNINGS.md`.
4. If no: add a "nothing learned" note to the ticket-close comment.
5. Separately: if the ticket revealed a persistent truth about the project (not a one-time gotcha), propose a `PROJECT.md` edit as a PR.

## Output

- Append to `.agent/LEARNINGS.md` (one entry, format-enforced) — or no append if nothing learned.
- Optional: a separate PR against `PROJECT.md` for persistent truths.
- Update ticket-close comment noting whether an entry was appended.

## Rules

**One entry per ticket maximum.** Pick the most surprising finding. If the ticket taught two things, the less-surprising one probably belongs in `PROJECT.md` Non-obvious conventions or `OWNERSHIP.md`, not `LEARNINGS.md`.

**"Nothing learned" is valid and preferred over padding.** Most tickets teach nothing new. Forced entries dilute the signal. A LEARNINGS.md full of "fixed typo, learned that typos should be avoided" is worse than a short one.

**Entry format is strict. All five fields required:**

```markdown
## <YYYY-MM-DD> | #<ticket> | <one-liner>
- **Root cause:** <one sentence>
- **Fix:** <what was done>
- **Gotcha for next time:** <the actionable warning>
- **Tags:** <from closed vocabulary>
```

If any field cannot be filled, the entry is incomplete and should not be appended. Either complete it or skip with "nothing learned."

**Tags come from the closed vocabulary at the top of `LEARNINGS.md`.** If a genuinely new tag is needed, append the entry with `[suggested tag: <name>]` inline and flag for human to add to the vocabulary. Do not invent tags silently.

**Never edit past entries.** If a prior entry turns out to be wrong, append a new corrective entry referencing it. History matters.

**Never delete.** When `LEARNINGS.md` gets large, archive by year (`LEARNINGS-<YEAR>.md`); current file keeps the active year only.

## PROJECT.md edit proposals

Open a separate PR against `PROJECT.md` only if the ticket revealed something that's **persistently true** about the project, not a one-time incident. Distinction:

- **Persistent truth → PROJECT.md:** "We use pnpm, not npm" · "Checkout is the highest-value path" · "Client prefers boring dependencies."
- **One-time gotcha → LEARNINGS.md:** "Payload migration failed silently in CI on April 15th" · "Session invalidation was missing on password change."

If in doubt, it's a LEARNINGS.md entry.

PRs against `PROJECT.md` follow the same review rules as any other PR (pr-hygiene runs). Keep them small — one change per PR.

## When the learning is architectural

If the ticket revealed not just a gotcha but a **decision worth recording** (we discovered we should use X over Y, we established a pattern, we deprecated an approach), that belongs in an ADR via `adr-author`, not LEARNINGS.md. The split:

- **LEARNINGS.md** — one-time gotchas, debugging insights, environmental quirks. "We hit X and the fix was Y."
- **ADR** — decisions that constrain future tickets. "We choose X over Y because Z."
- **PROJECT.md edit** — persistent truths about the project that aren't decisions per se. "Checkout is now a critical path because we shipped paid plans."

If unsure, default to LEARNINGS.md (cheaper). At ticket close, if `learnings-loop` notices the entry it's about to write reads more like a decision than a gotcha, it should instead propose loading `adr-author` and let that skill produce a `proposed` ADR.

## Cross-checks at ticket close

Before writing the entry, check:

- **Agent-assigned vs reviewer-adjusted risk:** if the plan/PR was 🟢 but reviewer re-labeled 🟡, note the discrepancy. Over time, patterns here reveal whether the agent's risk assessment is drifting.
- **Plan.md Files list vs actual diff:** if the diff added files not in the plan, note why. Unplanned file additions are a signal the agent's reconnaissance was incomplete.
- **Handoff chain length:** a 4+ handoff chain is a sign of thrashing; the learning (if any) is often about the ticket shape rather than the code.

These cross-checks don't necessarily produce LEARNINGS.md entries, but they inform whether the ticket was a clean run or a rough one.

## Failure mode

- **Ticket closed without clear resolution (rolled back, still broken):** note "no learning yet — ticket unresolved" and do not append. If the issue is later resolved, the resolving ticket will produce the learning.
- **Tags cannot be reconciled with vocabulary:** halt append, flag for human to extend vocabulary or reclassify.

## See also

- `.agent/LEARNINGS.md` in the target repo
- `.agent/PROJECT.md` (for edit proposals)
- `plan.md`, `handoff.md` (source material)
- `pr-hygiene` skill (Risk labels and review-tier lists feed into cross-checks)
- `metrics-recorder` skill (runs after this; reads the LEARNINGS.md entry if written, to populate `tags` in the metrics record)
- `adr-author` skill (when the learning is architectural, propose an ADR instead)
