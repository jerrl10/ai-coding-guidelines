---
name: triage
description: "Use this skill whenever a new GitHub issue is opened or re-opened on a project the harness runs on. Classifies the issue (bug / feature / question / spam), checks LEARNINGS.md for prior art on similar tickets, and decides what comes next in the flow (reproduce → think for bugs, scope-estimate → think for features, etc.). Low-confidence classifications get the 'needs-triage-human' label and stop rather than guessing."
---
# triage

First-line handler for new GitHub issues. Classifies, checks prior art, decides what comes next.

## When to load

Load when a new GitHub issue is opened (or re-opened) on a project the harness runs on. Runs before `reproduce`, `scope-estimate`, and `think`.

## Job

1. Read the issue body and any attachments.
2. Read `.agent/PROJECT.md` — specifically "What this project does", "Critical paths", "Active work themes".
3. Grep `.agent/LEARNINGS.md` for tags or keywords matching the issue area.
4. Classify the issue: bug / feature / question / spam.
5. Decide the next step based on classification and confidence.

## Output

A triage comment posted on the issue, with:
- Classification label.
- Reference to any similar past entries in `LEARNINGS.md`.
- Decision: answer-and-close / small-fix / hand-to-implementation / needs-human.
- If `needs-human`: a specific question for the human to answer.

GitHub labels applied:
- `kind/bug`, `kind/feature`, `kind/question`, or `kind/spam`.
- `triaged`.
- If unclear: `needs-triage-human`.

## Rules

**Use PROJECT.md to inform priority, not just the ticket text.** A "minor UI polish" ticket in an area flagged as a critical path is not minor. Surface the mismatch in the triage comment.

**Check LEARNINGS.md before proceeding.** If a similar past issue exists, reference it in the triage comment. The fix may be faster than a fresh investigation.

**Low-confidence classification → halt.** If you cannot classify the issue with `cs >= 6`, label it `needs-triage-human` and stop. Do not proceed to `reproduce` or `think` on an unclassified ticket.

**Questions can be answered and closed.** If the issue is a question (not a bug or feature) and `.agent/PROJECT.md` or `.agent/RUNBOOK.md` has the answer, post it in the comment and close the ticket. Note in `LEARNINGS.md` if the answer was non-obvious (might suggest a PROJECT.md update).

**Spam is closed with a short note.** Do not engage.

## Classification heuristics

| Signals | Likely classification |
|---|---|
| "broken", "error", "doesn't work", stack trace, reproduction steps | bug |
| "should", "could", "would be nice", "feature request", "add support for" | feature |
| "how do I", "what's the way to", "where is the …" | question |
| Off-topic, promotional, unrelated | spam |

These are heuristics, not rules. Use judgement.

## Failure mode

**Issue is ambiguous or multi-topic:** label `needs-triage-human` and ask one specific clarifying question on the issue. Do not try to guess. Do not proceed.

**PROJECT.md is missing or stale (> 6 months old):** halt and flag to human. You cannot triage on the assumption of critical paths you can't verify.

## See also

- `reproduce`, `scope-estimate`, `think` skills (next in the flow)
- `.agent/PROJECT.md`, `.agent/LEARNINGS.md`
