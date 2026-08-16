# PROJECT.md

**Project:** <name>
**Client:** <client name or "internal">
**Status:** active | maintenance | sunsetting
**Primary contact:** <who to escalate to, with channel>
**Last reviewed:** <ISO date — update at every review>

<!--
Target length: 300-500 words. If you're past 800, something belongs
in STACK.md, INFRA.md, or RUNBOOK.md instead.

This file is human-edited via PR. Agents propose edits, humans approve.
Do not let the agent self-edit this file.
-->

## What this project does

<Two to four sentences. Written so someone who's never seen the project
understands what they're about to work on. No jargon the client wouldn't use.>

## Who uses it

<One to two sentences. End users, not the client's internal stakeholders.
Shapes what counts as "critical" vs "nice-to-have" at triage.>

## Shape of the codebase

<Three to six bullets. High-level structure, not a file tree dump.>

- `apps/<name>` — <what this app is>
- `packages/<name>` — <what this package is>
- `infrastructure/` — <what's here>

## Critical paths

<Paths where bugs directly hurt the client's business.
NOT "all important paths" — the handful where an outage is a phone call.>

- <business flow>: `<path glob>`
- <business flow>: `<path glob>`

## Non-obvious conventions

<Format: "We do X (not the usual Y) because Z.">
<The `because` makes the reason evaluable. Without it, conventions get re-litigated.>

- <convention 1>
- <convention 2>

## Client preferences

<Explicit preferences, especially ones that shaped past decisions.>

- <preference 1>
- <preference 2>

## Active work themes

<What's happening right now. Shapes triage priority.>

- <theme 1>
- <theme 2>

## Active architectural concerns

<Currently-relevant ADRs the agent should load before planning. Use this when a recent
or in-flight decision affects multiple tickets in the current sprint. Most projects
have 0-3 entries here at a time; older accepted ADRs are searchable but don't need
to be listed explicitly.>

- ADR-NNNN — <one-line summary of the constraint this imposes>
- ADR-NNNN — <one-line summary>

## Pointers

- `STACK.md` — languages, frameworks, versions
- `INFRA.md` — how this deploys
- `RUNBOOK.md` — how to run locally, debug
- `OWNERSHIP.md` — safe/review/forbidden paths
- `LEARNINGS.md` — gotchas log
- `doc/adr/` — Architectural Decision Records (managed via the `adrs` CLI; see the harness README)
- External: <client docs, Figma, Linear project, etc.>
