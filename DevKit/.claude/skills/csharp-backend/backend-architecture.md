# Backend Architecture

## 1. Purpose

Define how backend code is organized, how modules talk, and where each kind of decision is made. Optimize for:

- Localizing change — a feature's implementation lives in one folder.
- Making boundaries real — the compiler enforces module separation, not conventions.
- Keeping hosts thin — all business logic lives in modules; hosts wire them.
- Keeping endpoints thin — HTTP handlers adapt requests to services, nothing more.
- Single ownership — every concept is owned by exactly one module.

Everything else follows from these.

## 2. Guiding Principles

1. **Vertical slicing by feature.** Code is grouped by what it does (a feature), not by what kind of code it is (controller / service / model). A feature's endpoint, service, repository, DTOs, validators, and entity live side by side.
2. **Single ownership.** Every concept is owned by exactly one module. That module defines the contract, holds the entity, runs the writes, and authorizes queries. Nobody else defines the same concept.
3. **Dependencies point inward.** Modules depend on abstractions (`SharedKernel`, `Platform` interfaces). Infrastructure adapters (database clients, message queues, third-party SDKs) depend on module abstractions, never the reverse.
4. **Hosts are thin composition roots.** Hosts contain `Program.cs`, middleware wiring, options binding, and module registration. No endpoints, no services, no entities, no business logic.
5. **Endpoints are thin adapters.** HTTP handlers map requests to service calls and back. They contain no validation, no branching on domain state, no data access, no orchestration. Handlers are `private static` — no instance state, no fields, services arrive as parameters.
6. **Boundaries are compile-time.** Module isolation is enforced by the `.csproj` reference graph plus `internal` visibility. `InternalsVisibleTo` between feature modules is not allowed.
7. **Rules are CI-enforced.** Architectural invariants that the compiler can't express are covered by architecture tests in CI. If a rule can regress silently, it will.

## 3. Solution Layout

```
src/
├── Directory.Build.props         # shared build settings (Nullable, TreatWarningsAsErrors, etc.)
├── Directory.Packages.props      # central package management
├── global.json                   # SDK pinning
├── MyApp.sln
├── src/
│   ├── MyApp.Api/                # HTTP host. Composition root for the web surface.
│   ├── MyApp.Workers/            # Event/queue host. Composition root for async work.
│   │
│   ├── MyApp.ModuleA/            # Feature module
│   ├── MyApp.ModuleA.Contracts/  # Published contracts for ModuleA (public interfaces + DTOs + events)
│   ├── MyApp.ModuleB/
│   ├── MyApp.ModuleB.Contracts/
│   ├── MyApp.ModuleC/
│   ├── MyApp.ModuleC.Contracts/
│   ├── MyApp.ModuleD/
│   ├── MyApp.ModuleD.Contracts/
│   │
│   ├── MyApp.Platform/           # Generic technical adapters (database base, storage, mail, cache, metrics)
│   └── MyApp.SharedKernel/       # Cross-module primitives (identifiers, error types, clock, Result-less exceptions, event bus)
└── tests/
    ├── MyApp.Tests.Unit/         # Fast, in-memory, per-slice
    ├── MyApp.Tests.Contract/     # Verify published contracts against implementations
    └── MyApp.Tests.Integration/  # Real infrastructure via Testcontainers / WebApplicationFactory
```

Project roles:

- **Feature modules** own business logic for their bounded context. Everything inside is `internal`; they expose nothing publicly from the main project.
- **Contracts projects** (`*.Contracts`) are the *only* public surface of a module. They contain interfaces other modules call into, the DTOs those interfaces exchange, and the events the module publishes.
- **Hosts** compose modules and wire infrastructure. They are the only projects that reference feature modules directly.
- **Platform** provides *generic* technical adapters (e.g., a database repository base, an `IEmailSender`). Never per-feature code.
- **SharedKernel** contains types used across three or more modules: value objects, identifiers, common exceptions, the event bus abstraction. Pure, infrastructure-free.

## 4. Modules

### 4.1 What a module is

A module is a bounded context. It groups features that share domain vocabulary, change together, and could reasonably be owned by one team. Modules are coarse — expect three to six per backend, not thirty.

### 4.2 Single ownership

