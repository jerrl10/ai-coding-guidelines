# metrics-schema.md

Full field list for `.agent/metrics/tickets.jsonl` records.

Each line is a single JSON object. Append-only. One line per ticket close.

## Required fields

| Field            | Type            | Notes                                                   |
| ---------------- | --------------- | ------------------------------------------------------- |
| `ticket_id`      | string          | e.g. "#412"                                             |
| `opened_at`      | ISO 8601 string | GitHub issue creation time                              |
| `closed_at`      | ISO 8601 string | ticket close event time                                 |
| `outcome`        | enum            | `merged` / `closed-without-merge` / `rejected`          |
| `classification` | enum            | `bug` / `feature` / `question` / `spam` (from `triage`) |
| `stack`          | string[]        | e.g. `["typescript","nextjs"]` (from STACK.md)          |

## Estimation fields (for later accuracy analysis)

| Field                 | Type         | Notes                                                |
| --------------------- | ------------ | ---------------------------------------------------- |
| `scope_estimate`      | enum         | `small` / `medium` / `large` (from `scope-estimate`) |
| `risk_label_agent`    | enum         | `low` / `medium` / `high` (at plan time)             |
| `risk_label_reviewer` | enum \| null | label on PR at merge (may differ)                    |
| `confidence_at_plan`  | int 0–10     | cs from plan.md                                      |
| `confidence_at_pr`    | int 0–10     | cs from PR body's Agent trail                        |

## Change-size fields

| Field                    | Type | Notes                                       |
| ------------------------ | ---- | ------------------------------------------- |
| `files_planned`          | int  | count from plan.md Files list (final state) |
| `files_actually_changed` | int  | from git diff                               |
| `lines_added`            | int  | from git diff --numstat summed              |
| `lines_removed`          | int  | same                                        |

## Process-timing fields

| Field                    | Type        | Notes                                   |
| ------------------------ | ----------- | --------------------------------------- |
| `gate_1_latency_seconds` | int \| null | null if auto-passed on 🟢               |
| `gate_2_latency_seconds` | int         | PR open → merge                         |
| `gate_2_rounds`          | int         | count of `changes_requested` events     |
| `handoff_count`          | int         | number of entries in handoff.md         |
| `handoff_triggers`       | string[]    | e.g. `["context-exhaustion","blocker"]` |
| `escalations`            | int         | count of escalation skill invocations   |

## Quality fields

| Field                        | Type        | Notes                                  |
| ---------------------------- | ----------- | -------------------------------------- |
| `tests_added`                | int         | count of new test files in diff        |
| `tests_modified`             | int         | count of modified test files           |
| `visual_diff_ran`            | bool        | whether visual-diff skill fired        |
| `visual_diff_flagged_routes` | int \| null | count of `potential-regression` routes |

## Safety fields

| Field                       | Type | Notes                                       |
| --------------------------- | ---- | ------------------------------------------- |
| `forbidden_path_attempts`   | int  | count of safe-edit halts on forbidden paths |
| `review_tier_paths_touched` | int  | count of review-tier paths in diff          |

## AI usage fields

| Field                  | Type           | Notes                                                                                           |
| ---------------------- | -------------- | ----------------------------------------------------------------------------------------------- |
| `model`                | string \| null | Primary model ID (e.g. `"claude-opus-4-7"`). Read from plan.md / handoff.md "Agent:" line.     |
| `tokens_input`         | int \| null    | Total input tokens across all agent turns. Null unless session stats are available.             |
| `tokens_output`        | int \| null    | Total output tokens generated. Null unless session stats are available.                         |
| `tokens_cache_read`    | int \| null    | Prompt-cache read tokens (Anthropic cache hits). Null unless session stats are available.       |
| `tokens_cache_write`   | int \| null    | Prompt-cache write tokens (tokens written to cache). Null unless session stats are available.   |
| `cost_usd`             | float \| null  | Estimated cost derived from model × token counts. Null if either is unavailable.               |
| `tool_calls`           | int \| null    | Total tool call events. Proxy for task complexity. Null unless session transcript is available. |
| `context_compactions`  | int \| null    | Number of context-window compression events. Null unless Claude Code exposes session log.       |

## Tagging fields

| Field  | Type     | Notes                                                           |
| ------ | -------- | --------------------------------------------------------------- |
| `tags` | string[] | from the LEARNINGS.md entry if one was written; empty otherwise |

## Meta fields

| Field              | Type        | Notes                                                      |
| ------------------ | ----------- | ---------------------------------------------------------- |
| `_schema_version`  | int         | bump when schema changes in breaking ways                  |
| `_recorder_errors` | string[]    | fields the recorder couldn't derive; empty if clean        |
| `correction_of`    | int \| null | line number of a prior record this corrects; null normally |

## Derivation notes for AI fields

- `model`: grep plan.md and handoff.md for the "**Agent:**" line. If multiple models appear across handoffs, record the one that did the majority of the implementation work.
- Token fields (`tokens_input`, `tokens_output`, `tokens_cache_read`, `tokens_cache_write`): Claude Code does not expose per-session token counts to skills at runtime. Record null unless the project wires an API-usage logging layer (e.g., a PostHog event or Anthropic Usage API poll) and the data lands somewhere readable.
- `cost_usd`: compute from token counts × the per-token price for the recorded model (Anthropic pricing page). Null if either model or any token count is null.
- `tool_calls`: count `<tool_use>` blocks in the session transcript if available; otherwise null. Useful complexity proxy — high tool-call counts relative to lines changed often signal thrash.
- `context_compactions`: Claude Code emits a summary injection when the context window is compressed. Count these events from the session transcript if available; otherwise null. `handoff_count` is a coarse lower bound.

**Anonymization:** `model` is categorical and safe to include in the central endpoint payload. Token counts and cost are numerical and safe. `tool_calls` and `context_compactions` are numerical and safe.

## What's deliberately NOT in the schema

- Free-text descriptions of the ticket.
- Author names (who opened, who reviewed). Use Git/GitHub APIs if needed separately; this file is for numerical aggregation.
- "Agent happiness" or other soft signals. Use confidence scores instead.

## Versioning

The `_schema_version` field exists so aggregation scripts can skip or transform records produced under older schemas. Bump when:

- A field is renamed or removed.
- A field's type changes.
- An enum gets new values that break existing aggregations.

Don't bump for additive changes (new optional fields).
