---
name: escalation
description: "Use this skill when the agent cannot continue without human judgment — the safe-edit rule blocks a forbidden-path edit, the agent has given up after multiple attempts, plan blockers cannot be resolved, or thrashing is detected. Stricter than handoff: must articulate what was tried, why it failed, and what a human should decide. The skill refuses to escalate without a concrete reasoning trace."
---

# escalation

Structured handoff where the agent explicitly cannot continue without human judgement. Stricter than `handoff`.

## When to load

Load in any of these cases:

- `safe-edit` halted because the change requires a forbidden-path edit. Produce a draft-patch proposal for the human.
- `reproduce` failed after multiple attempts. Surface the gap between ticket report and observable behavior.
- `think` can't produce a valid plan — blockers are non-empty, or problem cannot be restated without more info from a human.
- Agent has tried multiple approaches and is thrashing (handoff count ≥ 4, or time-in-ticket exceeds expected by > 2x).
- Any situation where `handoff` cannot produce a valid Next step.

## Job

Produce a structured escalation document AND surface it as a **draft PR**, so a human who is not in an interactive session can respond asynchronously via PR comments. The document names:

- What the agent tried.
- Why it failed.
- What the agent believes the real problem is, with a confidence score.
- What a human would need to decide or do.

For forbidden-path escalations: include a draft patch that the agent has prepared but not applied.

## Always open a draft PR on escalation

Every escalation opens (or updates) a **draft PR** in addition to writing the escalation document. This is the default channel — do not merely stop in the interactive session, because the human may not be watching it. Steps:

1. Commit work-so-far plus the ticket docs (`.agent/tickets/<id>/plan.md`, `escalation.md`, any partial diff) to the ticket branch.
2. Open a draft PR via `gh pr create --draft` (or update the existing one) whose body **is** the escalation document.
3. End the body with a `## How to resume` section following the **required template below**. Because this section makes the PR self-sufficient for the stateless CI agent, no separate `handoff.md` is needed on the GitHub path. The GitHub Action (`.github/workflows/claude.yml`) picks up `@claude` mentions and resumes the work.

### Required `## How to resume` template

The draft-PR body MUST end with this block. It is the single source of truth for the resuming agent — it has read only the repo and the comment, nothing else.

```markdown
## How to resume

**Already committed on this branch:** <one line — what the agent finished and pushed>
**Human action needed first:** <e.g. "apply the 3 forbidden-path patches above", or "none — just confirm">
**Comment to post when ready:** `@claude <exact imperative, naming a file:line or command>`
**Next action for the agent:** <the one concrete step — e.g. "wire the toggle in src/.../SettingsView.tsx:360, then run `cargo check` and un-draft">
**Do NOT touch:** <paths/scope the resuming agent must leave alone, or "n/a">
```

If any line cannot be filled concretely, the escalation is not ready — resolve it or fall back to `handoff` for a human.

This same flow applies to decision-point escalations that are not forbidden-path (e.g. "verify it runs in the app?" / "which of two approaches?"): put the question in the draft-PR body and stop. The human answers in a PR comment.

## Stateless-resume contract

The agent that resumes from a PR comment is a **fresh instance with no memory of the interactive session** (the GitHub Action spawns a new agent per `@claude` mention). Therefore the PR branch must be self-contained:

- All context needed to continue lives in committed files: `plan.md`, `escalation.md`, the partial diff, and the PR body — never only in chat.
- The `## How to resume` line must be actionable by an agent that has read only the repo and the comment. Vague resumes ("continue the work") fail; name the file, the command, or the decision being confirmed.
- Forbidden-path draft patches stay in the PR body as text; the human applies them and confirms via comment.

## Output

- Draft PR (`gh pr create --draft`) whose body is the escalation document, including the `## How to resume` section. This is the primary, always-on output.
- GitHub issue comment with the escalation document (when the ticket originates from an issue).
- Label on the issue/PR: `escalated` (or project-specific equivalent).
- Assignee: the project's primary contact per `.agent/PROJECT.md`.
- Optionally: Slack/messaging ping if the project's INFRA.md declares a channel for escalations.

## Rules

**Not allowed to escalate without articulating why.** If the agent cannot explain in one paragraph what it tried, why it failed, and what it thinks the real problem is, it is not allowed to escalate — it must either try one more concrete approach or ask a specific clarifying question. This prevents "bounce the ticket back at first friction" behavior.

**Draft patches are drafts.** On forbidden-path escalations, the agent produces a patch as text in the comment but does not apply it. The human can copy-apply, edit-then-apply, or reject. This preserves the human decision while giving them the speed benefit of a ready-to-use draft.

**State what you would need.** Every escalation must name what would unblock it: a decision from a human, access to a resource, a clarification on the spec. "I give up" without a named need is not a valid escalation.

**Confidence on diagnosis.** Use `cs` score on the agent's belief about the real problem. `cs < 5` means the agent is guessing — say so explicitly. A confident wrong diagnosis is worse than an honest low-confidence one.

**Forbidden-path escalation always has this structure:**

````markdown
## Forbidden-path escalation

**Path:** `<file path>`
**Classification:** forbidden (reason: <from OWNERSHIP.md>)
**Ticket:** #<ticket-id> — <title>

### Proposed change

<What the change would do, in prose.>

### Why it's needed

<Why this ticket cannot be solved without touching this path.>

### What a human should verify

- <specific thing 1>
- <specific thing 2>

### Draft implementation

```patch
<unified diff; NOT applied>
```

### Confidence

cs<N> on the fix being correct. cs<M> on side effects.
````

## Failure mode

**Agent cannot articulate what it tried:** this is a sign the agent is guessing. Force it to re-run through the state: what's done, what's in progress, what specifically failed. If it still can't articulate, load `handoff` with trigger `blocker` instead and accept that the ticket is in a messy state for the human.

## Interaction with handoff

`escalation` is a stricter version of `handoff`. The difference:
- `handoff` says "here's where I am, someone pick up."
- `escalation` says "I cannot continue without a human decision."

When in doubt, use `handoff` — it's more permissive. `escalation` is for situations where proceeding without human input would be wrong (forbidden paths, thrashing, unresolvable blockers).

## See also

- `safe-edit` rule (invokes `escalation` on forbidden-path attempts)
- `handoff` skill (the permissive cousin)
- `pr-hygiene` skill (`→ next: pr-hygiene --draft` opens the draft PR)
- `.github/workflows/claude.yml` — the Action that resumes work from `@claude` PR comments
- `.agent/PROJECT.md` for the primary contact