Every concept belongs to exactly one module. When designing the system, decide up front which module owns which type. For example, in a hypothetical app:

- Identity concepts (user, session, role) → `ModuleA`
- Catalog concepts (product, category) → `ModuleB`
- Commerce concepts (order, invoice) → `ModuleC`
- Operations concepts (notification, background job) → `ModuleD`

If two modules both need to know about a product, one owns it and the other queries through the owner's contract. No module ever defines its own parallel representation of a concept owned elsewhere.

When ownership is unclear, that is a signal the module boundaries are wrong — not a signal to duplicate.

### 4.3 Public surface

A module's entire public surface is its `.Contracts` project. That project contains:

- **Interfaces** the module exposes to callers outside itself (e.g., `IWidgetQueryService`, `IWidgetCommandService`).
- **DTOs** those interfaces return or accept (request/response records).
- **Event types** the module publishes (e.g., `WidgetDeleted`).

Everything in the main module project (entities, services, repositories, endpoint classes, internal DTOs) is `internal`. The main module project exposes only a single `public static class ModuleExtensions` with DI registration methods — that class lives in the main project, not in `.Contracts`, because it wires up internal types.

### 4.4 Isolation rules (compile-time)

- A feature module's `.csproj` may reference: `Platform`, `SharedKernel`, and any `*.Contracts` project.
- A feature module's `.csproj` may **not** reference another feature module's main project.
- A `.Contracts` project's `.csproj` may reference: `SharedKernel` only. Not `Platform`, not another `.Contracts` project, not any main module project. Contracts are pure — no infrastructure, no transitive module coupling.
- Hosts may reference everything.
- `InternalsVisibleTo` between feature modules is not permitted. Only test projects and the composition-root hosts may be granted internals access, and then only where unavoidable.

These rules are enforced by CI architecture tests (§15), not just convention.

## 5. Vertical Slicing

Inside a feature module, code is organized by feature, not by layer.

### 5.1 Default slice layout (flat)

```
MyApp.ModuleB/
├── ModuleBExtensions.cs                   # public static class
└── Features/
    ├── Widgets/
    │   ├── WidgetsEndpoints.cs            # MapWidgetsEndpoints + handlers
    │   ├── WidgetsFeatureExtensions.cs    # internal DI registration
    │   ├── IWidgetService.cs
    │   ├── WidgetService.cs
    │   ├── IWidgetReadRepository.cs
    │   ├── IWidgetWriteRepository.cs
    │   ├── WidgetRepository.cs            # implements both
    │   ├── CreateWidgetRequest.cs
    │   ├── CreateWidgetRequestValidator.cs
    │   ├── WidgetResponse.cs
    │   └── Widget.cs                      # internal entity (sealed record)
    ├── Gadgets/
    └── Categories/
```

Everything in `Features/` is `internal`. The slice is self-contained — a single feature's request, service, entity, storage, and validation all live in one folder.

### 5.2 When a slice grows

Past roughly ten to fifteen files in a slice, introduce subfolders — and only then:

```
Features/Widgets/
├── WidgetsEndpoints.cs
├── WidgetsFeatureExtensions.cs
├── Handlers/             # handler methods (if too many to keep in WidgetsEndpoints)
├── Services/
├── Repositories/
├── Requests/             # request/response DTOs + validators
├── Models/               # entities, value objects
└── Events/               # slice-local domain events
```

Premature subfoldering is noise. Stay flat until the slice earns the structure.

### 5.3 Promotion rules

- **Slice → module common.** When a second slice in the same module needs a type, move it up to `Common/` inside the module. Two consumers in one module is enough.
- **Module → SharedKernel or Platform.** When a *third* consumer across *different modules* needs the type, promote it. Two cross-module consumers is a coincidence; three is a pattern.
- **Entities never promote.** An entity stays in the module that owns its lifecycle. Other modules see it only through DTOs in the owning module's `.Contracts`.

### 5.4 Tests mirror the slice

```
tests/MyApp.Tests.Unit/ModuleB/Features/Widgets/
    WidgetServiceTests.cs
    CreateWidgetRequestValidatorTests.cs

tests/MyApp.Tests.Integration/ModuleB/Features/Widgets/
    WidgetsEndpointsTests.cs

tests/MyApp.Tests.Contract/ModuleB/
    IWidgetQueryServiceContractTests.cs    # verify published contract shape
```

