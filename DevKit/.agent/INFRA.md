# INFRA.md

<!--
Target: 100-200 lines.
More structured than STACK.md because incident response uses this —
every ambiguity is a minute lost when prod is on fire.

NEVER put actual credentials in this file. Names of secrets, not values.
-->

## Deploy target

- **Prod:** <platform + region + project/account ID>
- **Staging:** <same>
- **PR previews:** <platform or "none">

## Deploy trigger

- **Prod:** <how deploys fire, e.g., "merge to `main` → GitHub Actions `deploy-prod.yml`">
- **Staging:** <same>
- **Manual deploy:** <command + approval step, if any>

## Rollback

<Incident-critical. Working command in under 10 seconds of reading.>

- **Preferred:** `<command>` — <what it does, approx time>
- **Fallback:** <slower-but-always-works path>

## Secrets

- **Source:** <where secrets live — Secret Manager / SSM / Vault / other>
- **Injected:** <how services access them>
- **Local dev:** `.env.local` (not committed), template at `.env.example`
- **Never committed:** `.env`, `.env.local`, `.env.production`
- **Who can access:** <names + request channel>

## Databases

- **Prod:** <instance, version, access path>
- **Staging:** <same>
- **Access from local:** <command to connect>
- **Never edit prod DB directly.** Migrations via `<deploy command>` only.

## Logs

- **App logs:** <where they go>
- **CLI:** `<copy-paste command to read recent errors>`
- **Retention:** <days>
- **Structured fields:** <which fields are worth filtering on>

## Monitoring / alerts

- **Uptime:** <what, where, frequency>
- **Errors:** <alert rule>
- **Alerts route to:** <PagerDuty / Slack / email>

## CI

- **Provider:** <GitHub Actions / GitLab CI / other>
- **Test workflow:** `<path>`
- **Deploy workflows:** <see "Deploy trigger" above>

## Environment variables (schema)

- **Full list:** `<path to canonical schema file>`
- **Changes:** require matching updates to `.env.example` and this file.

---

**Last updated:** <ISO date>
