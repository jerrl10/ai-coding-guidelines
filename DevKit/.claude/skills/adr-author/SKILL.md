---
name: adr-author
description: "Use this skill when the plan introduces a new architectural decision — a new dependency, new pattern, new module structure, new external service, or contradicts an existing ADR. Also triggers when the user explicitly asks to record an ADR, or when the agent discovers an established pattern in the codebase that has no existing ADR. Drafts a new ADR via `adrs new` with status 'proposed'. Status transitions to 'accepted' are human-only — the agent never accepts its own ADRs."
---
# adr-author

Propose new ADRs when an architectural decision is being made. Status `proposed` only — humans accept.

## When to load

Load on any of these triggers:

1. **Explicit human request.** User asks to "write an ADR for X" or invokes `/adr` or similar.
2. **plan.md proposes an architectural choice.** The plan introduces a new dependency, new pattern, new module structure, new external service, or change to a previously-decided approach.
3. **Pattern discovery during reproduce or implementation.** The agent encounters an established pattern in the codebase that has no ADR ("we apparently always do X here, no decision recorded").
4. **Contradiction with existing ADR.** The plan or ticket's natural approach conflicts with a currently-accepted ADR. Either the existing ADR needs superseding, or the plan needs adjusting.

Do NOT load this skill for: bug fixes that don't change architecture, refactors within an existing pattern, dependency patch bumps, doc edits.

## Job

1. Confirm the decision is worth recording (not every choice is an architectural decision).
2. Draft an ADR via `adrs new`.
3. Populate Context, Decision, Consequences, and Status (`proposed`).
4. Link from the relevant plan.md or ticket.
5. Notify the human that an ADR is awaiting acceptance.

The agent never accepts an ADR. Status transitions from `proposed` to `accepted` are human-only operations (`adrs status <n> accepted`).

## Output

- A new file in the project's ADR directory (typically `doc/adr/NNNN-<slug>.md`).
- Status: `proposed`.
- Comment on the ticket / PR linking the new ADR.
- Update to plan.md noting which ADR(s) the plan now references.

## What counts as an architectural decision

This is the fuzzy part of the skill. A decision earns an ADR when:

