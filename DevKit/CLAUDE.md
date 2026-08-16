# CLAUDE.md

<!-- DevKit template. Fill in "Project specifics"; leave the rest. This is the
     only place the `safe-edit` rule lives — skills reference it by name, so
     dropping this file dangles them. -->

## Context files

Human-owned, in `.agent/`. Say so if one is missing; don't guess its contents.

- `PROJECT.md`, `STACK.md` — every ticket. STACK decides which stack skill loads.
- `OWNERSHIP.md` — **before every write.** Path tiers for `safe-edit` below.
- `INFRA.md` — deploys, logs, incidents. Decides which infra skill loads.
- `RUNBOOK.md` — running or testing locally.
- `LEARNINGS.md` — triage (prior art) and ticket close.

## The `safe-edit` rule

**Classify every path before writing to it.** Applies to `Edit`, `Write`,
`NotebookEdit`, and any Bash that mutates files (`mv`, `sed -i`, `>`, codegen,
formatters). A tool made the edit, but you invoked the tool.

Match the path in `.agent/OWNERSHIP.md` against `forbidden`, then `safe`.
Forbidden wins over safe. Unmatched is **review** — no fourth tier, no
"probably fine".

| Tier | Action |
| --- | --- |
| **safe** | Write it. |
| **review** | Write it, but the path appears in the plan's Files list and the PR body. A reviewer has to see it. |
| **forbidden** | **Do not write.** Halt, load `escalation`, produce a draft patch for a human. Never apply it yourself. |

- Urgency, small diffs, and "just do it" never unlock a forbidden path. The
  override is a human editing `OWNERSHIP.md` or applying the patch.
- A forbidden path already dirty in the working tree is an incident, not a
  cleanup task. Surface it.
- Classify before the write. A rolled-back edit still ran.
- `OWNERSHIP.md`, `.claude/skills/**`, and this file are forbidden by default —
  you don't edit your own rules.
- `escalation` refuses a report without: what you tried, which path blocked it
  at which tier, what a human must decide. "Blocked on auth code" isn't a trace.

## Lifecycle

```text
triage → reproduce (bugs) → scope-estimate → think ─┤1├→ test-first
       → write code → visual-diff (frontend) ─┤2├→ pr-hygiene
       → learnings-loop → metrics-recorder
```

- **Gate 1** — `.agent/tickets/<id>/plan.md` exists, human cleared it. No source
  writes before this.
- **Gate 2** — tests pass, `visual-diff` clean if frontend touched, no
  forbidden-path edits. `pr-hygiene` blocks rather than opening a doomed PR.

No `implement` skill by design — implementation is ordinary work, fenced by
`test-first` before and `pr-hygiene` after.

## Standing rules

- **Plan before code.** `think` first on anything past a one-line doc fix.
  `plan.md` is the artifact, not a chat message.
- **Test before fix.** A test that passes before the fix is wrong, not lucky.
- **Reproduce before fixing bugs.** No repro, no fix.
- **Search before asserting.** `search-first` on anything version-, pricing-, or
  recency-sensitive.
- **Say when you stop.** Low context or blocked → `handoff`. Need a human
  decision → `escalation`.

---

## Project specifics

<!-- Project-owned. Delete the placeholders. -->

### Build & test

```bash
# <install> / <test> / <lint> / <typecheck>
```

### Conventions that differ from the defaults

<!-- Only what the model gets wrong by default. Not a style tutorial. -->

- <e.g. "Server Components by default; `use client` needs a comment saying why.">

### Things that have bitten us

<!-- Short. Detail belongs in .agent/LEARNINGS.md. -->

- <e.g. "Staging DB is not a copy of prod. Don't infer schema from it.">
