# Lights Out

Lights Out is a desktop season manager for Assetto Corsa. It turns a data-driven race-series definition and the user's installed cars, tracks, mods, and DLC into a complete, resumable championship.

Assetto Corsa remains the driving simulator. Lights Out acts as the championship authority: it validates the series, prepares each event, launches the simulator, imports the result, calculates standings, and carries the season into the next round.

## Product flow

```text
Import series definition
        |
        v
Validate rules and installed content
        |
        v
Create a season and prepare its next event
        |
        v
Launch Assetto Corsa and drive the session
        |
        v
Review result, update standings, continue season
```

A series definition describes racing concepts rather than machine-specific paths. It can define:

- an ordered calendar of circuits and layouts;
- drivers, teams, cars, liveries, and AI attributes;
- practice, qualifying, and race sessions;
- grid formation and event-specific overrides; and
- points, bonuses, dropped scores, and tie-breakers.

“Any race series” means the format is data-driven and extensible. Unsupported regulations will be reported explicitly rather than silently approximated.

## Current status

Lights Out is in the product-definition and architecture phase. The product specification, application boundaries, first vertical-slice plan, and fictional four-round MX-5 Sprint Cup reference fixture are established. The desktop technology stack and exact Assetto Corsa compatibility contract are the next decisions.

The first vertical slice will run the [Lights Out MX-5 Sprint Cup](tests/fixtures/reference-series/README.md) from definition import through a launched race, accepted result, and updated standings. Broader rule and installation support will be added from verified examples after that complete path works.

## Architecture

Lights Out is designed as a local-first Windows desktop application with no required account or network service.

- A platform-independent season domain owns lifecycle, sporting rules, classification, points, and standings.
- Application services coordinate imports, season creation, event preparation, result acceptance, and recovery.
- Typed adapters isolate Assetto Corsa content discovery, launch configuration, process control, and result parsing.
- SQLite stores durable season state, audit history, and references to preserved raw result evidence.
- Simulator content remains externally owned; Lights Out does not modify car, track, skin, or mod source files.

See [ARCHITECTURE.md](ARCHITECTURE.md) and the [local-first architecture decision](docs/design-docs/0001-local-first-season-architecture.md) for the complete design.

## Project documentation

Repository documentation is the source of truth:

| Document | Purpose |
| --- | --- |
| [Product overview](docs/PRODUCT.md) | Users, intended outcome, principles, non-goals, and success measures |
| [Season simulation spec](docs/product-specs/season-simulation.md) | User journeys, requirements, lifecycle, and acceptance criteria |
| [Architecture](ARCHITECTURE.md) | System context, dependency direction, and boundary rules |
| [Architecture decision](docs/design-docs/0001-local-first-season-architecture.md) | Persistence, integration, recovery, trust boundaries, and tradeoffs |
| [Active implementation plan](docs/exec-plans/active/2026-07-21-season-vertical-slice.md) | Milestones, risks, decisions, and verification for the first playable slice |
| [Documentation index](docs/README.md) | Quality, reliability, security, design, and engineering guidance |

## Development

The application stack has not yet been selected, so setup, start, and application-test commands are intentionally pending. Stack selection must demonstrate Windows packaging, accessible desktop UI, SQLite migrations, typed JSON validation, safe process launch, and enforceable dependency boundaries before the repository is structured around it.

The repository knowledge harness currently requires Python 3 and can be verified with:

```powershell
python tools/harness_check.py
python -m unittest discover -s tests
```

Before making structural or implementation changes, read [AGENTS.md](AGENTS.md), [ARCHITECTURE.md](ARCHITECTURE.md), and the [active execution plan](docs/exec-plans/active/2026-07-21-season-vertical-slice.md). Keep changes narrow, preserve unrelated work, and update the relevant specification or decision record when behavior or architecture changes.

## Initial non-goals

- Downloading or redistributing mods and DLC
- Replacing Assetto Corsa's physics, AI, graphics, or in-session interface
- Multiplayer league administration or live race control
- Supporting Assetto Corsa Competizione or other simulators
- Claiming support for regulations that are not represented in the versioned series format

See the [season simulation spec](docs/product-specs/season-simulation.md#outcome-and-non-goals) for the authoritative scope.
