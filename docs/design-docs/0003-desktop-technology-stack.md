# Design: Windows desktop technology stack

Status: Accepted  
Owner: Engineering  
Last verified: 2026-07-21

## Context

Lights Out needs a concrete stack for a local-first Windows desktop application that owns season state, validates portable JSON definitions, controls a native simulator process, and exposes an accessible user interface. The first release targets vanilla Assetto Corsa on Windows only. Cross-platform UI and a hosted service are not product requirements.

The stack must support the dependency boundaries in `ARCHITECTURE.md`, SQLite migrations, deterministic non-UI tests, JSON Schema 2020-12, Windows process and filesystem APIs, UI Automation, and an installable Windows build. The repository currently has no .NET SDK, application scaffold, or canonical application commands.

## Decision

Use the following stack for the first playable slice:

| Concern | Choice |
| --- | --- |
| Language and runtime | C# with .NET 10 LTS; nullable reference types and warnings as errors |
| Desktop UI | WinUI 3 on the current stable Windows App SDK 2.2 line, using XAML |
| UI pattern | MVVM with `CommunityToolkit.Mvvm`; code-behind is limited to view-only behavior |
| Composition and logging | `Microsoft.Extensions.DependencyInjection` and `Microsoft.Extensions.Logging` at the composition root |
| Persistence | EF Core 10 with the SQLite provider and checked-in migrations |
| JSON | `System.Text.Json` plus Corvus JSON Schema source generation and validation for draft 2020-12 |
| Unit and integration tests | xUnit for non-UI code; isolated temporary databases and fixture files |
| UI and accessibility tests | Windows UI Automation through Appium's Windows driver, plus Accessibility Insights checks |
| Distribution | Unpackaged self-contained `win-x64` builds for development; signed self-contained MSIX for release |

Use Central Package Management and package lock files. Pin the .NET SDK in `global.json` and pin exact package patches centrally when the scaffold is created; take security and servicing patches deliberately without changing the selected major release lines.

Corvus-generated transport types validate the input shape at the import boundary. They are mapped immediately into hand-written domain types, so generated code and JSON-library types do not leak into sporting rules. EF entities are likewise persistence shapes and do not become domain entities.

The solution structure will be:

```text
src/
  LightsOut.Domain/          no project dependencies
  LightsOut.Application/     -> Domain; owns use cases and ports
  LightsOut.Infrastructure/  -> Application, Domain; SQLite and local storage
  LightsOut.AssettoCorsa/    -> Application, Domain; simulator adapter
  LightsOut.Desktop/         -> Application and concrete adapters; composition root
tests/
  LightsOut.Domain.Tests/
  LightsOut.Application.Tests/
  LightsOut.Infrastructure.Tests/
  LightsOut.AssettoCorsa.Tests/
  LightsOut.Architecture.Tests/
  LightsOut.Desktop.UiTests/
```

The desktop project is the only project allowed to reference WinUI. EF Core is confined to Infrastructure, Assetto Corsa formats and process details are confined to the simulator adapter, and Domain references no platform, persistence, UI, or JSON packages. Architecture tests will enforce these reference rules.

## Alternatives considered

- **WPF:** mature, stable, and simpler in some tooling paths, but WinUI 3 is Microsoft's recommended framework for new native Windows apps. WPF remains the fallback if the packaging and UI proof exposes a blocking WinUI defect.
- **Avalonia:** credible C# cross-platform UI with Windows accessibility support. Cross-platform delivery is not in scope, so its abstraction and custom rendering stack provide no current product benefit.
- **Tauri with TypeScript and Rust:** capable and compact, but introduces two application languages, WebView2, and a command bridge around process-heavy native integration. That is unnecessary complexity for a Windows-only product.
- **Electron:** productive web UI tooling but a larger runtime footprint and the same web/native boundary without a cross-platform requirement.
- **.NET MAUI:** optimized for shared mobile and desktop applications; Lights Out is a keyboard-and-mouse Windows desktop tool with no mobile target.
- **Raw SQLite or Dapper:** offer tighter SQL control, but EF Core migrations and change tracking reduce infrastructure work for the transactional season model. Repositories keep replacement possible if profiling later shows a real issue.
- **JsonSchema.Net:** technically suitable, but its current binary EULA may require paid maintenance for revenue-generating users. The Apache-2.0 Corvus toolchain avoids that product constraint and provides typed source generation.

## Consequences and risks

- The team needs the .NET 10 SDK and WinUI workload; the current machine has only older runtimes and no SDK.
- WinUI types require a XAML application/UI thread, so UI logic must remain thin. Most behavior belongs in ordinary .NET libraries that `dotnet test` can run without a graphical session.
- WinUI and Windows App SDK servicing moves faster than .NET LTS. Central version pins and a packaged smoke test make upgrades explicit.
- MSIX identity, signing, app-data locations, and full-trust process launch add release work. The proof must launch the verified Assetto Corsa handoff from an installed package, not only from Visual Studio.
- Corvus source generation couples the build to a third-party generator. Generated types stay behind an application-owned import adapter, and golden schema diagnostics cover replacement.
- The first release is `win-x64`. ARM64 and cross-platform support require separate compatibility evidence and are not implied by the framework choice.

## Verification

Before broad feature implementation, a disposable walking-skeleton proof must demonstrate:

1. a clean .NET 10 setup can restore, build, test, run, and publish from the canonical commands;
2. an unpackaged debug build and installed signed/test-signed MSIX start successfully;
3. keyboard navigation, scaling, high contrast, screen-reader names, and the UI Automation tree work for a representative import screen;
4. a JSON Schema 2020-12 fixture produces a generated type and useful path-based diagnostics for invalid input;
5. EF Core creates and migrates a SQLite database, then survives an application restart;
6. an application service can launch a harmless child process, capture its exit state, and cancel safely;
7. the installed desktop package can execute the verified Assetto Corsa launch-plan boundary without broad filesystem capabilities; and
8. architecture tests reject forbidden project and namespace dependencies.

The proof updates `harness/project.json` only after all canonical commands are executable. Full Assetto Corsa launch remains an explicit interactive compatibility exercise.

## Rollout and rollback

Install the .NET 10 SDK, create the solution and project boundaries, add the proof tests, then replace the harness placeholders. Add domain features only after the proof passes.

If WinUI or MSIX cannot satisfy process launch, accessibility, or clean-machine packaging, stop before product UI work and replace only `LightsOut.Desktop` with WPF on .NET 10. The domain, application, infrastructure, simulator adapter, schemas, and databases remain unchanged. A runtime or database-stack reversal after persisted user data ships requires a superseding design record and migration plan.
