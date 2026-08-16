---
description: Simplify the code changed on this branch — reuse, dedupe, dead-code, clarity, efficiency — without changing behavior. Applies the fixes.
argument-hint: "[optional path or area to focus on]"
allowed-tools: Bash(git branch:*), Bash(git status:*), Bash(git diff:*), Read, Glob, Grep, Edit, Write
---

# Simplify

Make the code changed on this branch simpler, without changing what it does. This is a **quality** pass — reuse, deduplication, dead-code removal, clarity, and cheap efficiency wins. It is **not** a bug hunt and **not** a feature change. Behavior in, behavior out.

If `$ARGUMENTS` is given, scope the pass to that path or area. Otherwise, work the whole diff.

## Current context

- **Current branch:** !`git branch --show-current`
- **Changed files:** !`git diff --name-only main...HEAD`
- **Working-tree changes:** !`git status --short`

## Scope

Review the changed lines and the code immediately around them — enough context to simplify safely, not the whole repo. Read each changed file before touching it. If the diff is empty, say so and stop.

## What to look for

1. **Reuse over reinvention.** A helper, util, or type already exists for this — call it instead of hand-rolling. Search the codebase before assuming nothing fits.
2. **Duplication.** The same logic appears two or more times → extract one well-named function. Don't extract a one-off used once.
3. **Dead code.** Unused variables, params, imports, branches, and functions introduced or left behind by the change → remove them. Confirm truly unused (grep) before deleting.
4. **Needless complexity.** Nested conditionals that flatten with an early return; a manual loop that's a single `map`/`filter`/`reduce`; a temp variable that adds no clarity; an abstraction with one caller that's clearer inlined.
5. **Naming and shape.** A name that misleads or a signature with too many positional args of the same type → fix per the project's conventions.
6. **Cheap efficiency.** Redundant passes over the same collection, repeated lookups that could be hoisted, obviously avoidable allocations. Only when it also reads as simply or more so — never trade clarity for a micro-optimization.

## Rules

**Behavior must not change.** Every edit preserves observable behavior, including edge cases and error paths. If a simplification would alter behavior, it is a bug fix, not a simplification — surface it separately, don't apply it silently.

**Match the surrounding code.** Follow the file's existing patterns, naming, and idioms. Load the project's `coding-standards` skill if present and check edits against it.

**Smaller is the goal, not different.** Prefer the edit that removes lines over the one that rewrites them. Don't restructure a whole module to save two lines.

**Leave clear wins only.** If a change is a judgment call or could be argued either way, skip it or note it — don't churn the diff with debatable rewrites.

**Don't touch what the branch didn't.** Unless `$ARGUMENTS` directs otherwise, don't simplify code unrelated to this branch's changes.

## After applying

1. Run the project's type checker, linter, and tests (see `STACK.md` / `RUNBOOK.md` for the commands). All must stay green.
2. Show `git diff --stat` and summarize what was simplified and why — grouped by the categories above, not file by file.
3. Note anything deliberately left alone and the reason (risk, debatable, out of scope).

Do not commit. The user reviews and commits.