- It will **constrain future tickets** in the project. ("Use Postgres" constrains data work for years; "use `let` instead of `const` here" doesn't.)
- It is **non-trivial to reverse.** Changing a database is hard; changing a function name is not.
- It involves **a real choice between options.** "Use the standard library's HTTP client" isn't a decision if no other option was considered. "Use library X over library Y" is.
- It would surprise a future contributor if undocumented. "Why does this codebase use X?" — if the answer is "we picked X over Y for reason Z", that needs an ADR.

A decision does NOT earn an ADR when:

- It's a local implementation detail (which sort algorithm, which variable name).
- It's the obvious choice everyone would have made.
- It's already covered by an existing accepted ADR (just follow that one).
- It's tentative — the agent is exploring, not deciding. Tentative explorations belong in plan.md, not ADRs.

**Stricter than feels right.** When in doubt, do not propose an ADR. ADRs that pile up dilute the signal of the ones that matter. A project with 200 trivial ADRs is worse than one with 30 meaningful ones.

## Researching alternatives

The Alternatives section is the most research-heavy part of drafting an ADR. Doing the research in the main agent's context burns through the context window.

Delegate alternatives research to the built-in `Explore` subagent:

> Use the Explore subagent to research alternatives to `<the proposed decision>`. Compare against options like `<list of plausible alternatives if known, or "common alternatives in this domain">`. For each, return: name, brief description, key tradeoffs, and a sentence on why a team might pick it. Read-only — no modifications.

The Explore subagent runs on Haiku, is fast and cheap, and has no write tools (safe for research). Its findings come back as a structured list that the main agent uses to draft the Alternatives section.

Skip this delegation if you already know the alternatives well (you've drafted similar ADRs in this project, or the alternatives are obvious). Use it when researching would otherwise mean reading library docs, comparing GitHub stars, or scanning the codebase for existing patterns.

## Drafting the ADR

Use `adrs --ng new --format madr --tags <tags> "<title>"` to scaffold. Then edit the file to fill:

**Title.** Verb-led and specific. "Use PostgreSQL for primary data" beats "Database choice." "Adopt MADR 4.0 for ADR format" beats "ADR format."

**Status.** `proposed`. Always proposed when written by the agent. Never accepted, never anything else.

**Context.** What problem is this decision solving? What constraints exist? What was true before this decision came up? Two to four sentences. The hardest section to write well — vague Context produces meaningless ADRs.

**Decision.** What is being decided. One paragraph, declarative. "We will X" or "We adopt Y." Not "we should consider X."

**Consequences.** What follows from this decision. Both positive (what becomes easier) and negative (what becomes harder, what we accept losing). Include implementation consequences (files affected, ongoing maintenance) and design consequences (what's now ruled in or out).

**Alternatives considered.** Other options and why they were rejected. Without this section, the ADR doesn't actually capture the decision — it just states it. At least one alternative, with a one-sentence reason for rejection.

**Tags.** From the project's closed vocabulary (same as LEARNINGS.md tags). Use `adrs --ng list --tags-list` or check PROJECT.md.

## Linking

If this ADR supersedes a previous one:

```bash
adrs --ng new --format madr --supersedes <N> --tags <tags> "<new title>"
```

This auto-creates the bidirectional link.

If this ADR amends or refines another (without superseding):

```bash
adrs link <new-N> Amends <old-N>
adrs link <new-N> Refines <old-N>
```

Linking is a separate step from creation; do it after the new ADR is drafted.

## Rules

**Always status `proposed`.** The agent never accepts an ADR. This is the gate.

**One ADR per decision.** If a ticket triggers two distinct decisions, draft two ADRs. Do not bundle.

**Never edit accepted ADRs.** If a previously-accepted decision needs revision, that's a supersession (new ADR) not an edit. Editing accepted ADRs erases the historical record.

**Cite the trigger.** The Context section should mention what brought the decision up — "Ticket #412 required X, which forced us to choose between Y and Z." This makes it easier to revisit later.

**Confidence on the alternatives.** If the agent considered options but with low confidence on the comparison, say so explicitly: "We chose X over Y; agent confidence on this comparison: cs5. A human should validate the trade-off."

## Failure mode

**Cannot articulate Context in 2-4 sentences:** halt. The agent doesn't understand what's being decided. Either the trigger was wrong (this isn't an architectural decision), or more reproduction/research is needed first. Do not write a vague ADR.

**Alternatives section would be empty:** halt. If only one option was considered, this isn't a decision — it's a default. Don't manufacture fake alternatives to fill the section.

**`adrs` not installed:** flag and ask the human whether to install or fall back to writing the ADR file directly as markdown in `doc/adr/`. Do not silently skip.

**Ticket is being assigned to revise an existing accepted ADR but the agent isn't sure of the supersession path:** halt and escalate. Supersede chains matter; getting them wrong fragments the history.

## Examples

### Example: clear architectural decision

Plan.md proposes:
> Add Redis for session storage. Currently sessions live in Postgres but reads are slow under load.

`adr-author` triggers. Drafts:

```
Title: Use Redis for session storage
Status: proposed
Context: Session reads from Postgres average 80ms p50, 220ms p99 under load.
  Sessions are read on every authenticated request.
Decision: Move session storage to Redis 7+. Postgres remains the source of truth
  for user records; sessions become a derived cache.
Consequences:
  + Session reads drop to <5ms p99.
  + Reduced load on the primary database.
  - New infrastructure dependency (managed Redis or self-hosted).
  - Cache invalidation on user-record changes is now a concern.
  - Local dev environment grows by one container.
Alternatives considered:
  - Keep Postgres, add a query-level cache: rejected because it adds complexity
    without solving the latency floor.
  - Use Memcached: rejected because Redis offers richer data structures we
    expect to need (rate-limit counters, queue backing).
Tags: data, performance, auth
```

This earns an ADR. Constrains future work, non-trivial to reverse, real alternatives.

### Example: should NOT trigger an ADR

Plan.md proposes:
> Refactor the `formatDate` utility to take a `Date` instead of a string.

This is implementation-level. No real alternatives, no future constraint, easily reversed. `adr-author` should not fire. If somehow triggered, halt at the "alternatives section would be empty" check.

### Example: pattern discovery

During implementation, the agent notices: every API route in `apps/web/src/app/api/` uses a wrapper called `withSession()`. There's no ADR for this pattern.

`adr-author` triggers. Drafts:

```
Title: Wrap authenticated API routes with `withSession()`
Status: proposed
Context: All API routes in apps/web/src/app/api/ that require authentication
  are wrapped with `withSession()`. This pattern is established but has no
  documented decision. Surfacing it as an ADR ensures future routes follow
  the convention and the convention itself is reviewable.
Decision: All authenticated API routes MUST use the `withSession()` wrapper.
  Routes that do not require authentication are exempt and should be in a
  clearly-named subdirectory.
Consequences:
  + Consistent auth handling across routes.
  + Easier to audit which routes require auth.
  - New routes must remember the wrapper; lint rule recommended.
Alternatives considered:
  - Per-route auth checks: rejected, current pattern; superseded by this convention.
  - Middleware-based auth: not used in this codebase due to App Router constraints
    on middleware.
Tags: auth, api, conventions
```

The agent surfaces the existing pattern as a `proposed` ADR. Human can accept (cementing the convention) or reject (declaring the pattern accidental and worth changing).

## See also

- `adr-loader` skill — reads existing ADRs at session start
- `adrs` tool: `https://github.com/joshrotenberg/adrs`
- MADR format: `https://adr.github.io/madr/`
- `.agent/PROJECT.md` (linked ADRs and active concerns)
- `doc/adr/` — ADR repository