## 6. Call Flow Inside a Slice

Each layer calls only the layer directly below. No skipping, no reversing.

```
HTTP → Endpoint handler → Service → Repository → database
                              ↓
                        Platform adapter (storage, mail, external APIs, …)
```

**Endpoint handler** — adapts HTTP. Takes the request and injected services as parameters, calls a service, returns a typed result. No validation, no branching on domain state, no data access, no orchestration.

**Service** — holds business logic. Enforces invariants, orchestrates repositories and `Platform` adapters, publishes domain events on meaningful state changes. Services are the only place domain rules live.

**Repository** — data access only. No business logic. Contracts are split by intent: `IWidgetReadRepository` (query methods), `IWidgetWriteRepository` (command methods). A single concrete class may implement both. A service that only reads must depend only on the read interface.

**Platform adapter** — wraps a technical concern (object storage, mail, external HTTP API). Exposed as an interface in `Platform`, implemented there. Services consume the interface, never the SDK directly.

### 6.1 Endpoint skeleton

```csharp
namespace MyApp.ModuleB.Features.Widgets;

internal static class WidgetsEndpoints
{
    public static IEndpointRouteBuilder MapWidgetsEndpoints(this IEndpointRouteBuilder app)
    {
        var group = app.MapGroup("/widgets").WithTags("Widgets");

        group.MapPost("/", CreateAsync);
        group.MapGet("/{widgetId}", GetAsync);

        return app;
    }

    // Validation has already run via the global endpoint filter (§10).
    // AppException subclasses propagate to the error middleware (§11).
    private static async Task<Created<WidgetResponse>> CreateAsync(
        CreateWidgetRequest request,
        IWidgetService service,
        CancellationToken ct)
    {
        var widget = await service.CreateAsync(request, ct);
        return TypedResults.Created($"/widgets/{widget.Id}", widget);
    }

    private static async Task<Ok<WidgetResponse>> GetAsync(
        string widgetId,
        IWidgetService service,
        CancellationToken ct)
        => TypedResults.Ok(await service.GetByIdAsync(widgetId, ct));
}
```

Every handler is essentially three lines: call the service, wrap with `TypedResults`. If it's longer, something belongs in the service.

Typed results (`Created<T>`, `Ok<T>`, `NotFound`, `Results<T1, T2>`) are preferred over `IResult` — they document what the endpoint can return, flow through to OpenAPI, and give the compiler something to check.

## 7. Cross-Module Communication

Modules talk in two ways and only two ways.

### 7.1 Synchronous: provider-owned contract

When module B needs data or behavior owned by module A, A exposes an interface in `A.Contracts`. B references `A.Contracts`, injects the interface, calls it.

```csharp
// In MyApp.ModuleB.Contracts
public interface IWidgetQueryService
{
    Task<WidgetSummary?> GetByIdAsync(string ownerId, string widgetId, CancellationToken ct);
    Task<int> CountForOwnerAsync(string ownerId, CancellationToken ct);
}

public sealed record WidgetSummary(string Id, string OwnerId, string Name, DateTime CreatedUtc);
```

The implementation lives inside `MyApp.ModuleB` and is registered by `ModuleBExtensions.AddModuleB(services)` in the composition root. Consumers never see the implementation or the underlying entity.

Rules:

- The *owner* defines the contract. Never the consumer.
- Contracts return DTOs, not entities.
- Contracts split read from write, matching §6's repository split. `IWidgetQueryService` vs `IWidgetCommandService`.
- Contracts are stable. Breaking changes to a contract are breaking changes to every consumer — treat them like a public API.

### 7.2 Asynchronous: domain events

When module B needs to *react* to something module A did — but doesn't need an immediate answer — A publishes a domain event and B subscribes.

```csharp
// In MyApp.ModuleA.Contracts
public sealed record UserDeleted(string UserId, DateTime OccurredUtc) : IDomainEvent;
```

Events are published through an in-process bus (`IEventPublisher` in `SharedKernel`). Handlers live in the subscribing module's slice and are registered with DI.

Use events when:

- The reaction is optional from the publisher's perspective — it doesn't care whether any handler succeeds.
- Multiple modules react to the same thing.
- The reaction can be retried independently of the publisher's transaction.

