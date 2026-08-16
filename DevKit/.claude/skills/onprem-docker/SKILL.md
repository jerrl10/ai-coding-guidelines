---
name: onprem-docker
description: "Operational map for projects deployed to on-premise Docker (docker-compose or similar, no managed platform). Covers log access, deploys, rollback, and the secrets map. Use when INFRA.md declares on-prem Docker as the deploy target. STUB — fill in per project before relying on it."
---

# onprem-docker

**Status:** STUB. Fill in before use.

## When to load

Load when `.agent/INFRA.md` declares on-premise Docker (docker-compose or similar, no managed platform) as the deploy target.

## Job

Provide the "how do I actually operate this project on on-prem Docker" knowledge: log access, deploys, rollback, secrets map. Contains the map, not the credentials.

## What should go here

- Log access (CLI snippet, where logs are stored, retention).
- Deploy pipeline (how triggers fire, how to deploy manually as a fallback).
- **Rollback (preferred + fallback).** Incident-critical section.
- Secrets (where they live, how services access them, never the values).
- Networking (URLs, internal vs public, Cloud SQL / DB access paths).
- Monitoring (where alerts route, how to silence, how to check uptime).
- Common failure modes specific to this platform.

## What should NOT go here

- Actual credentials, secret values, or service account keys.
- Project-specific names (those live in `.agent/INFRA.md`).
- Generic DevOps tutorials.

## See also

- `gcp-cloudrun` skill for a filled example.
- `.agent/INFRA.md` in the target repo.
