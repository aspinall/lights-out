# Plan: playable season vertical slice

Status: Active  
Owner: Engineering  
Created: 2026-07-21  
Updated: 2026-07-21

## Outcome

Deliver a packaged Windows desktop vertical slice in which a sim-racing fan can import one representative series, validate a fixture or supported Assetto Corsa installation, create and resume a season, launch its next race, accept the resulting classification, and see correct championship standings.

The slice establishes the extensible path to “any race series” without pretending the first version supports every sporting rule or simulator variant.

## Context

- [Season simulation product spec](../../product-specs/season-simulation.md)
- [Local-first architecture decision](../../design-docs/0001-local-first-season-architecture.md)
- [Top-level architecture](../../../ARCHITECTURE.md)
- [Product principles](../../PRODUCT.md)
- [Design principles](../../DESIGN.md)
- [Security baseline](../../SECURITY.md)

The desktop stack is selected in [Design 0003](../../design-docs/0003-desktop-technology-stack.md): C#/.NET 10, WinUI 3, EF Core/SQLite, and Corvus JSON Schema tooling. A pinned repo-local SDK and isolated caches avoid machine-wide development dependencies. The canonical start and application-test commands remain template placeholders until the walking-skeleton proof makes them executable.

## Acceptance criteria

- [ ] A clean checkout has documented, executable setup, start, test, and verify commands.
- [ ] A packaged Windows build completes the import-to-standings journey for the chosen reference series.
- [ ] The versioned JSON Schema and examples distinguish malformed, unsupported, and valid definitions.
- [ ] The season domain and standings engine run deterministically without Assetto Corsa or filesystem access.
- [ ] A fixture installation can be scanned and required content classified without mutation.
- [ ] The supported real installation profile produces a reviewable launch plan and can launch one race.
- [ ] A correlated result is retained, normalized, accepted idempotently, and reflected in standings.
- [ ] Restarting at every persisted lifecycle state offers the correct next or recovery action.
- [ ] Focused tests and the canonical repository verification command pass.
- [ ] Supported Windows and vanilla Assetto Corsa variants plus known limitations are documented; the slice does not require Content Manager.

## Steps

- [ ] Complete the reference fixture set: the MX-5 Sprint Cup definition, normalized results, and expected standings are checked in; installation and launch-plan fixtures remain after the Assetto Corsa contract research.
- [ ] Complete the vanilla Assetto Corsa compatibility spike: read-only installation, configuration, launcher, and output discovery plus golden fixtures are complete; controlled direct launch, real race-result capture, restoration proof, and clean-install repetition remain.
- [ ] Prove the selected desktop stack across Windows packaging, accessible UI, SQLite migrations, typed JSON validation, process launch, and structural dependency checks; the design selection is complete but its implementation gate remains open.
- [ ] Replace all placeholder canonical commands in `harness/project.json`, add CI coverage, and enforce dependency direction.
- [ ] Implement the versioned series schema, two-phase validation, normalized definition model, and actionable diagnostics.
- [ ] Implement the pure season domain: lifecycle, entrants, sessions, classification, points, tie-breakers, and deterministic standings replay for the reference rules.
- [ ] Implement SQLite migrations and repositories for definition snapshots, mappings, seasons, launch attempts, raw results, accepted results, audit events, and rebuildable standings.
- [ ] Implement content discovery and mapping against synthetic installation trees, including missing, ambiguous, and changed states.
- [ ] Implement deterministic launch-plan compilation and reversible staging using only application-owned files.
- [ ] Implement typed process launch, attempt correlation, cancellation/failure handling, output discovery, and result parsing.
- [ ] Build the desktop journeys and states for import, mapping, preview, season home, event preparation, launch, result review, recovery, standings, and completion.
- [ ] Add automated domain, contract, repository, adapter, structural, accessibility, and end-to-end journey tests.
- [ ] Exercise the packaged application against the supported real installation, document the compatibility result, and capture release/recovery guidance.

## Progress log

- 2026-07-21: Product spec, system architecture, design decision, and initial vertical-slice plan created.
- 2026-07-21: Identified the empty-stack scaffold and unresolved Assetto Corsa compatibility contract as the first implementation risks.
- 2026-07-21: Replaced the scaffold README with the Lights Out product flow, current status, architecture summary, documentation map, and development entry points.
- 2026-07-21: Selected the fictional four-round Lights Out MX-5 Sprint Cup as the reference series and added its draft v1 definition, normalized results, deterministic expected standings, and fixture integrity tests.
- 2026-07-21: Selected vanilla Assetto Corsa on Windows as the first simulator compatibility target; Content Manager support is deferred to a separate future adapter.
- 2026-07-21: Inspected the observed Steam installation and vanilla launcher read-only; recorded build evidence, exact reference content/layout/skin identifiers, `race.ini` structure, fixed output locations, and the launcher's internal `ac://start` to `acs.exe` lifecycle.
- 2026-07-21: Added sanitized vanilla installation, launch-plan, materialized INI, and observed output fixtures with automated mapping and contract tests. Direct external launch remains explicitly unverified pending a controlled interactive run.
- 2026-07-21: Controlled launch attempt showed that plain `acs.exe` invocation is redirected by Steam to the vanilla launcher, which rewrites `race.ini`; no result was produced, and the exact original configuration was restored by verified hash. A Steam-app-environment retry stopped safely at preflight because redirected launcher processes remained active.
- 2026-07-21: After closing redirected launcher processes, the retry with child-only `SteamAppId` and `SteamGameId` set to `244210` launched `acs.exe` directly, consumed the staged qualifying/race config, produced a new result, and restored the exact original config. The zero-lap classification is retained as a rejection fixture.
- 2026-07-21: Selected C#/.NET 10 LTS, WinUI 3 on Windows App SDK 2.2, EF Core/SQLite, Corvus JSON Schema tooling, xUnit, and Appium/UI Automation. The machine has no .NET SDK, so installation and a disposable packaging/accessibility/integration proof are the next gate.
- 2026-07-21: Added an idempotent, non-admin repo-local environment pinned to .NET SDK 10.0.302. SDK files, CLI state, NuGet packages/cache, and temporary build files live under ignored `.tools/`; no persistent `PATH` or registry changes are made.

