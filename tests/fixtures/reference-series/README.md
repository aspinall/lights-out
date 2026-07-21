# Reference series fixtures

The Lights Out MX-5 Sprint Cup is the golden championship for the first playable vertical slice. It is fictional and uses only official Assetto Corsa content.

## Championship card

- **Car:** Mazda MX-5 Cup
- **Grid:** one player and eleven AI drivers
- **Format:** 10-minute qualifying followed by one sprint race
- **Points:** 25–18–15–12–10–8–6–4–2–1 for classified finishers
- **Bonuses:** none
- **Dropped scores:** none
- **Tie-breakers:** finishing-position countback, then the better result in the most recent race

| Round | Event | Circuit | Race distance |
| --- | --- | --- | --- |
| 1 | Umbrian Opener | Magione, Full Circuit | 12 laps |
| 2 | Vallelunga Club Trophy | Vallelunga, Club Circuit | 14 laps |
| 3 | Silverstone Sprint | Silverstone, National Circuit | 12 laps |
| 4 | Brands Hatch Finale | Brands Hatch, Indy Circuit | 15 laps |

All sessions use clear daytime conditions. There are no pit-stop requirements, success ballast, reverse grids, bonus points, or manual penalties in this reference series.

## Fixture files

Files:

- `lights-out-mx5-sprint-cup.series.json` is the draft version-1 series definition that will drive the published schema.
- `lights-out-mx5-sprint-cup.results.json` contains normalized accepted race results for all four rounds.
- `lights-out-mx5-sprint-cup.expected-standings.json` is the expected deterministic championship projection.

The definition uses logical content references, not Assetto Corsa directory names. The simulator adapter must map these references to the user's installed content and record that mapping before a season becomes playable.

The fixture deliberately covers:

- one player and eleven AI entrants in the same official car;
- four official circuits and their layouts;
- qualifying-to-race grid formation;
- points awarded to the top ten classified finishers;
- two non-classified finishers;
- zero-point classified finishers; and
- a final points tie that remains tied through finishing-position countback and is resolved by the better result in the most recent race.

These files are product-driving examples, not a finalized interchange contract. Change them together with the versioned schema, domain rules, tests, product specification, and active execution-plan decision log.
