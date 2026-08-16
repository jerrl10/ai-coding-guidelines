---
name: adr-loader
description: "Use this skill at the start of every ticket to surface accepted ADRs relevant to the current work. Filters out superseded ADRs by default. Reads doc/adr/ via the `adrs` CLI; falls back to raw markdown if the CLI is not installed. Surfaces decisions as constraints for downstream skills (think, safe-edit, adr-author). Loads PROJECT.md 'Active architectural concerns' entries unconditionally."
---
# adr-loader

Surface architectural decisions relevant to the current ticket. Filters out superseded ADRs by default.

## When to load

Load at session start, after `project-context-loader` and before `triage`. Runs once per session, not per skill invocation.

## Job

1. Find ADRs relevant to the current ticket.
2. Read their decisions and consequences.
3. Filter to currently-effective ADRs (status `accepted`, not superseded).
4. Surface a context summary for downstream skills (`triage`, `think`) and the `safe-edit` rule to reason against.

## Output

A context block, returned to the agent's working memory (not written to disk):

```markdown
## Relevant ADRs

### ADR-0007 — Use PostgreSQL with Drizzle ORM (accepted, 2026-02-15)
**Decision:** All persistent data goes through Drizzle on Postgres 15+.
**Consequence:** New data models go in `packages/db/schema/`. Raw SQL allowed only in migrations.
**Tags:** data, persistence

### ADR-0012 — Server Components by default (accepted, 2026-03-01)
**Decision:** Next.js App Router; Server Components are default; "use client" requires justification.
**Consequence:** New components start as Server Components. Pushing client-side requires a code-comment reason.
**Tags:** frontend, performance

### ADR-0015 — Use JWT for session tokens (proposed, 2026-04-10)
**Status: PROPOSED — may not constrain this ticket.**
**Decision (proposed):** Move from cookie sessions to JWT.
**Tags:** auth, security
```

For tickets where no ADRs are relevant: output `No relevant ADRs found.` and proceed silently.

## Rules

**How to find relevant ADRs:** layered, cheapest first.

1. **Direct pointers in PROJECT.md.** PROJECT.md's "Pointers" or "Active concerns" sections may name specific ADRs. Always load these.
2. **Tag match against ticket keywords.** Run `adrs --ng list --tag <tag>` for tags that appear in the ticket title or body. Common matches: `auth`, `data`, `frontend`, `payments`, `migrations`. The tag vocabulary is shared with LEARNINGS.md.
3. **Full-text search on the ticket body.** Run `adrs search "<key phrases>"` for distinctive nouns from the ticket (component names, library names, feature areas). Skip generic terms.
4. **Path-based match.** If the ticket plan names files under specific paths, match those paths against ADR content (e.g., a ticket touching `apps/admin/**` finds ADRs mentioning the admin app).

Stop at the first layer that returns a non-empty result, unless you have specific reason to keep looking. Don't surface 20 ADRs — surface the 3-5 most relevant.

**Status filtering.**

- `accepted` — surface as a constraint. The agent should follow the decision.
- `proposed` — surface with explicit "PROPOSED — may not constrain" marker. The agent should not treat as binding.
- `superseded` — do not surface by default. If the supersession chain is relevant, surface the *current* ADR and note the prior decision in passing.
- `rejected` — surface only if the ticket appears to revisit the rejected approach (helps avoid re-litigating).
- `deprecated` — surface only if the ticket touches code still using the deprecated approach.

**Supersede chain handling.** If ADR-3 was superseded by ADR-7, and ADR-7 is superseded by ADR-12, surface only ADR-12. Do not show the chain unless the agent asks.

**Recency caveat.** ADRs accepted in the last 7 days carry a "recent — verify still applies" note. New decisions sometimes get reversed quickly; signal the uncertainty.

## How to call `adrs`

Two modes, in order of preference:

**MCP mode (preferred).** If the `adrs` MCP server is connected, use the typed tool calls: `adrs_list`, `adrs_search`, `adrs_get`. Filter results in the agent.

**Shell mode (fallback).** Use the CLI directly:

```bash
adrs --ng list --status accepted
adrs --ng list --tag auth
adrs search "session handling"
adrs --ng list --json   # structured output for parsing
```

Project-specific overrides go in `.adr-dir` (the directory `adrs` writes to) and are picked up automatically.

## Failure mode

**`adrs` not installed:** check for the binary in PATH. If missing:
- If `doc/adr/` directory exists, fall back to reading raw markdown files. Parse the YAML frontmatter manually for status/tags. Surface a degraded warning: "adrs CLI not installed; reading ADRs as markdown only."
- If `doc/adr/` doesn't exist, log "no ADR repository found" and continue. Do not halt — projects without ADRs are valid.

**`.adr-dir` says ADRs live somewhere unexpected:** trust `.adr-dir`. Do not second-guess.

**ADR file malformed (broken frontmatter, missing required fields):** skip the file, log the issue, continue. Do not let one bad ADR block the whole load.

**Too many matches (>15 candidates):** apply stricter filtering (require tag match AND path match). Do not surface a wall of marginally-relevant ADRs — that's worse than surfacing none.

## Interaction with other skills

- **`project-context-loader`** runs first and reads PROJECT.md. This skill reads PROJECT.md's ADR pointers as one of its layers.
- **`triage`** classifies the ticket; `adr-loader` runs after triage so it has the classification to bias the search (auth tickets bias toward auth-tagged ADRs).
- **`think`** uses the surfaced ADRs as constraints when drafting plan.md. The plan should explicitly reference any ADR it follows or contradicts.
- **`adr-author`** runs separately when a *new* decision is being made. `adr-loader` reads existing ADRs; `adr-author` writes new ones.
- **`safe-edit` rule** can use ADR content to refine OWNERSHIP.md classification (an ADR saying "auth code is owned by senior engineers" reinforces the forbidden tier).

## See also

- `adr-author` skill — drafts new ADRs when decisions are being made
- `.agent/PROJECT.md` "Pointers" and "Active concerns" sections
- `doc/adr/` — ADR repository (configurable via `.adr-dir`)
- `https://github.com/joshrotenberg/adrs` — the underlying tool
- MADR format: `https://adr.github.io/madr/`
