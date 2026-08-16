---
name: typescript-node
description: "Non-obvious conventions for TypeScript on Node.js (not Next.js, not Deno) — version-sensitive patterns, project-structure norms, test-runner specifics, and integration points with safe-edit, test-first, and visual-diff. Use when STACK.md declares TypeScript on Node. Thin by design, not a language tutorial. STUB — fill in per project before relying on it."
---

# typescript-node

**Status:** STUB. Fill in with project-relevant non-obvious conventions before use.

## When to load

Load when `.agent/STACK.md` declares TypeScript running on Node.js (not Next.js / not Deno).

## Job

Supply typescript-node-specific conventions the agent should follow during planning and implementation. Thin by design — cover only things the model would get wrong by default. Not a language tutorial.

## What should go here

- Version-sensitive conventions (what's different between major versions).
- Non-obvious project structure norms.
- Test runner specifics beyond what's in STACK.md.
- Patterns the ecosystem's model defaults would get wrong.
- Integration points with `safe-edit`, `test-first`, `visual-diff`.

## What should NOT go here

- General language tutorials.
- Style rules that are the ecosystem's standard.
- Things the model already does correctly without prompting.
- Dependency lists (those live in the project's lockfile).

## See also

- `typescript-nextjs` for a filled example of a stack skill
- `.agent/STACK.md` in the target repo
