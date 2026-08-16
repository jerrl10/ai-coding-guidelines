---
name: handoff
description: "Use this skill when the agent is running out of context, hits a blocker, is explicitly stopped, or is transferring a ticket between agents or to a human. Produces a structured handoff document so the next actor can take exactly one concrete action within 60 seconds. The 'Next step' must be a single imperative sentence pointing at a real file:line or command — vague handoffs are the dominant failure mode and the skill refuses to write one without a real next step."
---
# handoff

Produce a structured handoff document when control is passing to another actor. The receiver should be able to take exactly one concrete action within 60 seconds of reading.

## When to load

Load when any of these triggers fires:

- **context-exhaustion** — context window usage > 70% on a ticket that isn't close to done.
- **blocker** — the agent cannot proceed (missing info, ambiguous spec, external dependency).
- **explicit-stop** — the developer or operator stops the agent mid-ticket.
- **role-change** — the ticket is transferring between agents or between agent and human (L1 triage → L2 implementation, implementation → reviewer, agent → human).

## Job

Produce or append to `.agent/tickets/<ticket-id>/handoff.md`. Each invocation produces one new entry at the top of the file (newest first). Old entries remain in place — the file is a session log.

## Output

File: `.agent/tickets/<ticket-id>/handoff.md`. Format defined by `handoff-template.md` in this skill dir.

## Rules

**Append new handoffs at the top with an ISO timestamp.** Do not edit prior handoffs. If information from a prior handoff turned out wrong, note the correction in the new entry; don't rewrite history.

**The "Next step" is the contract.** It must be:
- A single imperative sentence.
- Referencing either a real file:line (e.g., `apps/api/src/routes/auth.ts:89`) or a real command (e.g., `pnpm db:migrate`).
- Concrete enough that the receiver can execute without further investigation.

Vague Next steps are not acceptable. "Continue the implementation" and "Fix the failing test" fail this rule. If you cannot produce a valid Next step, do not write a handoff — the situation needs `escalation` instead.

**State uses three buckets:** Done, In-progress, Untouched. This split is not optional. "In progress" is where bugs hide (half-applied edits, dirty branches, half-written tests).

**Decisions made captures what NOT to re-litigate.** Each entry: "Chose X over Y because Z. Revisit if `<trigger>`." Only include decisions future actors would otherwise re-open. Trivial decisions (filename, variable name) don't belong here.

**Context pointers use `path:line`, not just `path`.** A path alone sends the receiver on a hunt. `apps/web/src/auth/session.test.ts:47` sends them to the exact spot.

**Confidence is on the Next step.** A `cs < 5` means "I'm not sure this is the right next step" and the receiver should verify before executing. Being honest here is more valuable than projecting false confidence.

**Handoff #4 rule.** If this is the 4th or later handoff on the same ticket, re-read `plan.md` before writing the handoff and explicitly state whether the original plan is still correct. Often the right move at handoff #4 is not another handoff but an escalation — recognize the thrashing.

## Failure mode

**Cannot articulate a concrete Next step.** Do not write a handoff. Load `escalation` with the admission that the state isn't clear enough to hand off.

**Cannot summarize State in the three buckets.** The agent doesn't understand its own work. Escalate with that admission. Do not produce a half-baked handoff that hides this.

## Visibility

Handoffs are internal to the repo. **Do not link handoffs from PR descriptions.** The PR body has its own format (produced by `pr-hygiene`). Handoffs serve agents and developers; PRs serve reviewers. Different audience, different document.

## See also

- `handoff-template.md` in this skill dir
- `escalation` skill (stricter cousin of handoff)
- `plan.md` — handoffs reference the plan, don't duplicate it
- `learnings-loop` skill — reads the final handoff at ticket close
