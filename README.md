# agentic-flows

Reusable workflow definitions for RNT56 agentic projects.

`agentic-flows` is a contract and catalog repo for high-level agentic process design. ThinClaw, NilCore, and CrustCore are separate projects; this repo defines workflow specs they may choose to consume later through adapters, vendoring, or copied templates.

Useful optional-consumer framing:

- **ThinClaw** can consume flows as durable routines and operator-facing decisions.
- **NilCore** can consume flows as worker/supervisor execution plans.
- **CrustCore** can consume flows as verifier and proof contracts.

This repository does not replace or merge those projects. It gives them a neutral, versioned workflow format, examples, validation, and adapter contracts when they are ready to opt in.

## What is in this repo

```text
flows/          Versioned reusable workflow definitions.
templates/      Copyable starter flows for new projects.
schemas/        JSON Schema contracts for flows, nodes, and events.
tools/flowctl/  CLI for validation, listing, and graph export.
integrations/   ThinClaw, NilCore, CrustCore, and shared adapter contracts.
examples/       Minimal consumption examples and runbooks.
docs/           Architecture, spec, roadmap, and integration guidance.
tests/          CLI and schema regression tests.
```

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e . pytest

flowctl validate
flowctl validate-event examples/standalone/event.sample.json
flowctl validate-run examples/runs/
flowctl replay examples/runs/feature-implementation.run.json
flowctl validate-samples
flowctl report
flowctl list
flowctl graph flows/coding/feature-implementation/flow.yaml --format dot
pytest
```

The default validation command checks every `flow.yaml` under `flows/` and `templates/`.

## Current repo stack

- Flow definitions: YAML with a JSON Schema contract.
- Validation and export: Python CLI (`flowctl`).
- CI: GitHub Actions validates schemas, flows, graph export, and tests.
- Runtime adapters: optional contract-first documentation until an independent consumer project implements a loader.

## First-class flows

- `coding/feature-implementation`
- `coding/refactor-and-verify`
- `coding/security-audit`
- `research/deep-research-report`
- `collaboration/multi-agent-supervisor`
- `general/human-in-the-loop-review`

## Definition of ready

A workflow is ready to use when:

1. `flowctl validate` passes.
2. The flow declares intended optional consumers and required capabilities.
3. Every edge references an existing node.
4. Every node is reachable from the entrypoint.
5. At least one required quality gate is present.
6. Required quality gates name declared artifact or event evidence refs.
7. The flow README includes a maturity rubric.
8. A consuming project records events compatible with `schemas/event.schema.json`.

See [docs/project-plan.md](docs/project-plan.md) for the upgraded plan and [docs/core-integration.md](docs/core-integration.md) for runtime expectations.

## Documentation

Start with [docs/README.md](docs/README.md). The docs folder contains the full roadmap, goals, task backlog, workflow authoring guidance, testing strategy, release process, changelog management, governance, and adapter implementation plan.

## Changelog

Release and compatibility notes live in [CHANGELOG.md](CHANGELOG.md). Keep `Unreleased` current for schema, flow, command, adapter-contract, and process changes.
