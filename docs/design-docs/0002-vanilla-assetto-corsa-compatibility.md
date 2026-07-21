# Design: vanilla Assetto Corsa compatibility contract

Status: Proposed  
Owner: Engineering  
Last verified: 2026-07-21

## Context

The first Lights Out vertical slice targets vanilla Assetto Corsa on Windows without Content Manager. The integration must discover official content, materialize a race weekend, launch the 64-bit simulator, preserve the user's existing configuration, and correlate the simulator's fixed result output with a Lights Out launch attempt.

This spike is based on a read-only inspection of an installed Steam copy and its vanilla launcher implementation. Repository fixtures contain only sanitized, application-relevant observations. The installation contains historical Content Manager and Custom Shaders Patch traces, so a controlled run is still required to prove the unmodified vanilla execution path.

## Observed compatibility target

| Item | Observation |
| --- | --- |
| Operating system | Windows build `26200.8894` |
| Steam application | Assetto Corsa app `244210`, build `14923034` |
| Vanilla launcher | `AssettoCorsa.exe` version `0.18.0115.5097` |
| Simulator | 64-bit `acs.exe`; 32-bit `acs_x86.exe` is also installed |
| Installation | Standard Steam library with all reference-series official content present |
| User data | `Assetto Corsa` below a OneDrive Documents directory rather than the stale local Documents candidate |

The initial compatibility claim must remain narrower than “all Windows and Steam installations” until the controlled launch, result capture, and another clean installation profile pass. Build identifiers are diagnostic evidence, not hard-coded acceptance gates.

## Decision

### Installation discovery

The adapter discovers Steam libraries rather than assuming `C:\Program Files (x86)\Steam`:

1. Read registered Steam installation roots from the current-user and 32/64-bit local-machine registry locations.
2. Parse each root's `steamapps/libraryfolders.vdf` as a versioned external format.
3. Find `steamapps/appmanifest_244210.acf`, require `appid` `244210`, and read its `installdir`.
4. Validate the candidate by requiring `AssettoCorsa.exe`, `acs.exe`, `content/cars`, and `content/tracks`.
5. Resolve the user's Documents known folder, then check explicitly supported redirected Documents candidates. If zero or multiple `Assetto Corsa` user-data roots remain, require user selection and remember it in the installation profile.

Registry, VDF, ACF, JSON, and INI values are parsed at their boundaries. Paths from them are normalized and checked to remain below the selected Steam library or user-data root before access.

### Reference content mapping

| Logical reference | Vanilla `race.ini` value | Capacity |
| --- | --- | --- |
| `mazda-mx5-cup` | `MODEL=ks_mazda_mx5_cup` | 17 observed skins |
| `magione/full` | `TRACK=magione`, empty `CONFIG_TRACK` | 18 pit boxes |
| `vallelunga/club` | `TRACK=ks_vallelunga`, `CONFIG_TRACK=club_circuit` | 24 pit boxes |
| `silverstone/national` | `TRACK=ks_silverstone`, `CONFIG_TRACK=national` | 24 pit boxes |
| `brands-hatch/indy` | `TRACK=ks_brands_hatch`, `CONFIG_TRACK=indy` | 24 pit boxes |

The adapter treats directory identifiers as external simulator identifiers. It verifies canonical metadata and model/data sentinel files before offering a mapping. It ignores unrelated files in content folders and does not hash an entire installation during normal validation. The build-specific observed sentinels live in [the installation fixture](../../tests/fixtures/assetto-corsa/vanilla/observed-installation.json).

### Launch-plan compilation

The version-1 compiler materializes one user-data file: `cfg/race.ini`. It leaves controls, video, audio, assists, gameplay, car data, track data, skins, and Steam files unchanged.

Required `race.ini` sections are:

- `HEADER` with format version `2` for a championship-style multi-session event;
- `RACE` with car, track, layout, entrant count, global AI level, penalties, and fixed-setup policy;
- `CAR_0` through `CAR_n`, where `CAR_0` is the player and AI entries carry model, skin, driver identity, skill, and aggression;
- ordered `SESSION_n` blocks using vanilla types `2` for qualifying and `3` for race, with `PIT` and `START` spawn sets respectively;
- deterministic lighting, weather, temperature, wind, groove, and dynamic-track values; and
- local-mode flags disabling remote, replay, ghost, and benchmark behavior for the staged attempt.

