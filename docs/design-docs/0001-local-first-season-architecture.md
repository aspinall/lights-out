# Design: local-first season and simulator architecture

Status: Proposed  
Owner: Engineering  
Last verified: 2026-07-21

## Context

Lights Out must manage durable championship state while invoking a separately installed Windows game whose content, configuration, launcher, and result behavior are outside our control. Series definitions may come from untrusted authors. Mods may be missing, renamed, or malformed. A crash can occur between staging a session, launching the simulator, and accepting a result.

The architecture must keep sporting rules testable without Assetto Corsa, protect user content, make incomplete operations recoverable, and allow simulator integration details to evolve without contaminating the season model.

## Decision

Lights Out will be a local-first Windows desktop application. It is one deployable application with a local database and explicit internal boundaries; it is not initially split into local services.

The first simulator adapter targets vanilla Assetto Corsa without Content Manager. Third-party launchers may be added later through separate adapters and must not change the season domain contract.

### Components and dependency direction

```text
Desktop UI -> application services -> season domain <- repository ports
                         |                 ^
                         v                 |
                  runtime coordinator     |
                         |                 |
                         v                 |
               simulator/content ports ---+
                         ^
                         |
               Assetto Corsa adapters

JSON file -> definition adapter -> validated domain definition
SQLite    <- persistence adapter <- repository ports
```

- **Season domain** owns definitions, identifiers, lifecycle transitions, supported sporting rules, classification, points, and standings. It has no UI, filesystem, process, database, clock, or Assetto Corsa dependency.
- **Application services** implement use cases and transaction boundaries such as import definition, create season, prepare session, record launch, accept result, and recover interrupted work.
- **Runtime coordinator** sequences long-running staging, process launch, output discovery, and recovery. It reports explicit progress and cancellation states.
- **Ports** define typed contracts for persistence, filesystem inspection, clock, process launch, content discovery, launch staging, and result discovery.
- **Adapters** validate external shapes and convert them into domain types. Assetto Corsa-specific paths, identifiers, configuration formats, and result formats exist only here.
- **Desktop UI** renders application view models and sends commands. It does not calculate points, inspect game directories, or write launch files directly.

Dependencies point inward toward domain policy. Provider implementations are selected only at the application composition root. Structural tests will enforce forbidden imports once a language and framework are selected.

### Durable data ownership

SQLite is the system of record for mutable application state because seasons require transactions, uniqueness constraints, migration support, and robust local recovery. The repository stores:

- original definition bytes, format version, content hash, and normalized snapshot;
- approved content mappings and the installation profile they were validated against;
- season, event, session, and lifecycle state;
- launch plans and attempts with correlation identifiers;
- immutable raw-result metadata and normalized accepted results;
- standings projections that can be rebuilt from accepted results; and
- an append-only domain event/audit record for consequential transitions.

Large raw result artifacts may live in application-managed storage, referenced by hash and relative path from SQLite. Database migrations are forward-only and backed up before upgrade. User-installed simulator content is never owned by the repository.

### Boundary contracts

The versioned series JSON is validated in two phases: JSON Schema validates its external shape, then domain construction validates cross-references and sporting invariants. No application behavior probes arbitrary fields or local paths to guess intent.

The simulator adapter exposes capabilities rather than leaking configuration files:

- inspect an installation and return typed content descriptors;
- compare required logical content with installed content;
- compile a domain session into a launch plan or typed unsupported-setting errors;
- stage and clean up only application-owned files;
- launch a staged plan and return a correlated attempt;
- discover raw output candidates for that attempt; and
- parse a selected candidate into a normalized result or typed diagnostics.

Exact Assetto Corsa file and process contracts must be verified against supported installations before implementation. They are compatibility-adapter details, not domain assumptions.

### State, idempotency, and recovery

Every consequential operation has a stable identifier. Preparing the same unchanged session returns the existing plan. Launch attempts are recorded before invoking the external process. Raw results are hashed, and acceptance has a uniqueness constraint across season session and result identity. Standings are rebuilt within the same transaction that accepts or replaces a result.