Do *not* use events when the publisher needs a synchronous answer — that's §7.1.

### 7.3 Consistency boundaries

A single transaction never crosses a module boundary. Each module commits its own writes. Cross-module consistency is achieved through events plus idempotent retry, not distributed transactions.

This is the fundamental tradeoff of a modular monolith: strong consistency inside a module, eventual consistency across modules. Accept it explicitly in design.

## 8. Hosts and Composition Root

### 8.1 The HTTP host

Contents:

```
MyApp.Api/
├── Program.cs
├── appsettings.json
├── Composition/          # module registration, middleware pipeline assembly
└── Middleware/           # cross-cutting: error envelope, correlation ID, auth pipeline
```

`Program.cs` does four things:

1. Register options (config binding, `ValidateOnStart`).
2. Register modules (`services.AddModuleA().AddModuleB()…`).
3. Build the app, assemble middleware (error handling, correlation, auth).
4. Map each module's endpoints through a shared root group that carries global endpoint filters (validation, logging enrichment).

```csharp
var endpoints = app.MapGroup("").AddEndpointFilter<ValidationFilter>();

endpoints.MapModuleAEndpoints();
endpoints.MapModuleBEndpoints();
endpoints.MapModuleCEndpoints();
endpoints.MapModuleDEndpoints();
```

No business logic. No features. No repositories. No entities. If a type defines *what the app does*, it lives in a module.

### 8.2 The worker host

The event/queue host. Same shape as the HTTP host but wires event handlers and background-job executors instead of endpoints. Same rule: thin composition root, no business logic.

### 8.3 Composition root responsibilities

Only composition roots:

- Reference all feature modules.
- Wire concrete implementations to abstractions.
- Bind configuration.
- Assemble middleware and pipeline.

Nothing else does these things, ever.

## 9. Endpoints

Endpoints use ASP.NET Core minimal APIs with `TypedResults`. Each slice exposes its routes through a single `MapXxxEndpoints(IEndpointRouteBuilder)` extension on an `internal static` class. Handlers are `private static` methods — no class-level state, no constructor injection, services arrive as handler parameters.

Slices compose into modules. Modules compose into hosts. Each module exposes two methods: `AddModuleX` for DI registration, `MapModuleXEndpoints` for route wiring.

```csharp
// Slice (in the feature folder — see §6.1 for handler bodies)
namespace MyApp.ModuleB.Features.Widgets;

internal static class WidgetsEndpoints
{
    public static IEndpointRouteBuilder MapWidgetsEndpoints(this IEndpointRouteBuilder app)
    {
        var group = app.MapGroup("/widgets").WithTags("Widgets");
        group.MapPost("/", CreateAsync);
        group.MapGet("/{widgetId}", GetAsync);
        return app;
    }

    // private static handlers …
}

// Module (public surface)
public static class ModuleBExtensions
{
    public static IServiceCollection AddModuleB(this IServiceCollection services)
        => services
            .AddWidgetsFeature()
            .AddGadgetsFeature()
            .AddCategoriesFeature();

    public static IEndpointRouteBuilder MapModuleBEndpoints(this IEndpointRouteBuilder app)
    {
        app.MapWidgetsEndpoints();
        app.MapGadgetsEndpoints();
        app.MapCategoriesEndpoints();
        return app;
    }
}

// Host (Program.cs)
builder.Services
    .AddModuleA()
    .AddModuleB()
    .AddModuleC()
    .AddModuleD();

var app = builder.Build();

var endpoints = app.MapGroup("").AddEndpointFilter<ValidationFilter>();
endpoints.MapModuleAEndpoints();
endpoints.MapModuleBEndpoints();
endpoints.MapModuleCEndpoints();
endpoints.MapModuleDEndpoints();
```

Adding a slice to an existing module means editing only the module's two aggregator methods. The host never changes. Adding a new module means registering it in two lines of `Program.cs` (one `Add`, one `Map`).

Group-level metadata — authorization policies, tags, versioning — is applied on the `MapGroup` inside the slice. Cross-cutting filters that should apply everywhere (validation, correlation, logging enrichment) go on the root group in the host.

## 10. Validation