The vanilla launcher source writes the same concepts before calling its internal `ac://start` handler. The [Round 1 launch plan](../../tests/fixtures/assetto-corsa/vanilla/round-1-launch-plan.json) and [materialized INI](../../tests/fixtures/assetto-corsa/vanilla/round-1-race.ini) are the golden compiler fixtures.

### Safe staging

Before staging, Lights Out:

1. Acquires a single local simulator-launch lease.
2. Reads `cfg/race.ini` as bytes, records whether it existed, and stores its hash and backup in the attempt's application-owned directory.
3. Writes the complete generated INI to an application-owned temporary file.
4. Atomically replaces the user-data `cfg/race.ini` where the filesystem supports it and records a recovery marker before starting the simulator.
5. Keeps the staged file in place until the observed simulator process exits and result discovery completes.
6. Restores the exact prior bytes, or removes the file if none existed, and clears the recovery marker.

On startup, an uncleared marker blocks another launch. If `acs.exe` is still running, Lights Out waits or allows the user to detach without restoring. Otherwise it verifies the staged hash and restores the backup. If the current file differs from both staged and original hashes, recovery stops and asks the user rather than overwriting an external change.

OneDrive-backed user data introduces synchronization and atomic-replacement risk. The controlled test must verify replacement, simulator reads, result visibility, and restoration in the observed redirected directory. The adapter reports sync/conflict errors as recoverable staging failures.

### Process launch

The vanilla launcher performs this observed sequence:

1. writes/formats user `cfg/race.ini`;
2. invokes its private `ac://start` handler with car, track, skin, and time-limit query values;
3. monitors `acs.exe`; and
4. refreshes results after `acs.exe` stops.

The private handler's external contract is not published in the installed files. Lights Out will not automate the launcher's embedded browser or depend on `ac://start`.

A controlled attempt to start the installed 64-bit `acs.exe` directly, with the installation as its working directory and Steam already running, did **not** start the simulator. The requested process exited, Steam launched the library's default `AssettoCorsa.exe`, and the vanilla launcher initialized and rewrote `race.ini` from its saved UI state. No new result was produced. This matches Steamworks' relaunch behavior: an executable started without Steam application context can be relaunched through `steam://run/<AppId>`, which need not start the same executable.

The verified handoff is to give the child process the installed Steam runtime's `SteamAppId` and `SteamGameId` environment values (`244210`) before starting `acs.exe`. This does not write `steam_appid.txt` into the Steam-owned installation. After the redirected launcher processes were closed, the controlled retry started `acs.exe` directly, consumed the staged configuration, produced a new result after exit, and did not start the vanilla launcher or require Content Manager.

Process arguments are passed as typed argument-list entries without a shell. The process identifier, start time, executable identity, exit time, and exit code when available are recorded against the attempt. Process exit is not proof that a race completed.

### Result discovery and correlation

Vanilla writes fixed user-data outputs under `out/`:

- `race_out.json` — players, sessions, laps, classifications, and extras;
- `warnings.json` — CPU and frame-rate warnings; and
- `laps.ini` — a last-session lap summary.

The observed hotlap artifact confirms the top-level `track`, `number_of_sessions`, `players`, `sessions`, and `extras` fields. The installed vanilla result UI additionally consumes, per session, `name`, numeric `type`, `event`, `laps`, `bestLaps`, `raceResult`, and `lapstotal`; lap records identify a car index, lap number, time, and sectors.

`race_out.json` has no observed Lights Out correlation identifier and is overwritten. Before launch, Lights Out records its absence or hash, size, and modification time. After the process exits it waits for the file to become stable, requires a newly changed artifact, copies it immediately into application-owned immutable storage, hashes it, and then validates:

- the planned track and all expected car/skin identities;
- the expected session types and final race session;
- player indexes and classification indexes within bounds;
- lap totals, timing values, and array sizes within configured limits; and
- a completed race session rather than process exit or a practice-only result.

