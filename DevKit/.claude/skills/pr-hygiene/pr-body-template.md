## What & Why

<One sentence: what this changes. One sentence: why it changes.>

Closes #<ticket>.

## Risk: 🟢 low | 🟡 medium | 🔴 high

<One sentence justifying the risk level.>

## Changes

- <bullet per logical change, not per file>
- <each bullet: what, which path(s), why>

## Review-tier edits (from OWNERSHIP.md)

<Paths classified as `review` that this PR touches. Empty if none.>
<Format: `path — reason it's in review tier — what to check`>

## Tests

- **Added:** <new test names + what they prove>
- **Modified:** <existing tests changed + why>
- **Coverage:** <delta if measurable, otherwise "N/A">

## Visual diff

<If frontend: link to `.agent/tickets/<id>/visual-diff/` + one-line summary of what changed visually and whether it matches ticket intent.>
<If not frontend: "N/A — no frontend changes.">

## Rollback

<One sentence: how to undo this if it breaks prod.>

## Agent trail

- Plan: `.agent/tickets/<id>/plan.md`
- Final handoff: `.agent/tickets/<id>/handoff.md`
- Confidence on correctness: `cs<N>`

## Reviewer checklist

- [ ] Risk level matches actual risk
- [ ] Review-tier edits are justified
- [ ] Tests cover the reported behavior
<!-- dynamic items appended here by pr-hygiene based on diff -->