Validation is automatic. A global endpoint filter (`ValidationFilter`) inspects each handler's parameters, resolves `IValidator<T>` from DI for each parameter type where a validator exists, and short-circuits invalid requests with `422 Unprocessable Entity` and field-level error details (RFC 7807 `ValidationProblem`).

The filter is attached once at the root in `Program.cs` (see §8.1); slices don't re-attach it. The `ValidationFilter` itself is a small custom implementation (~20 lines iterating `ctx.Arguments`, resolving `IValidator<>` generically, calling `TypedResults.ValidationProblem` on failure) or pulled from a community package. Unlike MVC, FluentValidation's official integration does not cover minimal APIs automatically — the filter is an explicit piece of code that lives in `SharedKernel` or similar.

Validators live in the slice, next to the request DTO (`CreateWidgetRequestValidator.cs`). Validators are auto-registered by assembly scanning inside each module's `AddXxxFeature()` method.

Endpoint handlers never validate manually. A handler that starts with `if (string.IsNullOrEmpty(...)) return TypedResults.BadRequest(...)` is a bug — the validator should express the rule, or the route constraint should.

## 11. Error Handling

Errors propagate as exceptions. All application errors extend an abstract `AppException` in `SharedKernel`:

```csharp
public abstract class AppException : Exception
{
    public abstract string Code { get; }
    public abstract int StatusCode { get; }
}

public sealed class WidgetNotFoundException : AppException
{
    public override string Code => "WIDGET_NOT_FOUND";
    public override int StatusCode => 404;
}
```

A global `ErrorHandlerMiddleware` catches `AppException` subtypes and serializes:

```json
{ "error": { "code": "WIDGET_NOT_FOUND", "message": "Widget abc not found" } }
```

Rules:

- Never catch `AppException` subtypes in endpoint handlers or services. Let them propagate.
- Never return inline error envelopes (`return TypedResults.BadRequest(new { ... })`). The middleware owns the envelope.
- Never throw raw `Exception` — always a specific `AppException` subtype, so the code is preserved.
- `Result<T>` is not used. Exceptions plus middleware is the chosen pattern; a mixed style creates two ways to do the same thing.

## 12. Dependency Injection

### 12.1 Composition chain

Registration flows slice → module → host. Each layer aggregates the one below.

```csharp
// Slice (internal to the module)
internal static class WidgetsFeatureExtensions
{
    public static IServiceCollection AddWidgetsFeature(this IServiceCollection services)
        => services
            .AddScoped<IWidgetReadRepository, WidgetRepository>()
            .AddScoped<IWidgetWriteRepository, WidgetRepository>()
            .AddScoped<IWidgetService, WidgetService>()
            .AddScoped<IWidgetQueryService, WidgetQueryService>()      // contract implementation
            .AddValidatorsFromAssemblyContaining<CreateWidgetRequestValidator>();
}

// Module (public surface)
public static class ModuleBExtensions
{
    public static IServiceCollection AddModuleB(this IServiceCollection services)
        => services
            .AddWidgetsFeature()
            .AddGadgetsFeature()
            .AddCategoriesFeature();
}

// Host
builder.Services.AddModuleB();
```

### 12.2 Service lifetimes

| Lifetime      | Use for                                              | Notes                                                  |
|---------------|------------------------------------------------------|--------------------------------------------------------|
| Transient     | Stateless helpers, factories, validators             | Cheap to construct                                     |
| Scoped        | Per-request/invocation state; repositories; services | One instance per HTTP request or worker invocation     |
| Singleton     | App-lifetime state; caches; config; loggers          | **Must be thread-safe.** No scoped dependencies.       |

Never inject scoped services into singletons (captive dependency). Prefer constructor injection; `IServiceProvider.GetService<T>()` in business code is a smell — usually it means a factory or a different lifetime is needed.

## 13. Configuration

All configuration flows through strongly-typed `IOptions<T>`:

```csharp
public sealed class StorageOptions
{
    public string BucketName { get; init; } = string.Empty;
    public int MaxItemsPerContainer { get; init; } = 10_000;
}

builder.Services
    .AddOptions<StorageOptions>()
    .Bind(builder.Configuration.GetSection("Storage"))
    .ValidateDataAnnotations()
    .ValidateOnStart();
```