Any mismatch produces an unaccepted candidate for user review. Importing a preserved artifact remains the recovery path if automatic discovery fails. The raw artifact is retained before normalization.

The controlled smoke output confirmed the expected two-session shape and index-based `raceResult`. It also exposed a critical distinction: Assetto Corsa can emit a race classification even when every `lapstotal` is zero and `laps` is empty. Such an artifact is correlated with the launch but is not a completed race and must remain unaccepted. A non-empty `raceResult` alone is insufficient evidence of completion.

## Alternatives considered

### Write a vanilla `.champ` file and drive the vanilla launcher UI

Rejected for the first slice. It would duplicate season ownership, constrain rules to the launcher's championship model, and require UI automation. The installed `champs` directory is empty, while `race.ini` is the actual simulator boundary used by the launcher.

### Modify installation `cfg/race.ini`

Rejected. The simulator consumes the user-data copy, and installation files are Steam-owned templates. Lights Out only stages the user-data file.

### Use the dedicated server configuration

Rejected. `server_cfg.ini` and `entry_list.ini` describe multiplayer server sessions, not the local player race weekend.

### Depend on Content Manager command lines or extensions

Rejected for this compatibility target. Content Manager and Custom Shaders Patch traces may be present, but the generated contract contains no Content Manager-only keys and does not require either product.

## Consequences and risks

- The fixed output filename makes correlation probabilistic until validated against the launch plan and process window; raw preservation and user review are mandatory.
- Restoring `race.ini` after a crash requires durable hashes and conservative conflict handling.
- OneDrive redirection can change write and notification behavior.
- Vanilla numeric session types and INI keys are external compatibility values isolated in the adapter.
- Per-driver AI skill and aggression are present in the vanilla launcher implementation, but their effective behavior still needs the controlled race.
- The selected MX-5 grid fits every reference layout; future definitions must validate entrant count against `pitboxes`.
- A historical installation with third-party traces cannot alone establish a clean-vanilla compatibility claim.

## Verification

Completed by this spike:

- read-only Steam, executable, user-data, car, track, layout, skin, weather, launcher-source, configuration, log, and output inspection;
- exact logical-to-vanilla mapping for all reference-series content;
- sanitized observed installation and output fixtures;
- deterministic launch-plan and `race.ini` fixtures;
- fixture tests for entrant, session, content, and condition mappings; and
- a controlled direct-launch attempt proving that plain `acs.exe` invocation redirects to the vanilla launcher, plus hash-verified restoration after the launcher rewrote the staged file; and
- a successful `SteamAppId`/`SteamGameId=244210` child-process launch proving direct `acs.exe` execution, multi-session configuration loading, new result creation, byte-stable staging, and exact backup restoration; and
- repository harness and unit-test verification.

Still required before the adapter contract becomes Accepted:

- [ ] Back up and atomically stage the golden INI in the observed OneDrive user-data directory.
- [x] Safely terminate the test session and confirm process lifecycle behavior.
- [x] Capture and sanitize a real qualifying-plus-race `race_out.json`; the observed smoke artifact contains no completed laps and is retained as a rejection case.
- [ ] Capture a race with completed laps and verify result stability, classification semantics, and DNF representation. Zero-lap classification rejection and exact `race.ini` restoration are verified.
- [ ] Repeat content detection and launch on a clean vanilla installation profile.

The controlled local run uses the repository's `smoke-test-race.ini`: three MX-5 Cup entrants, one minute of qualifying, and a one-lap race at Magione. It is deliberately separate from the golden 12-car Round 1 launch plan.

## Rollout and rollback

Implement discovery and compilation before enabling launch. Ship the first adapter behind a compatibility label naming Windows, Steam Assetto Corsa, 64-bit `acs.exe`, and no Content Manager dependency. Keep staging disabled when discovery is ambiguous or recovery is unresolved.

Rollback disables the adapter and restores any outstanding backup using its recovery marker. Because no installation content or season domain data is changed by the adapter, rollback affects only staged user configuration and unaccepted launch attempts.
