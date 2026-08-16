# RUNBOOK.md

Practical how-to for operating this project locally.

<!--
Target: 150-300 lines.
Every command in copy-paste form. Named, not described.
If a new dev can't get the project running in 15 minutes using this file, it's broken.
Canonical source for setup — README should point here, not duplicate.
-->

## First-time setup

```bash
# Prerequisites: <list versions>
<commands to install deps, set up local env, run migrations, seed data>
```

## Run locally

```bash
<command to start all apps>
<command to start single app>
```

- <app 1>: http://localhost:<port>
- <app 2>: http://localhost:<port>

## Tests

```bash
<unit test command>
<e2e test command>
<visual diff command>
<typecheck command>
<lint command>
```

## Common tasks

### Add a new migration
```bash
<command>
```
See LEARNINGS.md tag `migrations` for gotchas.

### Reset local DB
```bash
<commands>
```

### Regenerate types after schema change
```bash
<command>
```

## Debugging

### App logs locally
<how to read them>

### Prod logs
See INFRA.md > Logs.

### Slow query
<how to inspect>

### Flaky test
Check LEARNINGS.md tag `flaky-tests`. If new, isolate with `<command>`.

## Known gotchas (deep-dive)

See LEARNINGS.md for the full list. The ones worth naming here because
they bite during onboarding:

- <gotcha 1>
- <gotcha 2>

---

**Last updated:** <ISO date>
