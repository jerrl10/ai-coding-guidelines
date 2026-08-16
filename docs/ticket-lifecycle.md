# Ticket lifecycle

How the skills in `DevKit/.claude/skills/` compose from a new issue to a merged PR.
Each phase names the skill that owns it, what artifact it produces, and what
makes it stop.

```text
                    ┌─────────────┐
   new issue ──────►│   triage    │  classify: bug / feature / question / spam
                    └──────┬──────┘
              bug ─────────┴───────── feature
               │                        │
        ┌──────▼──────┐                 │
        │  reproduce  │ (subagent)      │
        └──────┬──────┘                 │
               └──────────┬─────────────┘
                   ┌──────▼────────┐
                   │ scope-estimate│  small / medium / large
                   └──────┬────────┘
                   ┌──────▼──────┐
                   │    think    │──► .agent/tickets/<id>/plan.md
                   └──────┬──────┘
                    ═══ GATE 1 ═══  human clears the plan
                   ┌──────▼──────┐
                   │ test-first  │──► failing test
                   └──────┬──────┘
                   ┌──────▼──────┐
                   │ write code  │  bounded by the `safe-edit` rule
                   └──────┬──────┘
                   ┌──────▼──────┐
                   │ visual-diff │  frontend paths only
                   └──────┬──────┘
                    ═══ GATE 2 ═══  pr-hygiene enforces
                   ┌──────▼──────┐
                   │ pr-hygiene  │──► PR body, risk rating
                   └──────┬──────┘
                    ═══ MERGE ═══
                   ┌──────▼────────┐
                   │ learnings-loop│──► LEARNINGS.md entry (often: none)
                   └──────┬────────┘
                   ┌──────▼──────────┐
                   │ metrics-recorder│──► .agent/metrics/tickets.jsonl
                   └─────────────────┘
```

## Phases

| # | Skill | Produces | Stops when |
| --- | --- | --- | --- |
| 1 | `triage` | classification + next-phase decision | low confidence → `needs-triage-human` label, halt |
| 2 | `reproduce` | reproduction report (via the `reproducer` subagent) | cannot reproduce → `escalation` |
| 3 | `scope-estimate` | small / medium / large | large → design doc instead of implementation |
| 4 | `think` | `.agent/tickets/<id>/plan.md` | forbidden path in the Files list → `escalation` |
| 5 | `test-first` | a test that fails for the right reason | test passes before the fix → the test is wrong |
| 6 | — | the change itself | forbidden path → `escalation` |
| 7 | `visual-diff` | before/after screenshots, pixel diff | unexplained pixel diff → hard block |
| 8 | `pr-hygiene` | PR body + risk rating | any precondition fails → refuses to open the PR |
| 9 | `learnings-loop` | a LEARNINGS.md entry, or nothing | architectural decision → routes to `adr-author` |
| 10 | `metrics-recorder` | one JSONL record | never blocks a close |

There is deliberately no `implement` skill. Phase 6 is ordinary coding, fenced
by `test-first` before it and `pr-hygiene` after it. Adding a skill there would
be ceremony without a gate.

## The two gates

**Gate 1 — plan approved.** No source writes happen before `plan.md` exists and
a human has cleared it. This is the cheapest place to catch a wrong approach.

**Gate 2 — mergeable.** `pr-hygiene` checks: plan.md exists, tests exist for
non-doc changes, no forbidden-path edits in the diff, `visual-diff` present if
frontend paths were touched. It blocks rather than opening a PR that will bounce.

The `completion-check.py` Stop hook is the automated backstop for both gates.
It is off until `.agent/completion-check.json` sets `"enabled": true`.

## Cross-cutting skills

These load on trigger, not on phase:

| Skill | Triggers on |
| --- | --- |
| `search-first` | any recency-, version-, or pricing-sensitive claim |
| `adr-loader` | start of every ticket — surfaces accepted ADRs as constraints |
| `adr-author` | the plan introduces a new architectural decision (status `proposed`; humans accept) |
| `coding-standards` | writing or reviewing code in the repo |
| `handoff` | context running out, blocked, or transferring the ticket |
| `escalation` | a human decision is required — stricter than `handoff` |

## Stack and infra skills

Loaded conditionally from the `.agent/` context files:

- From `STACK.md`: `typescript-nextjs`, `typescript-node`, `csharp-backend`
- From `INFRA.md`: `gcp-cloudrun`, `onprem-docker`, `generic-ci`

`typescript-node`, `onprem-docker`, and `generic-ci` ship as **stubs**. Fill them
in per project before relying on them — their frontmatter says so, and the skill
body is a checklist of what to write.

`csharp-backend` is the opposite: a fully specified house style for vertically
sliced .NET backends, with CI-enforceable rules. If the project it lands in works
differently, edit its `backend-architecture.md` to match rather than leaving two
sets of rules in play.

## Authoring skills

Outside the ticket flow, used when shaping work rather than doing it:
`to-prd`, `prd-to-plan`, `grill-me`, `write-a-skill`.

## Where things live

`DevKit/` mirrors this exactly, which is why installing it is a plain copy.

```text
<project>/
├── CLAUDE.md                       # the safe-edit rule + standing rules
├── .claude/
│   ├── settings.json               # permissions + Stop hook
│   ├── hooks/completion-check.py
│   ├── skills/<name>/SKILL.md
│   ├── commands/<name>.md
│   └── agents/reproducer.md
└── .agent/
    ├── PROJECT.md  STACK.md  INFRA.md  RUNBOOK.md
    ├── OWNERSHIP.md            # path tiers the safe-edit rule reads
    ├── LEARNINGS.md
    ├── completion-check.json   # opt-in Stop hook config
    ├── tickets/<id>/plan.md
    └── metrics/tickets.jsonl
```
