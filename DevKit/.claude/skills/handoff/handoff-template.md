# Handoff — <ticket-id> — <ticket-title>

<!-- Newest entry at the top. Do not edit prior entries. -->

## <ISO timestamp> — handoff #<N>

**Trigger:** context-exhaustion | blocker | explicit-stop | role-change
**From:** <agent-id or human name>
**To:** <next agent | human lead | reviewer | future-self>

### Next step

<ONE imperative sentence. References a real file:line or real command. No ambiguity.>

Example: "Run `pnpm test apps/web/src/auth/session.test.ts` — it fails on line 47; fix is to await the session promise on line 34."

### State

- **Done:** <what's merged/completed, with file paths>
- **In progress:** <what's mid-change, which branch, which files are dirty>
- **Untouched:** <what was in the plan but not started>

### Decisions made

<Each decision as: "Chose X over Y because Z. Revisit if <trigger>.">
<Only include decisions future-actor would otherwise re-litigate.>

### Blockers

<Each as: "<what's blocking> — <what would unblock it> — <who can unblock>">
<Empty if none.>

### Context pointers

- **Files that matter:** <path:line references>
- **Tests that matter:** <test names + current status>
- **External:** <tickets, docs, Slack threads, PR comments>

### Confidence

**cs<N>** on the Next step being correct. <One sentence if cs < 5.>

---

<!-- prior handoffs remain below -->
