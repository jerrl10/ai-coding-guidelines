---
name: search-first
description: "Forces a web search before answering questions about current state, recent changes, or anything that may have evolved. Use whenever the question involves words like \"new\", \"latest\", \"recent\", \"updated\", \"current\", \"now\", \"yet\", \"still\", \"anymore\", or specific version numbers. Also use when the user names a specific library, framework, or tool and asks about its capabilities — even without explicit recency cues, the answer may have changed since training. Triggers include: library and framework current state, comparing options before an ADR, verifying that a known issue still applies, current pricing or availability, error messages mentioning specific versions, and recent deprecations. When in doubt, search. Stale training data is worse than a quick search."
---

# search-first

Search the web for current information before answering, instead of relying on training data that may be stale.

## When to load

Load whenever the agent's answer would depend on facts that change over time: library versions, framework features, pricing, deprecations, current best practices, or anything where "the answer six months ago" might differ from "the answer now."

In ticket work, this most often fires during:

- **`triage` / `think`** — checking whether a proposed approach uses a current pattern or a deprecated one.
- **Implementation** — looking up library APIs, error messages, or migration guides.
- **Dependency choices in `adr-author`** — comparing libraries before drafting an ADR's Alternatives section honestly.
- **Investigation of confusing errors** — when LEARNINGS.md doesn't have prior art and the error mentions a specific version or recent change.

This is the only skill in the harness that loads almost anywhere in the lifecycle. It's a posture, not a phase.

## Job

Run at least one targeted web search before formulating an answer to a version-sensitive or current-state question. Ground the response in the search results, cite them, and flag when results are thin instead of falling back silently.

## Rules

1. **Search before answering for in-scope questions.** Do not answer from training data alone. At least one `web_search` query before the response.
2. **Specific, targeted queries.** Break vague questions into concrete search terms. For comparisons, search for each product / version separately if needed.
3. **Cite what you find.** Ground the answer in search results. If sources conflict, say so explicitly.
4. **Flag thin results.** If search doesn't yield good info, say so rather than falling back to training data without warning.
5. **Don't hedge unnecessarily.** If the search results are clear, give a clear answer.

## Output

The agent's response, with citations to specific URLs from search results. For factual claims that came from the search, link the source.

In `plan.md` or ADR contexts, search results inform the document but don't need to be reproduced verbatim — a one-line note like "approach validated against [Payload v3 migration docs](url) as of <date>" is enough.

## Failure modes

- **Search returns nothing useful.** Say so: "Searched for X; results were thin. My best inference from training data is Y, with confidence cs5 — verify before relying on this." Don't pretend training-data inference is search-grounded.
- **Search results conflict.** Surface the conflict: "Source A says X, source B says Y, dated such-and-such." Let the human pick. Don't silently average.
- **Network unavailable.** Halt the in-scope question and escalate. Don't bluff through.

## Trigger examples (NOT to fire)

- Questions about the project's own codebase. Use `LEARNINGS.md`, `PROJECT.md`, or grep instead.
- Questions where the answer is in the ticket itself.
- Stable computer-science fundamentals (sorting algorithms, B-tree mechanics, HTTP status codes).
- Anything where the user has explicitly given the answer.

When the question is mixed (project context + library version), do both: search for the library piece, grep for the project piece.

## Related

- `triage` skill — runs at session start; may trigger search-first when a ticket mentions specific library versions.
- `think` skill — produces plan.md; search-first results inform the Approach section.
- `adr-author` skill — Alternatives section often requires search to compare options honestly.
- `LEARNINGS.md` — check this before searching the web; the gotcha may already be recorded.
