---
name: csharp-backend
description: "Architecture rules for C# / .NET backends built as vertically sliced modules on ASP.NET Minimal APIs — module boundaries, feature slices, cross-module contracts, endpoint shape, validation, error handling, DI, and configuration. Use when STACK.md declares C#/.NET on the backend, when planning or implementing backend C# code, when reviewing a .NET diff, or when a question touches project references, `internal` visibility, `TypedResults`, endpoint filters, `IOptions<T>`, repositories, or domain events. Load before writing the first line of a new slice — most violations are structural and expensive to undo later."
---

# C# backend architecture

Rules for how backend code is organized, how modules talk, and where each kind of
decision is made. Opinionated and enforced: §15 lists the checks that fail CI.

Full reference: **[backend-architecture.md](backend-architecture.md)**.

## Load this first

Read the reference section that matches what you are about to do. The document
cross-references by section number (§5.1, §7.1, …), so keep the numbering in mind.

| Doing | Read |
| --- | --- |
| Orienting in an unfamiliar solution | §1–3 — purpose, principles, solution layout |
| Adding or splitting a module | §4 — what a module is, ownership, public surface, isolation |
| Adding a feature | §5–6 — slice layout, growth and promotion rules, call flow |
| Making module A talk to module B | §7 — provider-owned contracts, domain events, consistency boundaries |
| Touching a host / `Program.cs` | §8 — HTTP host, worker host, composition root |
| Writing an endpoint | §9–11 — endpoint shape, validation, error handling |
| Wiring services or config | §12–13 — DI chain, lifetimes, typed options |
| Writing tests | §14 — unit / contract / integration split |
| Reviewing a diff | §16 — banned-practices table, then §15 for the CI checks |

## The rules that get broken most

Check these before writing. Each maps to a row in §16.

1. **Vertical slices, not horizontal layers.** No `Controllers/`, `Services/`,
   `Models/` folders. A feature's endpoint, service, repository, DTOs, validators,
   and entity live side by side in one folder. Stay flat until the slice earns
   subfolders (~10–15 files).
2. **Single ownership.** Exactly one module owns a concept — defines the contract,
   holds the entity, runs the writes, authorizes the queries. If two modules want
   to own the same thing, one of them is wrong.
3. **Contracts are provider-owned.** Module A never defines an interface for
   module B's behavior. Reference `B.Contracts`, never `B`. No `InternalsVisibleTo`
   between feature modules. Entities never cross a module boundary — DTOs do.
4. **Endpoints are thin adapters.** `internal static` class, `private static`
   handlers, services as parameters. No validation, no data access, no orchestration,
   no branching on domain state. Return `TypedResults.Xxx(...)`, not bare `IResult`.
5. **Errors propagate.** Throw a specific `AppException` subtype; let the error
   middleware translate it. Never `return TypedResults.BadRequest(new { ... })`, and
   never catch `AppException` in a handler or service.
6. **Validation is a filter, not handler code.** Validators plus the global
   `ValidationFilter` endpoint filter (§10).
7. **Hosts are thin.** `Program.cs`, middleware, options binding, module
   registration. No endpoints, services, entities, or business logic in a host.
8. **Config is typed.** Bind to an options class and inject `IOptions<T>`. Services
   never read `IConfiguration` directly.
9. **Read and write repositories are separate** — `IXReadRepository` +
   `IXWriteRepository`, never one `IRepository` with both.
10. **No cross-module transaction.** Module-local transaction plus a domain event
    (§7.2, §7.3).

## Judgment markers

- **A rule blocks the change you were asked to make** → the rule changes via a
  documented PR editing `backend-architecture.md`, or the code changes. Adding a CI
  exception is not an option (§15).
- **Unsure whether a type belongs in `.Contracts`** → if another module needs it,
  it is a contract. If you reached for `InternalsVisibleTo`, it is a contract.
- **Slice is getting large** → §5.2–5.3 give the growth and promotion rules. Do not
  invent subfolders early; do not let a 30-file slice stay flat.
- **`.csproj` or `Directory.Packages.props` needs changing** → use the `dotnet` CLI.
  Hand-editing the XML is banned (§16).
- **The existing code already violates a rule** → that is a finding, not a licence.
  Note it; do not extend the violation. Widescale cleanup is its own ticket.

## Relationship to other skills

- `think` — a plan that adds a module or crosses a module boundary should name the
  owning module and the contract it goes through, before any code.
- `safe-edit` (in `CLAUDE.md`) — `.Contracts` projects and module boundaries are
  usually `review` tier at minimum. Check `.agent/OWNERSHIP.md`.
- `adr-author` — a new module, a new cross-module dependency, or a deviation from
  this document is an architectural decision. Record it.
- `test-first` — the §14 split decides which test project the failing test goes in:
  unit for a service or validator, contract for a `.Contracts` change, integration
  for a cross-module flow.
- `pr-hygiene` — §16 is a usable review checklist; §15 is what CI will fail on.

## Per-project note

This document describes one house style. If the project it is installed in differs,
edit `backend-architecture.md` to match reality rather than leaving the agent to
reconcile two sets of rules — a standard nobody follows is worse than none.
