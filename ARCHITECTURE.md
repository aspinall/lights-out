# Architecture

## System context

Lights Out is a local-first Windows desktop season manager for sim-racing fans. Users import a data-driven race-series definition, map its requirements to an existing Assetto Corsa installation, run each event in the simulator, and return to Lights Out for results and championship progression.

```text
series JSON ----> Lights Out desktop app ----> application-owned SQLite and artifacts
                         |       ^
                         v       |
             Assetto Corsa installation
             content, process, and results
```

The desktop application is initially the only deployment unit and requires no online account or service. Series definitions, simulator outputs, mods, DLC, and the Assetto Corsa installation are external and untrusted or externally owned. Lights Out owns its database, application storage, staged launch artifacts, and audit history; it does not own or modify source game content.

The detailed decision, recovery model, and rejected alternatives are recorded in [Design 0001](docs/design-docs/0001-local-first-season-architecture.md).

## Dependency model

The default domain layering is:

```text
types -> config -> repository -> service -> runtime -> interface
                         ^
providers ---------------+
```

- Dependencies move from left to right only.
- `types` has no domain-internal dependencies.
- `repository` owns persistence; `service` owns business rules.
- `runtime` coordinates processes, jobs, and lifecycle.
- `interface` translates HTTP, CLI, UI, or event boundaries.
- Cross-cutting capabilities enter through explicit `providers` interfaces.
- Shared utilities remain small, domain-neutral, and free of business policy.

Adapt the names to the chosen stack in a design record, but retain explicit, mechanically enforceable dependency directions.

For Lights Out, the planned mapping is:

```text
domain types -> definition/config -> repository ports -> application services -> runtime -> desktop UI
                                               ^                 |
                                               |                 v
                                  persistence adapter    simulator/content ports
                                                                    ^
                                                                    |
                                                        Assetto Corsa adapters
```

- The season domain owns lifecycle and sporting rules and has no platform dependencies.
- Application services own use cases and transaction boundaries.
- The runtime coordinates staging, external processes, result discovery, and recovery.
- Assetto Corsa and persistence details enter through typed ports and boundary adapters.
- Only the composition root selects concrete adapters.

## Boundary rules

- Validate untrusted data once at every external boundary.
- Convert transport and persistence shapes into domain types before applying business logic.
- Make time, randomness, network access, and storage replaceable at test boundaries.
- Emit structured events at important state transitions.
- Keep secrets out of source, logs, fixtures, and error messages.
- Treat series and result files as untrusted, versioned inputs with explicit size and shape limits.
- Never infer a completed race from process exit alone; accept only a validated, correlated result.
- Never write into car, track, skin, or mod source directories.
- Make prepare, launch recording, result acceptance, and standings rebuild idempotent.

## Architectural changes

Any change to deployment units, trust boundaries, public contracts, persistence ownership, or dependency direction requires a design record in `docs/design-docs/`. Add a structural test or lint when the rule can be checked mechanically.

