# ai-coding-guidelines

A portable Claude Code kit (**DevKit**): a gated ticket lifecycle, safe-by-default permissions, and reusable context files.

## What's in `DevKit/`

| Path | Purpose |
| --- | --- |
| `CLAUDE.md` | Project memory. Home of the **`safe-edit` rule** — the path-tier check every skill consults before a write. |
| `.claude/settings.json` | Permission allow/ask/deny lists and the Stop hook. Commit it. |
| `.claude/skills/` | The 25-skill library driving the lifecycle. |
| `.claude/commands/` | `merge-main`, `simplify`. |
| `.claude/agents/` | Subagent definitions (`reproducer`). |
| `.claude/hooks/` | `completion-check.py` — Stop hook backstopping both gates. Off until you opt in. |
| `.agent/` | Context templates you fill in: `PROJECT.md`, `STACK.md`, `INFRA.md`, `RUNBOOK.md`, `OWNERSHIP.md`, `LEARNINGS.md`. |

Reference docs sit outside the kit so a whole-directory copy can't drag them into your project.

## Lifecycle

```text
triage → reproduce (bugs) → scope-estimate → think ─┤1├→ test-first
       → write code → visual-diff (frontend) ─┤2├→ pr-hygiene
       → learnings-loop → metrics-recorder
```

**Gate 1** — `plan.md` exists and a human cleared it; no source writes before this.
**Gate 2** — tests pass, `visual-diff` clean if frontend touched, no forbidden-path edits.

No `implement` skill by design: implementation is ordinary coding, fenced by `test-first` before and `pr-hygiene` after. Phase-by-phase detail, plus the cross-cutting and stack skills: [`docs/ticket-lifecycle.md`](docs/ticket-lifecycle.md).

## Stop hook

`completion-check.py` checks the branch diff for forbidden-path edits, a missing `plan.md`, and optionally source changes with no test — blocking the turn and telling Claude what to fix. Stdlib only, no network.

**Inert until you opt in.** Create `.agent/completion-check.json` with `{"enabled": true}`; add `base_ref` and per-check toggles to taste (`tests_touched` is the strict one, off by default). Full reference: the module docstring in `DevKit/.claude/hooks/completion-check.py`.

**Commit the kit before enabling it** — `.claude/skills/**` is itself a forbidden path, so an uncommitted install reads as a wall of violations on the first turn.

## Permissions

Defaults lean *local and reversible is allowed; outward-facing and destructive asks*:

- **allow** — reads, edits, test/build/lint runners, read-only `git` and `gh`.
- **ask** — `git push`/`reset`/`rebase`/`merge`, `gh pr create`/`merge`, dependency installs, and edits to `.env*`, `CLAUDE.md`, `OWNERSHIP.md`, `PROJECT.md`, `.claude/**`.
- **deny** — force pushes, `rm -rf`, `sudo`, `curl`/`wget`, reads of secrets, keys, `.env`.

Two consequences: `metrics-recorder`'s optional POST to a central endpoint is off (`curl` is denied; the local JSONL write is unaffected), and `visual-diff`'s Playwright invocation needs adding to `allow` or it prompts on every capture.