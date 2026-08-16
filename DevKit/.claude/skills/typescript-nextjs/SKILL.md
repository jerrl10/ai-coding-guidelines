---
name: typescript-nextjs
description: "Non-obvious conventions for Next.js projects in TypeScript — App vs Pages Router, Server vs Client Components, data fetching, routing files, middleware, and version-sensitive notes. Use when STACK.md declares Next.js, when planning or implementing Next.js code, or when reviewing it. Thin by design; assumes the agent knows the framework."
---

# typescript-nextjs

Conventions and non-obvious rules for Next.js projects in TypeScript. Thin by design — covers only things the model would get wrong by default.

## When to load

Load when `.agent/STACK.md` declares Next.js as a framework. Works alongside `typescript-node`.

## Job

Supply Next.js-specific conventions the agent should follow during planning and implementation. Does not teach Next.js; assumes the agent knows the framework broadly.

## Conventions

**App Router vs Pages Router.** Read `STACK.md` to determine which the project uses. The two have different mental models:
- App Router (default for new projects): Server Components by default, `"use client"` opt-in, file-based routing under `app/`.
- Pages Router (legacy): Client Components by default, `pages/` directory, `getServerSideProps` / `getStaticProps`.

Do not mix — a project is one or the other. If both coexist in the tree, that's a migration in progress; check `STACK.md` Deprecated section.

**Server vs Client Components (App Router).**
- Server Components cannot use React hooks, cannot use `window`/`document`, cannot handle events directly.
- Client Components must be marked with `"use client"` at the top of the file.
- A Server Component can import and render a Client Component; the reverse is awkward (pass as children or import dynamically).
- When in doubt, prefer Server Components. Pushing `"use client"` down the tree keeps bundles small.

**Data fetching in App Router.**
- Server Components: use `fetch()` directly, or call DB/service code directly. Next.js extends `fetch` with caching options.
- Client Components: use SWR, React Query, or similar. Do not fetch in `useEffect` for initial data — it's worse than Server Component fetching.

**Routing files.** `app/path/page.tsx` is the route. `layout.tsx`, `loading.tsx`, `error.tsx`, `not-found.tsx` have specific meanings — don't repurpose them.

**Metadata / SEO.** Use the `metadata` export or `generateMetadata` function in `layout.tsx` / `page.tsx`. Do not use `<head>` tags directly in App Router — they won't render correctly.

**Middleware is edge-runtime by default.** `middleware.ts` at the root runs on the Edge runtime. Node-only APIs (fs, full Node stdlib) won't work there. Check before using a Node dep in middleware.

## Version-sensitive notes

Next.js moves fast. Check `package.json` for the exact version. Major version differences to know:

- Next.js 13+: App Router introduced.
- Next.js 14+: Server Actions stable (no longer experimental flag).
- Next.js 15+: React 19, async request APIs (cookies, headers, params).

If the project pins an older version, stay within its capabilities. Do not propose upgrading as part of a bug fix.

## Integration with harness skills

- **safe-edit:** `app/api/**` routes should generally be `review` tier. Auth-related routes (`app/api/auth/**`, `app/api/login/**`) are usually `forbidden`. Check project's `OWNERSHIP.md`.
- **test-first:** Server Components are hard to unit-test in isolation — prefer integration tests via Playwright. Client Components test fine with Vitest + Testing Library.
- **visual-diff:** Next.js projects are prime territory for visual-diff. `STACK.md` Frontend paths should include `app/**/page.tsx` and `app/**/layout.tsx` at minimum.

## Common failure modes

**Adding `"use client"` to a whole file when only one child needs it.** Push the boundary down instead. One leaf Client Component beats marking the whole tree.

**Calling a Server Action from a Client Component without proper setup.** Server Actions need the `"use server"` directive and must be imported, not inlined.

**Using `getServerSideProps` in App Router.** Different world — doesn't exist there. If you see a plan proposing it on an App Router project, the agent is confused.

## See also

- `typescript-node` skill (runs alongside for shared TS conventions)
- `.agent/STACK.md` (for framework version and router choice)
- Next.js docs at `https://nextjs.org/docs` (search-first skill for version-sensitive claims)
