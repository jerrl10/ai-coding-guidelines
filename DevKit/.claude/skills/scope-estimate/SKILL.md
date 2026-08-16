---
name: scope-estimate
description: "Use this skill whenever a ticket has been classified by triage but not yet planned by think — typically right after triage on features, or after reproduce on bugs. Estimates change size as small / medium / large. Large-scope tickets halt the normal implementation path and produce a design doc instead. Err toward larger when uncertain — underscoping is the more expensive error because it puts large work through gates that assume small work."
---
# scope-estimate

Estimate the size of a change before planning implementation. Catches "this is too big for one ticket" early.

## When to load

Load after `triage` and (for bugs) `reproduce`. Runs before `think`.

## Job

Estimate:
1. Approximate files that need to change.
2. Risk level (per the `risk-rubric` rule in `CLAUDE.md`).
3. Time bucket: small (<30 min agent-time) / medium (30 min–2h) / large (>2h or architectural).
4. Decide whether to proceed to implementation or produce a design doc instead.

## Output

- Scope class (`small` / `medium` / `large`) written into the ticket's planned `plan.md` header.
- GitHub label: `scope/small`, `scope/medium`, or `scope/large`.
- For `large`: halt implementation path. Produce a design doc instead, escalate for human review.

## Rules

**Large scope → design doc, not implementation.** If the estimate is large, the correct output is a design doc, not a plan. The design doc describes the intended approach and is reviewed before any implementation work. This prevents agents from diving into architectural changes without alignment.

**Size is estimated, not promised.** The actual ticket may grow. The scope class sets expectations and triggers the design-doc path for large work; it doesn't bind the implementation.

**Err toward larger.** If unsure between small and medium, call it medium. If unsure between medium and large, call it large. Underscoping is the more expensive error.

**Use LEARNINGS.md for calibration.** Past tickets in similar areas are the best prior for size estimates. If a similar past ticket took 2 hours, the new one probably won't be 15 minutes.

## Size triggers

| Trigger | Minimum scope |
|---|---|
| Touches a `review`-tier path | medium |
| Includes a new migration | medium |
| Requires a new dependency | medium |
| API shape change | medium |
| Touches a `forbidden` path (should have been blocked, but still) | large |
| Touches > 5 top-level directories | large |
| Requires changes across multiple apps in a monorepo | large |
| Requires infra or deploy-config change | large |

## Failure mode

**Cannot estimate with `cs >= 5`:** label as `large` by default and produce a design doc. Low-confidence estimates at medium are the most expensive — they look small and end up sprawling.

## See also

- `risk-rubric` rule (in `CLAUDE.md`) — risk rubric used here for consistency
- `.agent/LEARNINGS.md` — calibration data
- `think` skill — next in the flow
