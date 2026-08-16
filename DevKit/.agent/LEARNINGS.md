# LEARNINGS.md

Gotchas, root causes, and non-obvious fixes. **Append-only.** Newest at the top.

<!--
Rules (enforced by the `learnings-loop` skill):

- One entry per ticket maximum. Pick the most surprising finding.
- "Nothing learned" is valid and preferred over padding.
- All five fields required per entry: Root cause, Fix, Gotcha for next time, Tags, one-liner.
- Tags come from the closed vocabulary below. New tags: append with [suggested tag: x] flag,
  add to vocabulary in a separate edit.
- Never edit past entries. Append corrections referencing the prior entry.
- Never delete. Archive by year (LEARNINGS-<YEAR>.md) when this file gets large.
-->

## Tag vocabulary

<Closed vocabulary. Extend deliberately, not per-entry.>

- `auth` — login, session, tokens, SSO, password flows
- `payments` — billing, checkout, refunds, idempotency
- `migrations` — DB schema changes, migration tooling
- `ci` — build pipeline, tests-in-CI, deploy pipeline
- `deploy` — rollouts, rollbacks, env-specific issues
- `flaky-tests` — non-deterministic test behavior
- `perf` — performance, latency, throughput
- `security` — CORS, CSP, rate limits, hardening
- `data` — data model, data integrity, backfills
- `integrations` — third-party APIs, webhooks
- `dev-env` — local development setup and tooling
- `ui` — frontend rendering, layout, accessibility
- `tls` — certificates, HTTPS, domain setup
- `dependencies` — package bumps, supply chain

---

<!--
Format for each entry:

## YYYY-MM-DD | #<ticket> | <one-liner>
- **Root cause:** <one sentence>
- **Fix:** <what was done>
- **Gotcha for next time:** <the actionable warning>
- **Tags:** <from vocabulary above, comma-separated>

Newest at top.
-->

<!-- entries go below this line; empty at project start -->
