---
name: reproduce
description: "Use this skill on every bug-classified ticket after triage and before think and implementation. Invokes the `reproducer` subagent to confirm the reported bug in isolation, then writes the result into plan.md. Cannot-reproduce tickets are escalated for human investigation, not silently 'fixed' — a fix without reproduction is guesswork."
---
# reproduce

Confirm a reported bug is reproducible before attempting a fix. The skill orchestrates; the `reproducer` subagent does the work in an isolated context.

## When to load

Load on bug-classified tickets, after `triage` completes. Runs before `scope-estimate` and `think`.

## Job

1. Invoke the `reproducer` subagent with the bug description and ticket id.
2. Read the subagent's structured report.
3. Route based on the report's `Verdict`:
   - **reproduced** → record reproduction in `plan.md` (or in a separate Reproduction section if plan.md doesn't exist yet); proceed to `scope-estimate` / `think`.
   - **unreproduced** → comment on the GitHub issue with the report; load `escalation`.
   - **environmental** → comment on the GitHub issue; if RUNBOOK.md rot is the cause, propose a RUNBOOK update via `learnings-loop`; load `escalation` if the ticket is blocked.
   - **inconclusive** → surface the report to the human; let them decide whether to invest more time, escalate, or close.

## How to invoke the subagent

In the parent agent's prompt to itself, call the reproducer explicitly:

> Use the `reproducer` subagent to reproduce ticket `<ticket-id>`. Pass the bug description verbatim from the GitHub issue. The subagent will return a structured Reproduction report.

The subagent operates in an isolated context, reads RUNBOOK.md and STACK.md itself, and returns only its final report. Its intermediate tool calls do not consume parent context.

## What to do with the report

Copy the entire Reproduction report into:

- `plan.md` "Reproduction" section (if plan.md exists)
- Or `.agent/tickets/<ticket-id>/repro.md` as a standalone file (if plan.md not yet written; `think` will pull it in)

The report's `Minimal repro` block is the most valuable artifact — it feeds `test-first`'s test design and `think`'s approach.

## Rules

**Trust the subagent's verdict.** Don't second-guess unless the report contradicts itself. The subagent has fresh context and three reproduction attempts; the parent agent does not have that information.

**Don't re-run reproduction in the parent context.** That would defeat the context-isolation benefit. If you doubt the subagent's report, invoke it again with refined inputs — don't try to verify it yourself.

**Surface inferences explicitly.** If the subagent's report includes "Inferences made from the report" entries, those go into the GitHub issue comment too. The reporter should see what assumptions the agent made.

**"Partially reproduced" maps to "inconclusive."** If the subagent reports 1-of-3 or 2-of-3 reproduction consistency, treat it as inconclusive in the absence of further signal — flakiness changes the planning approach substantially.

## Failure modes

**Subagent halts on destructive setup requirement** (database wipes, secrets needed, paid API calls) → the report's `Verdict` will be `inconclusive` with the destructive requirement noted. Do not authorize destructive reproduction on the subagent's behalf. Escalate to the human.

**Subagent reports environmental failure with no RUNBOOK.md** → the project is missing setup documentation. Propose a RUNBOOK.md draft via `learnings-loop`; halt the ticket until it's addressed.

**Subagent's report is malformed or missing the structured format** → invoke the subagent again with explicit instructions to follow the report format from its system prompt. If two attempts produce malformed output, treat as inconclusive and surface to human.

## See also

- `.claude/agents/reproducer.md` in the project template — the subagent definition
- `.agent/RUNBOOK.md` in the target repo
- `escalation` skill (invoked on could-not-reproduce or destructive-setup verdicts)
- `scope-estimate`, `think` skills (next in the flow)
- `test-first` skill — uses the minimal repro as the basis for the failing test
