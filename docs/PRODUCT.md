# Product

## Users and outcome

Lights Out is for sim-racing fans who want to experience a coherent championship rather than configure isolated races by hand. A user supplies a race-series definition and the required Assetto Corsa content; Lights Out validates the combination, prepares each event, launches it in Assetto Corsa, records the result, and carries championship state into the next round.

The primary outcome is a complete, resumable season whose calendar, entrants, sessions, rules, results, and standings remain understandable outside the simulator.

## Core beliefs

- Assetto Corsa is the driving simulator; Lights Out is the championship authority.
- A series definition should describe racing concepts, not simulator file-layout details.
- Never start an event that cannot be reproduced or whose prerequisites are known to be missing.
- Preserve the user's installed content and season history; stage reversible integration changes.
- Optimize for a complete user outcome, not feature count.
- State acceptance criteria in behavior users can observe.
- Prefer the smallest coherent change that tests the riskiest assumption.
- Treat accessibility, privacy, performance, and failure recovery as product behavior.

## Non-goals

- Replacing Assetto Corsa's physics, AI, rendering, or in-session user interface.
- Downloading, redistributing, licensing, or automatically updating mods and DLC.
- Guaranteeing every real-world sporting regulation in the first release.
- Multiplayer championship administration, live race control, or league hosting in the first release.
- Supporting simulators other than the original Assetto Corsa in the first release.

## Success measures

Initial measures are local and privacy-preserving unless the user explicitly opts into diagnostics.

| Measure | Owner | Data source | Decision informed |
| --- | --- | --- | --- |
| Series imports reaching a playable first event | Product | Local structured lifecycle events | Whether definition and content validation are understandable |
| Launched events producing an accepted result | Product | Local event and result records | Whether the Assetto Corsa integration is reliable |
| Seasons resumed without repair | Engineering | Local recovery events | Whether persistence and staging are robust |
| Validation failures resolved on the next attempt | Product | Local validation summaries | Whether recovery guidance is actionable |

