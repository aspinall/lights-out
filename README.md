# Agent-first engineering harness

This repository is a stack-neutral template for building software with coding agents. It turns product intent, architectural boundaries, quality expectations, and execution history into versioned artifacts that an agent can discover and verify.

It follows the operating model described in OpenAI's [Harness engineering](https://openai.com/index/harness-engineering/): humans steer, agents execute, and failures improve the harness rather than becoming one-off prompting folklore.

## Start a project

1. Create a repository from this template.
2. Replace the project summary and commands in `harness/project.json`.
3. Write the first product spec in `docs/product-specs/`.
4. Record consequential design decisions in `docs/design-docs/`.
5. For multi-step work, copy `docs/exec-plans/PLAN_TEMPLATE.md` into `docs/exec-plans/active/`.
6. Teach `tools/harness_check.py` any architecture or quality rule that matters repeatedly.
7. Run `python tools/harness_check.py` before opening a pull request.

## Repository map

| Path | Purpose |
| --- | --- |
| `AGENTS.md` | Short entry point for agents; a map, not a manual |
| `ARCHITECTURE.md` | Top-level system shape and dependency rules |
| `docs/` | Versioned product, design, quality, and operational knowledge |
| `docs/exec-plans/` | Active and completed plans with decisions and progress |
| `harness/project.json` | Machine-readable project metadata and canonical commands |
| `tools/harness_check.py` | Fast, dependency-free harness validation |
| `.github/` | CI and pull-request feedback loops |

## Feedback loop

```text
intent -> plan -> implement -> verify -> review -> capture learning
   ^                                                  |
   +--------------------------------------------------+
```

When an agent fails, prefer a durable repair: expose missing context, add a command, encode an invariant, improve an error message, or add an evaluation. Keep `AGENTS.md` small and link to the source of truth.

## What this template deliberately omits

There is no application framework, deployment target, or package manager. Those choices should be explicit design decisions for the product. The harness checker uses only the Python standard library and runs on Windows, macOS, and Linux.

