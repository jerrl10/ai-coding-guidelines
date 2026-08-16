---
name: metrics-recorder
description: "Use this skill at every ticket close (PR merged, issue closed without merge, or ticket otherwise resolved) to capture per-ticket metrics as a JSON record. Runs after learnings-loop. Appends to .agent/metrics/tickets.jsonl locally; optionally POSTs an anonymized copy to a central endpoint for cross-project estimation priors. Records: timing, estimation accuracy, risk drift, handoff count, test coverage, safety signals."
---
# metrics-recorder

Capture per-ticket metrics at ticket close. Feeds project-health dashboards and cross-project estimation priors.

## When to load

Load at ticket close, after `learnings-loop` runs. Last skill in the ticket lifecycle.

## Job

1. Read `plan.md`, `handoff.md`, the PR description and timeline, git diff stats.
2. Assemble a per-ticket metrics record (see schema below).
3. Append the record as one JSON line to `.agent/metrics/tickets.jsonl`.
4. Produce an anonymized copy and POST it to the central metrics endpoint (if configured in `.agent/metrics/config.json`; skip silently if not).

## Output

- `.agent/metrics/tickets.jsonl` — append one line per ticket. Never edit past lines.
- Network: one POST to central endpoint with anonymized record, if configured.
- No console output unless an error occurs.

## Record schema

See `metrics-schema.md` in this skill dir for the full field list with types and derivation rules. Core fields:

- `ticket_id`, `opened_at`, `closed_at`, `outcome`
- `classification`, `scope_estimate`, `risk_label_agent`, `risk_label_reviewer`
- `files_planned`, `files_actually_changed`, `lines_added`, `lines_removed`
- `gate_1_latency_seconds`, `gate_2_latency_seconds`, `gate_2_rounds`
- `handoff_count`, `handoff_triggers[]`, `escalations`
- `tests_added`, `tests_modified`, `visual_diff_ran`, `visual_diff_flagged_routes`
- `forbidden_path_attempts`, `review_tier_paths_touched`
- `confidence_at_plan`, `confidence_at_pr`
- `model`, `tokens_input`, `tokens_output`, `tokens_cache_read`, `tokens_cache_write`
- `cost_usd`, `tool_calls`, `context_compactions`
- `tags[]`, `stack[]`

## Rules

**Append-only.** Never edit past records. If a record was wrong, append a correction with the same `ticket_id` and a `correction_of` field pointing at the original line number. Aggregators must handle corrections.

**Anonymization for central endpoint is strict.** Drop:
- `ticket_id` (replace with a hash)
- `tags` (could leak project specifics)
- Any free-text
- Any file paths
- Project name (replace with salted hash)

Keep:
- All numerical fields (token counts, cost, tool_calls, context_compactions, lines, timing)
- All categorical fields (classification, scope, risk, outcome, handoff_triggers, stack, confidence scores, model)
- Timestamps (but not ticket IDs)

Never send LEARNINGS.md content to the central endpoint.

**Missing fields are honestly null, not fabricated.** If a field cannot be derived (e.g., gate_1_latency couldn't be measured because Gate #1 was skipped), record `null`. Do not synthesize plausible values.

**Confidence scores come from the actual cs values in plan.md and PR body.** Not re-estimated at close time.

## Derivation notes

- `gate_1_latency_seconds`: time from `plan.md` commit to explicit human ack (reaction, comment, or approval). Null if Gate #1 was auto-passed on 🟢 risk.
- `gate_2_latency_seconds`: time from `gh pr create` to `merged` event.
- `gate_2_rounds`: number of `changes_requested` review events before merge.
- `files_planned`: count of entries in plan.md's Files expected to change list at final plan state.
- `files_actually_changed`: `git diff --name-only base...HEAD | wc -l`.
- `visual_diff_flagged_routes`: count of routes marked `potential-regression` in visual-diff report.md, if the skill ran.
- `risk_label_reviewer`: the label on the PR at merge time (reviewers may adjust).

## Failure mode

- **Cannot read plan.md or PR data:** record what is available, leave missing fields null, note in a `_recorder_errors` field. Do not halt.
- **Central endpoint unreachable:** write local record as normal, queue the anonymized record in `.agent/metrics/pending.jsonl` for retry. Do not fail the ticket close.
- **tickets.jsonl is not writeable (permissions, disk):** halt and escalate. This is a config error, not a soft failure.

## Interaction with other skills

- `learnings-loop` runs before this skill. This skill reads the LEARNINGS.md entry (if any) to populate the `tags` field.
- `pr-hygiene` writes the risk label and confidence score that this skill reads.
- `handoff` entries are counted here to derive `handoff_count` and `handoff_triggers`.

## Dashboards and reporting

This skill only produces the source data. A separate tool/script reads `tickets.jsonl` and produces the project-summary.md dashboard. Kept separate so the dashboard can be regenerated on demand without re-running per-ticket recording.

Default dashboard script: `ci/build-dashboard.py` (not yet shipped; see Known gaps).

## See also

- `metrics-schema.md` — full field list
- `.agent/metrics/config.json` — central endpoint URL and auth
- `learnings-loop`, `pr-hygiene`, `handoff` skills
