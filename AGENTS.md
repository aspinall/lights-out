# Agent instructions

This file is the repository map. Read only the documents relevant to the task; the linked files are the sources of truth.

## Start here

1. Read `harness/project.json` for the project summary and canonical commands.
2. Read `ARCHITECTURE.md` before changing structure, dependencies, or boundaries.
3. Find product intent in `docs/product-specs/index.md`.
4. Find prior decisions in `docs/design-docs/index.md`.
5. For substantial work, create or update a plan under `docs/exec-plans/active/`.

## Working agreement

- Inspect before editing; preserve unrelated user changes.
- Treat repository-local, versioned artifacts as the system of record.
- Keep changes narrow, reversible, and covered by proportionate verification.
- Parse and validate data at system boundaries. Do not build behavior on guessed shapes.
- Respect the dependency rules in `ARCHITECTURE.md`.
- Use the canonical commands from `harness/project.json`; do not invent alternate workflows without documenting them.
- Update the relevant spec, design record, plan, or runbook when behavior or a decision changes.
- Turn recurring review feedback into documentation, a lint, a test, or an evaluation.
- Do not weaken checks merely to make a change pass.
- Never commit secrets, credentials, generated caches, or local environment files.

## Definition of done

- Acceptance criteria are demonstrably satisfied.
- Focused tests pass, then the repository verification command passes.
- User-visible behavior is exercised at the highest practical level.
- Logs and errors are actionable and contain no sensitive data.
- Documentation and the active execution plan reflect the final state.
- New architectural or taste invariants are mechanically enforced where practical.

## Knowledge map

- Product principles: `docs/PRODUCT.md`
- Design principles: `docs/DESIGN.md`
- Quality grading: `docs/QUALITY.md`
- Reliability: `docs/RELIABILITY.md`
- Security: `docs/SECURITY.md`
- Golden engineering principles: `docs/GOLDEN_PRINCIPLES.md`
- Planning process: `docs/exec-plans/README.md`
- Known debt: `docs/exec-plans/tech-debt.md`

