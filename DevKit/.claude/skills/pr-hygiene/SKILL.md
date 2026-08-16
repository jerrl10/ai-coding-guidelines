---
name: pr-hygiene
description: "Use this skill when the agent is ready to open a pull request — implementation done, tests passing, intending to call `gh pr create`. Produces a structured PR description a human can review in under 2 minutes. Checks preconditions: plan.md exists, tests exist for non-doc changes, no forbidden-path edits, visual-diff present if frontend touched. Enforces the risk rubric. Blocks if any precondition fails — refuses to open the PR rather than producing one that will be rejected."
---
# pr-hygiene

Produce a PR description that a human can review in under 2 minutes. Open the PR. Block if preconditions fail.

## When to load

Load when the agent is ready to open a PR — after implementation, tests, and (for frontend changes) visual-diff have completed.

Also loaded by `escalation` (via `→ next: pr-hygiene --draft`) to open a **draft** PR that carries an escalation — e.g. forbidden-path patches the human must apply, or a decision the human must make. In draft mode the body is the escalation document and several preconditions are relaxed (see "Draft mode").

## Job

1. Check preconditions.
2. Generate `.agent/tickets/<id>/pr-body.md` from the template.
3. If any check fails, refuse to open the PR and surface what's missing.
4. On success, run `gh pr create --body-file <pr-body.md>`.
5. Write the resulting PR URL back into `plan.md` and `handoff.md`.

## Output

- File: `.agent/tickets/<id>/pr-body.md` — the PR body, written before push for auditability.
- Action: `gh pr create --body-file <file>` — opens the PR against the default branch (or the branch specified by the ticket, if any).
- Updates: PR URL appended to `plan.md` and the latest `handoff.md` entry.

## Preconditions (block PR if any fail)

0. The Completion check statement has been emitted for this ticket in the current turn. The `completion-check` Stop hook enforces this at end-of-turn, but `pr-hygiene` also checks here so the missing statement is surfaced mid-turn rather than at hook time. If missing, halt; emit the Completion check first (see `.claude/hooks/completion-check.py` in the project template, or the hook's failure message which includes the required schema). The `→ next` field in the statement tells `pr-hygiene` whether to open a regular PR (`gh pr create`) or a draft PR (`gh pr create --draft`).
1. `.agent/tickets/<id>/plan.md` exists.
2. For non-doc-only changes: new or modified test files exist in the diff.
3. No forbidden-path edits in the diff (cross-check against `OWNERSHIP.md`).
4. If `STACK.md` declares frontend paths and the diff touches them: visual-diff artifact present at `.agent/tickets/<id>/visual-diff/`.
5. All `review`-tier paths in the diff are listed in the PR body's Review-tier section.
6. The plan.md Files list and the actual diff agree — or divergence is surfaced in the PR body.

If any precondition fails, produce a "not ready for PR" report naming the missing piece and the skill to load next. Do not open the PR.

## Draft mode (`pr-hygiene --draft`)

When invoked by `escalation`, the goal is the opposite of a finished PR: surface blocked or undecided work so a human can act asynchronously via PR comments. Behavior changes:

- Open with `gh pr create --draft`. Never mark ready-for-review; the human un-drafts (or comments `@claude` to resume).
- The PR **body is the escalation document** (`.agent/tickets/<id>/escalation.md`), not the standard finished-PR template. It must end with a `## How to resume` section naming the exact `@claude ...` comment that unblocks it.
- Relaxed preconditions: #2 (tests present) and #4 (visual-diff) do NOT block — the work is intentionally incomplete. Still enforced: #0 (Completion check emitted), #1 (plan.md exists), #3 (no forbidden-path edits actually committed — draft patches live in the body as text, never applied), #5 (review-tier paths listed).
- The branch must satisfy the `escalation` skill's **stateless-resume contract**: all context committed to files, because the resuming agent (GitHub Action) has no memory of the interactive session.

## PR body template

See `pr-body-template.md` in this skill dir. Required sections:

- **What & Why** — max 2 sentences. Longer = the PR is doing too much; split.
- **Risk** — 🟢/🟡/🔴 per the always-on `risk-rubric` rule (loaded via `CLAUDE.md`). Not agent's free choice; rubric-driven.
- **Changes** — bullets per logical change, not per file.
- **Review-tier edits** — paths from OWNERSHIP check with what to verify.
- **Tests** — Added (with test names) / Modified (with reasons) / Coverage delta or "N/A".
- **Visual diff** — link to artifact + one-line summary of whether change matches ticket intent, or "N/A — no frontend changes."
- **Rollback** — one sentence. If migration present, must address the schema change specifically.
- **Agent trail** — links to plan.md, final handoff.md, `cs` score.
- **Reviewer checklist** — static items plus dynamic items generated from the diff (see `dynamic-checklist.md`).

## Rules

**Two-sentence What & Why maximum.** If you can't fit it in two sentences, split the PR.

**Diff size check.** If > 400 lines changed across > 10 files on a non-mechanical change, prompt to split.

**Risk rubric is hardcoded.** The agent does not pick freely. The `risk-rubric` rule (always-on via `CLAUDE.md`) sets the floors.

**Bullets per logical change.** A 5-file change with one intent = one bullet. Do not mirror the file tree.

**Empty Tests.Added on a bug fix is a block.** Refuse to open the PR; send the agent back to `test-first`.

**Rollback must be actionable.** "Revert this commit" is not a valid rollback if a migration is in the diff.

**Auto-merge is never enabled.** This harness requires explicit human approval on every PR. `pr-hygiene` does not use `gh pr merge --auto`.

## Dynamic checklist items

Generated from the diff, appended to the static checklist in the PR body:

| Diff contains | Checklist item added |
|---|---|
| New migration | "Migration is reversible / has a `down`" |
| Modified existing migration | "This should have been blocked by safe-edit — investigate" |
| New dependency | "License check, size check, maintainer check" |
| Dependency major bump | "Changelog reviewed for breaking changes" |
| New env var | "`.env.example` and INFRA.md updated" |
| API route signature change | "Consumers identified and updated (or flagged)" |
| New public export | "Intentional part of public API, or should be internal?" |
| File deletion > 50 lines | "Confirmed unused (grep result in PR body or plan)" |
| Touched review-tier path | "Reason and specific check listed in Review-tier section" |

Extend the table in `dynamic-checklist.md` as new patterns emerge.

## Failure mode

- Plan.md missing → halt. Load `think` to produce a retroactive plan, then retry. (This should not happen in a well-run flow, but handle the case.)
- Tests missing on bug fix → halt. Load `test-first`.
- Visual-diff artifact missing on frontend change → halt. Load `visual-diff` (or flag that visual-diff is unavailable and require explicit note in PR body).
- Forbidden-path edit in diff → halt. This is a safe-edit bypass and should be surfaced as an incident, not silently fixed.
- Diff exceeds size threshold → prompt agent to split; do not open PR.

## See also

- `pr-body-template.md`
- `risk-rubric` rule (in `CLAUDE.md`) — risk-tier floors
- `safe-edit` rule (in `CLAUDE.md`) — pre-write OWNERSHIP classification
- `dynamic-checklist.md`
- `test-first`, `visual-diff`, `escalation` skills
- `.agent/OWNERSHIP.md`, `.agent/STACK.md`
