# Central metrics service — design sketch

**Status:** not built. This is the architecture, not code.

## Why a central service

Per-project metrics live in each repo. Cross-project insights require aggregation across repos. A central endpoint receives anonymized records from every project's `metrics-recorder` skill and exposes the aggregate.

## What it stores

Only anonymized records. Never ticket content, never file paths, never tags, never LEARNINGS.md entries. See `metrics-recorder/SKILL.md` "Anonymization" section for the exact fields kept.

## Minimum viable shape

```
┌─────────────────────┐       anonymized POST        ┌────────────────────┐
│ Project repo        │  ───────────────────────▶   │ central service    │
│ metrics-recorder    │                              │  - auth (per-proj  │
│ writes locally +    │                              │    token)          │
│ POSTs anonymized    │                              │  - writes to DB    │
└─────────────────────┘                              │  - exposes readers │
                                                     └─────────┬──────────┘
                                                               │
                                                               ▼
                                                     ┌────────────────────┐
                                                     │ queries            │
                                                     │  - estimation      │
                                                     │    priors          │
                                                     │  - cross-project   │
                                                     │    drift           │
                                                     │  - stack health    │
                                                     └────────────────────┘
```

- **Auth:** each project has a long-lived token. Token scopes: write-own, read-aggregate. A compromised token leaks that project's metrics only (already anonymized), not others'.
- **Storage:** Postgres. One table, one row per ticket close. Schema mirrors `metrics-schema.md`.
- **Deploy:** Cloud Run (or equivalent) + managed Postgres. Low traffic; smallest instance sizes are fine. Probably costs < $30/month.

## MVP alternative (no service)

If building a service is premature: each project commits anonymized records to a *second* internal GitHub repo via PR. That repo has a CI job that merges PRs after format validation. Aggregation scripts read the JSONL file directly from that repo.

This gets you the aggregate data without running infrastructure. Graduate to a service once the volume makes PR-per-ticket annoying (~50 tickets/week across all projects is roughly where the switch makes sense).

## Queries this enables

**Estimation priors:**
```
SELECT
  classification, scope_estimate, stack,
  percentile_cont(0.5) WITHIN GROUP (ORDER BY closed_at - opened_at) AS median_time,
  percentile_cont(0.9) WITHIN GROUP (ORDER BY closed_at - opened_at) AS p90_time,
  count(*) AS sample_size
FROM ticket_metrics
WHERE closed_at > now() - interval '90 days'
  AND outcome = 'merged'
GROUP BY 1, 2, 3
HAVING count(*) >= 5;
```

Read as: "for each (classification, scope, stack) triple with at least 5 recent tickets, what's the time-to-close distribution?"

**Drift detection per project:**
```
SELECT project_hash,
       avg(risk_label_reviewer != risk_label_agent) AS drift_rate
FROM ticket_metrics
WHERE closed_at > now() - interval '30 days'
GROUP BY project_hash;
```

**Stack health comparison:**
```
SELECT stack,
       avg(gate_2_rounds) AS avg_review_rounds,
       avg(bug_reopen_within_14d::int) AS reopen_rate
FROM ticket_metrics
WHERE closed_at > now() - interval '90 days'
GROUP BY stack;
```

Note: `bug_reopen_within_14d` is a derived column; needs a view or post-hoc join against later ticket records.

## What not to build

- **Fancy dashboards day one.** SQL + a spreadsheet for the first few months. Invest in UI only after you know which queries you run weekly.
- **Real-time streaming.** Tickets close at a rate of tens per day company-wide. Nightly batch is fine.
- **ML on the metrics.** Not enough data. Not the right tool. Use percentiles and direct inspection.

## Risks

- **Anonymization is hard to keep correct.** One careless field added to the recorder schema leaks client data. Mitigation: explicit allowlist of fields for central POST, not a denylist. Reject unknown fields.
- **Per-project tokens get committed by accident.** Mitigation: tokens live in the deploy env (like any other secret per INFRA.md), never in the repo. `metrics-recorder` skip silently if no token is configured.
- **Data interpretation goes wrong.** Median time-to-close looking bad might mean "harness got worse" or "we took on harder tickets." Always compare like-to-like (same classification, scope, stack). Don't slice on one dimension and panic.
