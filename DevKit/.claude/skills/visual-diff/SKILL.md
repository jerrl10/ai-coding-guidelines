---
name: visual-diff
description: "Use this skill whenever a ticket touches frontend paths declared in STACK.md, before pr-hygiene opens the PR. Captures before/after screenshots and runs pixel-diff plus vision-model review on the changed routes. Pixel diff is the hard gate (blocks merge on unexplained diffs); vision review is the soft gate (flags semantic regressions). Skip if the project has no frontend paths or the diff doesn't touch them."
---
# visual-diff

Screenshot-based regression detection for frontend changes. Layered: pixel diff as the hard gate, vision-model review as a soft gate.

## When to load

Load after implementation is complete on any ticket that touched paths listed in `.agent/STACK.md` under "Frontend paths." Runs before `pr-hygiene` opens the PR.

If no frontend paths in `STACK.md` or none touched in the diff: this skill does not run. `pr-hygiene` will see no visual-diff artifact and accept `N/A — no frontend changes` in the PR body.

## Job

For each route affected by the change:

1. Capture a baseline screenshot on the base branch (or load from stored baseline).
2. Capture a candidate screenshot on the feature branch.
3. Run pixel-diff between them.
4. If diff exceeds threshold: run vision-model review to classify as intentional-vs-regression.
5. Produce a report in `.agent/tickets/<id>/visual-diff/` with before, after, diff PNGs, and a summary.

## Output

```
.agent/tickets/<id>/visual-diff/
  report.md                    # summary; linked from PR body
  routes.json                  # list of routes captured + their status
  <route-slug>/
    before.png
    after.png
    diff.png                   # pixelmatch output
    vision-review.md           # vision model's assessment, if run
```

`report.md` format:

```markdown
# Visual diff report — #<ticket>

## Routes with changes

- `/checkout` — 3.2% pixel diff. Vision review: **intentional** (matches ticket "add promo code field").
- `/account` — 0.1% pixel diff. Below threshold, not flagged.
- `/admin/users` — 14.7% pixel diff. Vision review: **potential regression** (new element appears to overlap existing table; ticket does not mention admin changes).

## Routes unchanged

- `/`, `/pricing`, `/about`, `/login`, `/signup` (22 routes total)

## Agent assessment

<cs score on whether visual changes match ticket intent + one-sentence summary>
```

## Rules

**Which routes to capture:** read `STACK.md` Frontend paths. For each app, use its declared route enumeration mechanism (Next.js: directory scan of `app/**/page.tsx`; Django: URL conf; etc.). If the project doesn't declare how to enumerate routes, fall back to a list in `.agent/visual-diff-routes.txt`.

**Viewports to capture:** default to three — mobile (375×667), tablet (768×1024), desktop (1440×900). Projects can override via `.agent/visual-diff-config.json`.

**Capture conditions:** run against the local dev server per `RUNBOOK.md`. Wait for network idle before capturing. Disable animations (inject `* { animation-duration: 0s !important; transition-duration: 0s !important; }`) to reduce false positives.

**Thresholds (starting point, tune per project):**
- Pixel per-pixel tolerance: 0.1 (pixelmatch default).
- Route fails pixel diff if > 1% of pixels differ.
- Tune in `.agent/visual-diff-config.json` if false-positive rate is high.

**Vision review only runs on routes that failed pixel diff.** Cost control. Vision model receives: before PNG, after PNG, diff PNG, the ticket title and body, and the plan.md Approach section. It classifies each route as `intentional`, `potential-regression`, or `unclear`.

**Baselines are stored via Git LFS** (or flat commits for projects with <50 routes — revisit at scale). Per-route, per-viewport PNGs under `.agent/visual-diff-baselines/`. Never modified autonomously by the agent.

**Baseline updates require human approval.** When a PR with visual changes is merged, a follow-up CI job (separate workflow, not this skill) updates baselines only for routes the reviewer marked approved in the PR. Unreviewed routes keep their old baseline.

**PR body content:** `pr-hygiene` reads `report.md` and summarizes:
- One-line summary of what changed visually.
- Explicit statement of whether the change matches ticket intent.
- Link to full report and images.

If any route is flagged `potential-regression` and the agent cannot explain why based on the ticket, the skill does not write a "change matches intent" claim — it surfaces the regression concern for human review. `pr-hygiene` then blocks or flags based on project policy (strict: block PR; lenient: add `needs-visual-review` label).

## Failure mode

**Dev server won't start locally:** halt. Most likely RUNBOOK is out of date. Escalate with specifics.

**Route enumeration fails:** halt. Ask for `.agent/visual-diff-routes.txt` to be populated manually, or for the project to declare its enumeration approach in STACK.md.

**Pixel diff library not installed:** the skill expects `pixelmatch` and `pngjs` (for JS projects) or equivalents. If missing, halt and surface the install command. Do not silently skip visual diff.

**Vision model API unreachable:** run pixel diff only, skip vision review, note the degraded mode in `report.md`. Do not block the PR on vision review alone — pixel diff remains the hard gate.

**No baseline exists for a route** (first time seeing this route): capture a baseline on the base branch as the reference. Note "baseline created this run" in the report. This is expected during rollout; flag if it keeps happening after routes have stabilized.

## Tooling dependencies

- Playwright (capture), headless mode. Cross-browser optional; default to Chromium only.
- `pixelmatch` + `pngjs` (for JS/TS projects) or `odiff-bin` (faster, Rust-based) or `pixelmatch-py` (for Python projects).
- Git LFS for baseline storage (for projects with > 50 routes).
- Access to a vision-capable model API (Claude, GPT-4-class). API key comes from project's secret source per `INFRA.md`.

These are intentionally swappable. The skill describes the contract (capture, diff, review, report) not the exact tools. Project-specific skills can override.

## Known weaknesses

- **Threshold tuning is empirical.** Starting values will produce some false positives in the first few PRs. Expect to tune in the first week.
- **Baselines can diverge silently.** If a project goes weeks between PRs, baselines can stale against dependency upgrades (e.g., a Tailwind update changes defaults). Solution: periodic baseline refresh PRs, reviewed by humans.
- **Animation and video content.** Even with animation disabled, some components (video players, canvas, iframes with third-party content) produce inconsistent screenshots. Exclude specific selectors per project via config.
- **Internationalization.** If the app has multiple locales, the capture matrix multiplies. Default to the primary locale; add others explicitly per project if needed.

## See also

- `pr-hygiene` skill (reads `report.md`, enforces "no PR if visual-diff missing on frontend changes")
- `.agent/STACK.md` — Frontend paths section is load-bearing
- `.agent/RUNBOOK.md` — how to start the dev server locally
- `.agent/visual-diff-config.json` (per-project) — thresholds, viewports, exclusions
- `.agent/visual-diff-baselines/` (per-project, LFS-tracked) — reference screenshots