Rules:

- Group settings by concern. One options class per coherent group; not one giant `AppSettings`.
- `ValidateOnStart()` always. Fail fast at boot, not lazily on first use.
- `IOptions<T>` for read-only; `IOptionsMonitor<T>` only when reloading matters.
- Services never touch `IConfiguration` directly.

## 14. Testing

Three test projects, each with a distinct purpose.

### 14.1 Unit tests

Fast, deterministic, per-slice. Test services and validators in isolation with mocked collaborators. Mirrors the module/feature folder structure. No I/O, no database, no HTTP.

### 14.2 Contract tests

Verify each module's published contracts (`*.Contracts` project) against its implementation. Catches accidental contract drift — a service method signature change that wasn't reflected in the interface, or a DTO field renamed without coordinating consumers. Run on every PR.

### 14.3 Integration tests

End-to-end through real infrastructure: database via Testcontainers, HTTP via `WebApplicationFactory`. Covers cross-module flows, middleware, authentication. Slower; run on PR and main.

## 15. Enforcement

Rules that the compiler can't express are enforced with architecture tests (NetArchTest or ArchUnitNET) in `Tests.Unit/Architecture/`. These run on every PR and fail the build on violation.

Required checks:

1. No feature module's `.csproj` references another feature module's main project (only `*.Contracts` allowed).
2. No feature module has `InternalsVisibleTo` for another feature module.
3. No code in `Features/` of module A `using`s `Features/` of module B.
4. No type in a `.Contracts` project references `Platform` or any other `.Contracts` project.
5. No endpoint handler contains manual validation (heuristic: no `TypedResults.BadRequest(new {...})` calls or manual null/range checks inside handler bodies).
6. No repository is called from an endpoint handler (only services).
7. Entities are never referenced from outside their owning module.

CI fails loudly on any violation. Fixing by adding an exception is not allowed; either the code changes, or the rule does — via a documented PR updating this file.

## 16. Banned Practices — Quick Reference

| Banned                                                             | Use instead                                                        |
|--------------------------------------------------------------------|--------------------------------------------------------------------|
| Horizontal layer folders (Controllers/, Services/, Models/)        | Vertical feature slices (§5)                                       |
| Endpoint handlers / entities / repositories in a host project      | They live in a feature module slice                                |
| Feature module → feature module `.csproj` reference                | Reference the `.Contracts` project instead (§7.1)                  |
| Consumer-owned cross-module interfaces                             | Provider-owned contracts in `Owner.Contracts`                      |
| `InternalsVisibleTo` between feature modules                       | Promote to a contract if the type is needed across modules         |
| A module's entity exposed outside the module                       | A DTO in the module's `.Contracts`                                 |
| Two modules owning the same concept                                | One owner; the other queries through the owner's contract          |
| Single `IRepository` with both read and write methods              | Split `IXReadRepository` + `IXWriteRepository` (§6)                |
| Manual validation in endpoint handlers                             | Validators + global `ValidationFilter` endpoint filter (§10)       |
| `return TypedResults.BadRequest(new { ... })`                      | Throw a specific `AppException` subtype (§11)                      |
| Catching `AppException` in endpoint handlers or services           | Let it propagate to the error middleware                           |
| `IResult` return type when a specific shape is known               | `TypedResults.Xxx(...)` with a typed return (§6.1)                 |
| Instance classes with constructor-injected services for endpoints  | `internal static` class with `private static` handlers (§9)        |
| Host calling `AddApplicationPart` or per-module `AddXxxControllers`| Module-owned `MapModuleXEndpoints(IEndpointRouteBuilder)` (§9)     |
| Cross-module transaction                                           | Module-local transaction plus domain event (§7.2, §7.3)            |
| Services reading `IConfiguration` directly                         | Bind to a typed options class, inject `IOptions<T>` (§13)          |
| Scoped services captured by singletons                             | Match lifetimes or inject a factory                                |
| `IServiceProvider.GetService<T>()` in business code                | Constructor injection                                              |
| Editing `.csproj` / `Directory.Packages.props` XML by hand         | `dotnet` CLI                                                       |
| Slice subfolders before the slice has earned them (~10–15 files)   | Stay flat (§5.1)                                                   |
| Premature promotion to `SharedKernel` 