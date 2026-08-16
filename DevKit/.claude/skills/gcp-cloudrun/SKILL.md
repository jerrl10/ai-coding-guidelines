---
name: gcp-cloudrun
description: "Operational map for projects deployed to GCP Cloud Run — reading logs, understanding deploys, executing rollbacks, and locating secrets. Use when INFRA.md declares Cloud Run as the deploy target, or when investigating a Cloud Run incident (logs, rollback, failed deploy, cold starts)."
---

# gcp-cloudrun

Operational knowledge for projects deployed to GCP Cloud Run. Provides the map to logs, secrets, deploys, and rollback.

## When to load

Load when `.agent/INFRA.md` declares Cloud Run as the deploy target.

## Job

Provide the "how do I actually operate this project on GCP" knowledge that lets the agent read logs, understand deploys, and execute rollbacks. Contains the map, not the credentials.

## Logs

Cloud Logging is the default log sink. Read from the CLI:

```bash
gcloud logging read \
  'resource.type="cloud_run_revision" AND severity>=ERROR' \
  --limit=50 \
  --format=json \
  --project=<project-id>
```

Filter by service name:
```bash
gcloud logging read \
  'resource.type="cloud_run_revision" AND resource.labels.service_name="<service>"' \
  --limit=50 \
  --project=<project-id>
```

Filter by trace ID (useful once you have a request ID):
```bash
gcloud logging read \
  'trace="projects/<project-id>/traces/<trace-id>"' \
  --project=<project-id>
```

Retention is typically 30 days on the default `_Default` log bucket unless the project configured longer retention. Check `INFRA.md` for project-specific retention.

## Deploys

Cloud Run services deploy from container images. Typical flows:

- **GitHub Actions → Cloud Run:** workflow builds a container, pushes to Artifact Registry, calls `gcloud run deploy`. The workflow file is the source of truth; read it from `.github/workflows/`.
- **Cloud Build trigger:** a GCP-side trigger on git push. Less visible from the repo; check `INFRA.md` for the trigger definition.

To deploy manually (rarely correct — usually prefer re-running the workflow):
```bash
gcloud run deploy <service> \
  --image=<image-ref> \
  --region=<region> \
  --project=<project-id>
```

## Rollback

Cloud Run keeps revision history. Rollback is "route 100% of traffic to the prior revision."

List revisions:
```bash
gcloud run revisions list \
  --service=<service> \
  --region=<region> \
  --project=<project-id>
```

Route traffic to a specific revision:
```bash
gcloud run services update-traffic <service> \
  --to-revisions=<revision-name>=100 \
  --region=<region> \
  --project=<project-id>
```

Rollback time: ~30 seconds to route traffic. No image rebuild needed. This is the **preferred rollback** for Cloud Run.

**Fallback rollback** (if traffic routing doesn't work for some reason): revert the commit, push, let the deploy pipeline redeploy. Slower (minutes) but always works.

Both should be documented in the project's `INFRA.md` with the specific service names, regions, and project IDs filled in.

## Secrets

Secrets live in GCP Secret Manager. Cloud Run services access them via:

- **Environment variables** bound to secrets at deploy time (most common).
- **Direct API calls** from the service code using the Secret Manager client library.

The service account running the Cloud Run service needs the `roles/secretmanager.secretAccessor` role on the specific secrets.

**Never commit secrets.** `.env*` files for local dev only. Prod secrets come from Secret Manager at runtime.

To list what secrets exist:
```bash
gcloud secrets list --project=<project-id>
```

To read a secret value (requires appropriate role):
```bash
gcloud secrets versions access latest --secret=<name> --project=<project-id>
```

The agent should never actually run these commands to read production secrets unless explicitly instructed and authorized. Know the map; don't casually traverse it.

## Networking

Cloud Run services are reachable via:
- HTTPS URL assigned at deploy (`<service>-<hash>.<region>.run.app`).
- Custom domain mapped via Cloud Run Domain Mappings or a load balancer in front.
- Internal-only services: require authentication via IAM or a VPC connector.

If the service needs to reach a Cloud SQL instance, it's typically via a VPC connector or the Cloud SQL Auth Proxy — check `INFRA.md`.

## Monitoring

- **Uptime checks** in Cloud Monitoring ping a health endpoint periodically.
- **Alerting policies** fire on error rates, latency, or uptime failures.
- **Cloud Trace** captures distributed traces if the service is instrumented.

Where alerts route (PagerDuty / Slack / email) should be in `INFRA.md`.

## Common failure modes

**"It deploys but returns 500 immediately":** usually a missing env var or failed secret binding. Check revision logs for startup errors before assuming a code bug.

**"Logs are empty":** Cloud Run only captures stdout/stderr. If the app writes to a file, those logs are lost on revision shutdown. Make sure logging goes to stdout.

**"Slow cold starts":** Cloud Run scales to zero by default. If latency on first request matters, `--min-instances=1` or higher is the lever. Costs more; surface the tradeoff.

**"Deploy succeeds but old version is serving":** traffic wasn't routed. `gcloud run services update-traffic` with `--to-latest` is the fix.

## See also

- `.agent/INFRA.md` in the target repo (service names, regions, project IDs)
- `generic-ci` skill (for the CI side of deploys)
- GCP docs at `https://cloud.google.com/run/docs` (via `search-first` for version-sensitive claims)