## Decision log

- 2026-07-21: Use a local-first single desktop deployment with internal ports rather than networked services; this matches the offline single-user outcome while preserving replaceable integrations.
- 2026-07-21: Use versioned JSON plus JSON Schema for portable definitions and SQLite for mutable seasons; interchange and transactional state have different requirements.
- 2026-07-21: Make one reference series the walking skeleton; breadth of rules follows only after import-to-standings works at the real desktop boundary.
- 2026-07-21: Keep exact Assetto Corsa configuration and result details out of the domain until verified against an explicit compatibility target.
- 2026-07-21: Use the official Mazda MX-5 Cup and four compact official circuits for the reference series; keep content references logical until verified installation identifiers are captured by the simulator-adapter research.
- 2026-07-21: Target vanilla Assetto Corsa before third-party launchers so the first integration contract depends only on the simulator and official Steam installation.
- 2026-07-21: Stage only user-data `cfg/race.ini`, preserve and hash its exact previous bytes, restore conservatively after process/result handling, and never mutate Steam-owned configuration or content.
- 2026-07-21: Treat direct `acs.exe` launch as the candidate external handoff, not an established contract, because the installed vanilla launcher exposes only a private embedded `ac://start` handler.
- 2026-07-21: Reject plain direct `acs.exe` invocation after observed Steam redirection. Test a child-only `SteamAppId`/`SteamGameId=244210` context next; do not create `steam_appid.txt` or otherwise modify the Steam installation.
- 2026-07-21: Adopt child-only `SteamAppId`/`SteamGameId=244210` plus direct 64-bit `acs.exe` as the verified vanilla handoff for the observed profile. Never accept a race result solely because `raceResult` is present; require evidence of completed laps and configured completion rules.
- 2026-07-21: Build the Windows-only client with C#/.NET 10 and WinUI 3; isolate UI, persistence, and Assetto Corsa behind ordinary .NET project boundaries so WPF can replace only the desktop shell if the proof fails.
- 2026-07-21: Use Corvus rather than JsonSchema.Net for JSON Schema 2020-12 validation because Corvus is Apache-2.0 and generates typed C#, while JsonSchema.Net's current binary EULA can impose a revenue-related maintenance fee.
- 2026-07-21: Use a repo-local Windows toolchain rather than a devcontainer because the primary proof requires an interactive WinUI desktop, MSIX identity, UI Automation, Steam, and Assetto Corsa. Reserve containers for optional non-UI CI work.

## Risks and recovery

- **Unstable simulator contract:** launcher or result differences may block automation. Mitigate with a narrow compatibility matrix, fixture capture, capability-based adapters, and deliberate manual result import. Do not guess undocumented formats.
- **Rule-model explosion:** “any series” can create unbounded scope. Add explicit versioned rule kinds driven by reference fixtures; reject unsupported rules clearly.
- **User-content damage:** configuration staging could overwrite externally owned files. Default to application-owned locations, record every staged artifact, use atomic writes and backups where an external location is unavoidable, and test cleanup/restore.
- **Interrupted external process:** the desktop app may exit while Assetto Corsa runs. Record the attempt before launch and recover through correlated output discovery without auto-advancing.
- **Schema or database evolution:** changes may strand saved seasons. Snapshot definitions, use migrations and pre-upgrade backups, and build replay/restore fixtures before user-data releases.
- **Stack mismatch:** a framework may package well but make process integration or accessibility poor. Require a disposable proof before committing the repository structure.

Human judgment is required to approve the researched vanilla Assetto Corsa compatibility matrix and decide which additional sporting rules enter definition format version 1.

## Verification

Documentation baseline:

```text
python tools/harness_check.py
python -m unittest discover -s tests
```

Implementation verification commands will replace the placeholders in `harness/project.json` after stack selection. Record exact results here at each milestone. The final behavioral exercise uses a clean Windows user profile and proceeds from definition import through a launched fixture/real session, result acceptance, application restart, standings display, and season continuation.

Baseline result on 2026-07-21 using the Codex workspace Python runtime:

- `tools/harness_check.py`: 0 errors, 1 expected warning for placeholder setup/start/test commands pending stack selection.
- `python -m unittest discover -s tests`: 18 tests passed.
- `git diff --check`: passed; Git reported only the repository's expected LF-to-CRLF checkout notices.

## Outcome notes

Not yet shipped. Move this plan to `completed/` only after the packaged vertical slice and compatibility exercise satisfy all acceptance criteria. Record deferred rule kinds and simulator variants in `docs/exec-plans/tech-debt.md` with concrete triggers.
