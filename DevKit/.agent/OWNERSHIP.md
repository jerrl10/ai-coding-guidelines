# OWNERSHIP.md

Classifies every path in the repo into safe / review / forbidden.
The `safe-edit` rule consults this before every write. Default for unmatched paths: **review**.

If a path matches both safe and forbidden patterns, **forbidden wins**.

---

## forbidden

<Paths the agent may not edit. Requires human override per ticket.>

- `src/**/auth/**` — session handling, token verification. Humans only.
- `src/**/payments/**` — payment integrations, idempotency-critical. Humans only.
- `**/migrations/[0-9]*` — applied migrations; create new, never edit old.
- `**/migrations/V*` — Flyway / similar pattern, same rule.
- `infrastructure/terraform/**` — infra changes go through separate review process.
- `.env`, `.env.local`, `.env.production`, `.env.staging`, `.env.test` — secrets. The file .env.example is deliberately NOT listed here so it defaults to review (editable with human approval).
- `LICENSE`, `NOTICE` — legal text.
- `OWNERSHIP.md`, `.claude/skills/**` — agent does not modify its own rules.
- `SECURITY.md` — security policy.
- `README.md` — project README; agents propose edits via PR but don't self-edit.

<!--
Common additions for specific projects (uncomment and adjust if relevant):
- `src/**/crypto/**` — key derivation, signing.
- `src/**/middleware/cors.ts`, `src/**/middleware/csp.ts`, `src/**/middleware/rateLimit.ts`
- Paths that handle user data deletion
-->

## safe

<Paths where the agent may edit freely, including auto-merge if project policy allows.>

- `**/*.test.ts`, `**/*.test.tsx`, `**/*.test.js`, `**/*.test.jsx`
- `**/*.spec.ts`, `**/*.spec.tsx`, `**/*.spec.js`, `**/*.spec.jsx`
- `**/*.test.py`, `**/test_*.py`, `tests/**`
- `**/*.Test.cs`, `**/*.Tests.cs`
- `__tests__/**`
- `CHANGELOG.md`, `docs/**/*.md`
- `**/*.stories.tsx`, `**/*.stories.ts`
- `**/*.d.ts` (ambient declarations — **exception:** those in `types/` root may be review; adjust per project)
- `**/generated/**`, `**/*.generated.*` — regenerated from schemas

## review

<Default tier for unmatched paths. No need to list; this is the catch-all.>

<!--
Explicit additions here are for paths you want to make extra clear are review-tier
even though they'd default to review anyway. Useful for documenting intent.
-->

## notes

- Lockfile edits (`pnpm-lock.yaml`, `poetry.lock`, `packages.lock.json`) follow the tier
  of the manifest change (package.json / pyproject.toml / .csproj) they accompany.
- If the agent is unsure which tier applies, treat as review and flag in the PR description.
- Changes to this file itself require a human (self-update is forbidden above).
