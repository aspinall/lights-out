# Architecture

## System context

Describe the product, its users, external systems, trust boundaries, and deployment units here before application code is added. Link detailed design records instead of growing this file indefinitely.

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

## Boundary rules

- Validate untrusted data once at every external boundary.
- Convert transport and persistence shapes into domain types before applying business logic.
- Make time, randomness, network access, and storage replaceable at test boundaries.
- Emit structured events at important state transitions.
- Keep secrets out of source, logs, fixtures, and error messages.

## Architectural changes

Any change to deployment units, trust boundaries, public contracts, persistence ownership, or dependency direction requires a design record in `docs/design-docs/`. Add a structural test or lint when the rule can be checked mechanically.

