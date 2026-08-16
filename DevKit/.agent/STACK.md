# STACK.md

<!--
Target: 80-150 lines. Bullets, not prose.
Reference files (package.json, .nvmrc, etc.) instead of duplicating when possible.
-->

## Languages

- <language + version, e.g., "TypeScript 5.4 (strict mode)">

## Runtime

- <runtime + version, referencing .nvmrc or equivalent>
- <package manager + version>

## Frameworks

- <framework + version>

## Data

- <database + version, local vs managed>
- <cache / queue, if any>

## Test runners

<Include explicit negative statements: "No Jest. No Cypress." — they're as important as the positives.>

- <runner for unit/component>
- <runner for e2e>

## Build / lint / format

- <build tool>
- <lint tool>
- <format tool>
- <type checker>

## Frontend paths

<REQUIRED section — used by visual-diff skill.
List the paths under which frontend changes live. Used to decide which routes to screenshot.>

- `<path glob>`
- `<path glob>`

## Backend paths

- `<path glob>`
- `<path glob>`

## Non-code artifacts

- Figma: <link>
- Database schema source of truth: `<path>`
- OpenAPI / type spec: `<path>`

## Deprecated or migrating-out

<Paths still present but being removed. Warns agents off extending them.>

- `<path>` — <reason being removed>

---

**Last updated:** <ISO date>
