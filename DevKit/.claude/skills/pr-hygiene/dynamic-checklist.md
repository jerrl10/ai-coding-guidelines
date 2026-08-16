# Dynamic checklist patterns

When generating the PR body's Reviewer checklist, append items based on what the diff contains. This is a living table — add patterns as new failure modes emerge.

| Trigger (diff contains…) | Checklist item |
|---|---|
| New file in `**/migrations/**` | Migration is reversible / has a `down` method or equivalent |
| Edit to existing migration file | **Flag as incident.** safe-edit should have blocked this. |
| New line in `package.json`, `pyproject.toml`, `*.csproj` dependencies | License check, size check, maintainer check |
| Version bump where major number changed in a dep | Changelog reviewed for breaking changes |
| New key added to env schema file (e.g., `packages/env/schema.ts`) | `.env.example` updated AND INFRA.md updated |
| Export signature changed in a public module | Consumers identified and updated, OR breaking change flagged |
| New `export` on a file with no prior exports | Intentional part of public API, or should be internal? |
| File deletion > 50 lines | Confirmed unused (grep result in PR body or plan.md) |
| Diff includes files in review-tier paths | Reason and specific check listed in Review-tier section |
| Lockfile change without package.json change | Stale lockfile update — is this intentional? |
| New GitHub workflow file | Secrets required, triggers correct, runs-on audited |
| SQL seed data changes | Staging/prod seed paths considered |
| CSS/Tailwind config changes | Visual diff covers representative pages |

## Adding patterns

When a reviewer catches something that should have been surfaced automatically, add a row here in the same PR that documents the miss. This is how the checklist becomes the project's compounded review discipline.
