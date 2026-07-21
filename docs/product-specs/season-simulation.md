# Product spec: season simulation

Status: Draft  
Owner: Product  
Last verified: 2026-07-21

## Problem

Assetto Corsa can simulate individual driving sessions, but creating a championship that resembles a chosen race series requires repeated manual configuration outside the race: selecting compatible cars and tracks, rebuilding grids and session settings, tracking results, calculating points, and carrying sporting state into later rounds. Mod-dependent seasons add another failure mode because missing or mismatched content is often discovered only when an event is launched.

Sim-racing fans need a season authority that makes this work repeatable and recoverable while leaving the actual driving simulation to Assetto Corsa.

## Outcome and non-goals

A user can import a data-driven race-series definition, map it to locally installed Assetto Corsa content, create a season, and play it event by event. Lights Out owns the calendar, entrants, sporting rules, results, and standings. Before each event it produces a validated Assetto Corsa launch configuration; afterwards it ingests a result and advances the season.

“Any race series” means the season format is data-driven and extensible. It does not mean the first release implements every regulation ever used. A definition that uses an unsupported rule must fail validation with a precise explanation instead of being silently approximated.

The first release does not:

- acquire, redistribute, or modify cars, tracks, mods, or DLC;
- replace Assetto Corsa's physics, AI, graphics, or in-session behavior;
- administer multiplayer leagues or synchronize seasons between computers;
- support Assetto Corsa Competizione or another simulator;
- scrape proprietary championship data from the web; or
- infer a trustworthy result when the simulator output is absent or ambiguous.

## Domain language

- **Series definition:** portable, versioned input describing a championship format in racing terms.
- **Content mapping:** user-approved association from definition car, skin, and circuit references to a local Assetto Corsa installation.
- **Season:** an instantiated, mutable play-through of a series definition.
- **Event:** one calendar round containing one or more ordered sessions.
- **Launch plan:** the validated, reproducible simulator-specific configuration for one session.
- **Result:** immutable raw evidence from a completed session plus its normalized domain representation.
- **Standings:** derived driver and, when configured, team totals based on accepted results.

## Series definition

The initial interchange format is versioned JSON validated against a published JSON Schema. It contains stable identifiers and display names rather than local file paths. At minimum it can describe:

- series metadata and format version;
- an ordered calendar of circuits and layouts;
- drivers, teams, car models, skins, and AI attributes;
- practice, qualifying, and race sessions with durations or lap counts;
- grid formation rules supported by the current format;
- a points table, fastest-lap or pole bonuses, eligibility conditions, dropped scores, and deterministic tie-breakers; and
- optional per-event overrides such as entrants, sessions, or conditions.

Unknown format versions, unknown rule kinds, duplicate identifiers, impossible references, and internally inconsistent settings are validation errors. Additive unknown metadata may be preserved but has no sporting effect.

## Season lifecycle

A season moves through explicit states:

```text
draft -> ready -> event prepared -> session launched -> result pending
  ^        |             |                  |                |
  |        +-------------+------------------+----------------+
  |                  recover or retry
  +---------------- configuration repaired

accepted result -> standings updated -> next event ready -> completed
```

The application persists each transition. Closing or crashing the application must not silently advance a season or discard an accepted result.

## User journeys

### Create a season

1. The user selects a series definition.
2. Lights Out validates its syntax, schema version, references, and supported rules.
3. Lights Out scans a user-selected Assetto Corsa installation and proposes content mappings.
4. The user resolves missing or ambiguous mappings and sees why an item is required.
5. Lights Out shows the calendar, entrants, sessions, and rules that will govern the season.
6. The user creates the season. The definition and approved mappings are snapshotted so later source-file edits do not silently alter it.

### Prepare and run an event

1. The home screen shows the current standings and the next valid action.
2. Lights Out revalidates content needed for the next session and shows any blocking changes.
3. The user reviews the entrants, grid, session settings, and conditions.
4. Lights Out writes a reversible launch plan without modifying installed source content.
5. The user launches Assetto Corsa from Lights Out.
6. Lights Out records the launch outcome and waits for a result; a failed or cancelled launch leaves the session retryable.

### Accept a result

1. Lights Out discovers simulator output associated with the launch and preserves the raw artifact.
2. It normalizes and validates classification, entrant identity, laps, status, and relevant bonuses.
3. The user reviews warnings or resolves an ambiguous result before it affects the championship.
4. On acceptance, Lights Out stores the result immutably, recalculates standings deterministically, and exposes the next session or event.
5. If automatic import is unavailable, the user may import a supported result artifact manually; arbitrary manual classification editing is deferred until its audit requirements are designed.

### Resume and recover

On restart, Lights Out returns to the last persisted state. It identifies an interrupted staging or launch attempt, explains what is known, and offers safe retry or result-import actions. Reprocessing the same result must not award points twice.

## Functional requirements

- Multiple seasons can coexist and progress independently.
- A season is playable offline after its simulator content is installed.
- Validation distinguishes definition errors, unsupported features, missing content, ambiguous mappings, and changed content.
- A launch plan includes enough provenance to reproduce which definition, mappings, entrants, and settings were used.
- The standings engine is independent of Assetto Corsa and produces the same result from the same ordered accepted results.
- Result acceptance is idempotent and auditable; raw evidence is retained alongside the normalized result.
- Destructive actions, including deleting a season or replacing an accepted result, require explicit confirmation and a documented recovery policy.
- User-facing flows cover loading, empty, invalid, partially mapped, ready, launched, result-pending, recoverable-error, and completed states.
- Keyboard operation, focus order, labels, contrast, and status communication target WCAG 2.2 AA.

## Acceptance criteria

- [ ] A valid sample series definition can be imported and previewed without Assetto Corsa installed.
- [ ] Invalid references and unsupported rules are rejected with the exact definition location and an actionable message.
- [ ] Given a fixture installation, Lights Out reports required content as present, missing, ambiguous, or changed without altering it.
- [ ] A fully mapped series can create a season whose snapshotted calendar, entrants, sessions, and rules survive restart.
- [ ] Preparing a session creates a deterministic launch plan and never edits car, track, skin, or mod source files.
- [ ] A cancelled or failed simulator launch can be retried without advancing the championship.
- [ ] A valid result fixture can be associated with its launch, accepted once, and used to calculate the expected standings.
- [ ] Importing the same result twice does not duplicate points or advance the season twice.
- [ ] An ambiguous or malformed result cannot affect standings until the user resolves or replaces it.
- [ ] Completing the final configured session marks the season complete and preserves its full history.
- [ ] The critical create, prepare, launch, accept, resume, and complete journeys are exercised through the desktop boundary at the highest practical test level.

## Measurement

The initial product uses local structured events for import, validation, staging, launch, result, recovery, and completion transitions. Diagnostic export is user-initiated and must redact local usernames, arbitrary paths, and content names unless the user explicitly includes them. The measures and decision owners are defined in [the product overview](../PRODUCT.md#success-measures).

## Open questions

- Which Windows and Assetto Corsa installations and launchers define the first supported compatibility matrix? Owner: Engineering.
- Which real-world series should be the reference fixture for the first vertical slice? Owner: Product.
- Which session output provides the most stable automatic result contract, and what manual import formats are viable? Owner: Engineering.
- Which grid, weather, pit-stop, penalty, ballast, and multi-race rules belong in format version 1? Owner: Product.
- What backup, export, and accepted-result correction workflow provides an adequate audit trail? Owner: Product and Engineering.