Application state never treats process exit alone as proof that a race completed. After an interrupted launch, recovery can rediscover a correlated result, return the session to a retryable state, or wait for user action. Staged writes use an application-owned temporary location and atomic replacement where the integration contract permits it; any backup restoration is recorded.

### Trust boundaries

- Series files and result files are untrusted input with size limits, strict parsing, and no executable content.
- Assetto Corsa and mod directories are externally owned and read-only except for narrowly documented, user-approved integration locations.
- Process arguments are constructed as typed values without shell interpolation.
- The application requires no administrator privileges for its normal operation.
- Logs use structured event names and redact usernames, arbitrary absolute paths, process environment, and definition-supplied free text by default.
- The first release has no required network service or account.

### Observability

Each create, validate, prepare, launch, discover, accept, advance, and recover operation carries a correlation identifier. Local logs capture outcome codes and actionable diagnostics without sensitive content. A user-initiated support bundle can include the schema version, application version, redacted logs, validation report, and selected artifacts after an inclusion preview.

## Alternatives considered

### Encode championship behavior directly in Assetto Corsa configuration

Rejected because simulator configuration is an execution format, not a durable championship model. It cannot safely own portable definitions, rich validation, standings history, or recovery.

### Put filesystem and process calls directly behind UI actions

Rejected because business rules would be coupled to Windows and a particular Assetto Corsa layout, making recovery and fixture-based testing difficult.

### Store seasons as editable JSON only

Rejected for mutable state. Plain files are useful for interchange and export, but cross-entity transactions, idempotent result acceptance, migrations, and crash recovery are safer in SQLite.

### Start with separate background services

Rejected because a single-user offline desktop application does not yet justify deployment and synchronization complexity. The internal port boundaries allow a helper process to be introduced later if process isolation becomes necessary.

### Build around a specific third-party launcher

Rejected as the core architecture. The first slice targets vanilla Assetto Corsa; launcher-specific support such as Content Manager can be an adapter after its contract and user demand are established.

## Consequences and risks

- The domain can be tested on any development platform, but full launch verification requires supported Windows/Assetto Corsa fixtures.
- Snapshotting definitions protects existing seasons but requires an explicit upgrade or clone flow for definition changes.
- SQLite and application-managed artifacts need coordinated backup, migration, and deletion behavior.
- Automatic result correlation may not be reliable across all installation variants. The UI must expose evidence and support a deliberate manual import path rather than guessing.
- Some requested series rules will be rejected until represented explicitly in the versioned rule model.
- A technology stack remains to be selected. The selected stack must preserve these boundaries, support accessible desktop UI, package for Windows, and make SQLite and process integration testable.

## Verification

- Contract tests validate definition and result adapters with valid, malformed, oversized, unknown-version, and inconsistent fixtures.
- Domain tests cover lifecycle transitions, points, tie-breakers, dropped scores, and deterministic replay without filesystem or simulator access.
- Repository tests exercise migrations, transaction rollback, uniqueness, result idempotency, and standings rebuild.
- Simulator adapter tests run against synthetic installation trees and golden launch/result fixtures.
- Structural tests reject forbidden dependencies into the season domain and direct adapter use from the UI.
- Desktop journey tests exercise import, map, create, prepare, failed launch, accepted result, restart recovery, and completion.
- A manual compatibility matrix verifies packaged builds against each supported Assetto Corsa installation and launcher variant.

## Rollout and rollback

Build a walking skeleton around one reference series, one installation profile, one race session, and fixture results before launching the real simulator. Add capabilities and rule kinds only with schema, domain, adapter, and compatibility tests.

During development, schema and database changes may be reset only for disposable fixtures. Before any user-data release, migrations require pre-upgrade backup and tested restore. New series format versions are additive readers where possible; an existing season continues using its snapshotted definition and adapter version. Simulator integration changes are rolled back by selecting the prior adapter behavior and removing only application-owned staged files.
